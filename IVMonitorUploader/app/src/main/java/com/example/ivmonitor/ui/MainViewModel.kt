package com.example.ivmonitor.ui
import com.google.firebase.firestore.ListenerRegistration
import android.app.Application
import android.bluetooth.BluetoothDevice
import android.os.Build
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import com.example.ivmonitor.bluetooth.BluetoothClient
import com.example.ivmonitor.data.FirestoreRepository
import com.example.ivmonitor.model.DropLog
import com.example.ivmonitor.model.Patient
import com.example.ivmonitor.model.SessionSummary
import com.example.ivmonitor.util.DropLogParser
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.UUID


class MainViewModel(application: Application) : AndroidViewModel(application) {

    private val repository = FirestoreRepository()
    private val bluetoothClient = BluetoothClient(application.applicationContext)

    private val _patients = MutableLiveData<List<Patient>>(emptyList())
    val patients: LiveData<List<Patient>> = _patients

    private val _selectedPatient = MutableLiveData<Patient?>(null)
    val selectedPatient: LiveData<Patient?> = _selectedPatient

    private val _connectionState = MutableLiveData(false)
    val connectionState: LiveData<Boolean> = _connectionState

    private val _bluetoothInfo = MutableLiveData("HC-05 페어링 기기와 연결")
    val bluetoothInfo: LiveData<String> = _bluetoothInfo

    private val _sessionInfo = MutableLiveData("선택 환자 기준 업로드 세션 생성")
    val sessionInfo: LiveData<String> = _sessionInfo

    private val _statusLog = MutableLiveData("대기 중")
    val statusLog: LiveData<String> = _statusLog

    private val _sessionActive = MutableLiveData(false)
    val sessionActive: LiveData<Boolean> = _sessionActive

    private var selectedBluetoothDevice: BluetoothDevice? = null
    private var currentSessionId: String? = null
    private var currentSessionStartTime: Long? = null
    private val receivedLogs = mutableListOf<DropLog>()
    private var lastSavedLogId: String? = null
    private var readJob: Job? = null

    private val _sessionStarting = MutableLiveData(false)
    val sessionStarting: LiveData<Boolean> = _sessionStarting

    private val timeFormatter = SimpleDateFormat("HH:mm:ss", Locale.getDefault())
    private val _testMode = MutableLiveData(false)
    val canStart = (_testMode.value == true) || bluetoothClient.isConnected()
    private var patientsListener: ListenerRegistration? = null
//    private val _testMode = MutableLiveData(false)
    val testMode: LiveData<Boolean> = _testMode


    fun enableTestMode() {
        _testMode.value = true
        _connectionState.value = true
        _bluetoothInfo.value = "테스트 연결됨: 가상 입력 모드"
        appendStatus("테스트 모드 활성화")
    }

    fun disableTestMode() {
        _testMode.value = false
        _connectionState.value = bluetoothClient.isConnected()
        _bluetoothInfo.value = if (bluetoothClient.isConnected()) {
            "Bluetooth 연결 유지 중"
        } else {
            "HC-05 페어링 기기와 연결"
        }
        appendStatus("테스트 모드 비활성화")
    }

    fun loadPatients() {
        viewModelScope.launch {
            try {
                appendStatus("환자 목록 불러오는 중...")
                val items = repository.getPatients()

                android.util.Log.d("PATIENT_DEBUG", "loadPatients size=${items.size}")
                android.util.Log.d("PATIENT_DEBUG", "loadPatients items=$items")

                _patients.value = items

                if (items.isEmpty()) {
                    appendStatus("환자 목록이 비어 있습니다.")
                    return@launch
                }

                selectPatient(items.first())
                appendStatus("환자 목록 로드 완료 (${items.size}명)")
            } catch (e: Exception) {
                android.util.Log.e("PATIENT_DEBUG", "loadPatients failed", e)
                appendStatus("환자 목록 로드 실패: ${e.message}")
            }
        }
    }
    fun selectPatient(patient: Patient?) {
        _selectedPatient.value = patient

        _sessionInfo.value = if (patient != null) {
            "선택 환자: ${patient.name} / ID: ${patient.id} / 병상: ${patient.bedNumber}"
        } else {
            "선택 환자 없음"
        }
    }
    fun startPatientsListener() {

        patientsListener?.remove()

        appendStatus("환자 실시간 동기화 시작")

        patientsListener = repository.observePatients(

            onUpdate = { list ->

                android.util.Log.d("PATIENT_DEBUG", "update size=${list.size}")

                _patients.postValue(list)

                val current = _selectedPatient.value

                if (list.isEmpty()) {
                    _selectedPatient.postValue(null)
                    return@observePatients
                }

                if (current == null) {
                    selectPatient(list.first())
                    return@observePatients
                }

                val exists = list.any { it.id == current.id }

                if (!exists) {

                    appendStatus("선택 환자 삭제됨 → 자동 변경")

                    if (_sessionActive.value == true) {

                        appendStatus("세션 초기화")

                        currentSessionId = null
                        currentSessionStartTime = null
                        receivedLogs.clear()
                        lastSavedLogId = null
                        _sessionActive.postValue(false)
                    }

                    selectPatient(list.first())
                }
            },

            onError = {
                appendStatus("환자 동기화 실패: ${it.message}")
            }
        )
    }

    fun connectBluetooth() {
        viewModelScope.launch {
            try {
                if (!bluetoothClient.isBluetoothSupported()) {
                    appendStatus("이 기기는 Bluetooth를 지원하지 않습니다.")
                    _connectionState.value = false
                    return@launch
                }

                if (!bluetoothClient.isBluetoothEnabled()) {
                    appendStatus("Bluetooth가 꺼져 있습니다.")
                    _connectionState.value = false
                    return@launch
                }

                appendStatus("페어링 기기 검색 중...")
                val pairedDevices = bluetoothClient.getPairedDevices()
                val hc05 = pairedDevices.firstOrNull {
                    val name = it.name ?: ""
                    name.contains("HC-05", ignoreCase = true)
                }

                if (hc05 == null) {
                    appendStatus("페어링된 HC-05를 찾지 못했습니다.")
                    _connectionState.value = false
                    return@launch
                }

                selectedBluetoothDevice = hc05
                _bluetoothInfo.value = "연결 대상: ${hc05.name} / ${hc05.address}"
                appendStatus("HC-05 연결 시도: ${hc05.name} (${hc05.address})")

                bluetoothClient.connectByDeviceAddress(hc05.address)

                _connectionState.value = true
                _bluetoothInfo.value = "연결됨: ${hc05.name} / ${hc05.address}"
                appendStatus("HC-05 연결 완료")

                startReadingLoop()
            } catch (e: SecurityException) {
                _connectionState.value = false
                appendStatus("권한 오류: ${e.message}")
            } catch (e: Exception) {
                _connectionState.value = false
                appendStatus("Bluetooth 연결 실패: ${e.message}")
            }
        }
    }

    fun startSession() {
        val patient = _selectedPatient.value
        if (patient == null) {
            android.util.Log.e("SESSION_DEBUG", "patient is null")
            appendStatus("세션 시작 실패: 환자 미선택")
            return
        }

        if (_sessionActive.value == true) {
            android.util.Log.w("SESSION_DEBUG", "startSession blocked: already active")
            appendStatus("이미 활성 세션이 있습니다.")
            return
        }

        if (_sessionStarting.value == true) {
            android.util.Log.w("SESSION_DEBUG", "startSession blocked: session already starting")
            appendStatus("세션 생성 진행 중입니다.")
            return
        }

        if (currentSessionId != null) {
            android.util.Log.w("SESSION_DEBUG", "startSession blocked: currentSessionId already exists = $currentSessionId")
            appendStatus("이미 생성된 세션이 존재합니다.")
            return
        }

        val canStart = (_testMode.value == true) || bluetoothClient.isConnected()
        if (!canStart) {
            android.util.Log.e(
                "SESSION_DEBUG",
                "canStart=false, testMode=${_testMode.value}, bt=${bluetoothClient.isConnected()}"
            )
            appendStatus("세션 시작 실패: Bluetooth 또는 테스트 연결 필요")
            return
        }

        _sessionStarting.value = true

        viewModelScope.launch {
            try {
                val sessionId = UUID.randomUUID().toString()
                val startTime = System.currentTimeMillis()

                android.util.Log.d(
                    "SESSION_DEBUG",
                    "creating session patient=${patient.id}, sessionId=$sessionId"
                )

                val summary = SessionSummary(
                    sessionId = sessionId,
                    startTime = startTime,
                    endTime = null,
                    totalDrops = 0,
                    avgRate = 0.0,
                    warningCount = 0,
                    alertCount = 0
                )

                repository.createSession(patient.id, summary)

                currentSessionId = sessionId
                currentSessionStartTime = startTime
                receivedLogs.clear()
                lastSavedLogId = null

                _sessionActive.value = true
                _sessionInfo.value =
                    "세션 활성화 / 환자: ${patient.name} / 세션ID: ${sessionId.take(8)}..."
                appendStatus("세션 시작 완료: $sessionId")

                android.util.Log.d("SESSION_DEBUG", "session created and activated: $sessionId")
            } catch (e: Exception) {
                android.util.Log.e("SESSION_DEBUG", "startSession failed", e)
                appendStatus("세션 시작 실패: ${e.message}")
            } finally {
                _sessionStarting.postValue(false)
            }
        }
    }

    fun uploadManualLog(
        dropCount: Int,
        ratePerMin: Double,
        status: String,
        lastDropSec: Double
    ) {
        val patient = _selectedPatient.value
        if (patient == null) {
            android.util.Log.e("UPLOAD_DEBUG", "patient is null")
            appendStatus("수동 업로드 실패: 환자 미선택")
            return
        }

        val sessionId = currentSessionId
        if (sessionId == null) {
            android.util.Log.e("UPLOAD_DEBUG", "sessionId is null")
            appendStatus("수동 업로드 실패: 세션 미시작")
            return
        }

        android.util.Log.d(
            "UPLOAD_DEBUG",
            "uploadManualLog start patient=${patient.id}, sessionId=$sessionId, dropCount=$dropCount, ratePerMin=$ratePerMin, status=$status, lastDropSec=$lastDropSec"
        )

        viewModelScope.launch {
            try {
                val log = DropLog(
                    timestamp = System.currentTimeMillis(),
                    dropCount = dropCount,
                    ratePerMin = ratePerMin,
                    status = status,
                    lastDropSec = lastDropSec
                )

                android.util.Log.d("UPLOAD_DEBUG", "before saveLog")

                repository.saveLog(patient.id, sessionId, log)

                android.util.Log.d("UPLOAD_DEBUG", "after saveLog success")

                receivedLogs.add(log)
                lastSavedLogId = log.stableLogId()

                appendStatus(
                    "테스트 로그 업로드 완료\n" +
                            "- patient=${patient.id}\n" +
                            "- dropCount=$dropCount\n" +
                            "- ratePerMin=$ratePerMin\n" +
                            "- status=$status\n" +
                            "- lastDropSec=$lastDropSec"
                )
            } catch (e: Exception) {
                android.util.Log.e("UPLOAD_DEBUG", "saveLog failed", e)
                appendStatus("수동 업로드 실패: ${e.message}")
            }
        }
    }

    fun endSession() {
        val patient = _selectedPatient.value ?: run {
            appendStatus("세션 종료 실패: 환자 미선택")
            return
        }

        val sessionId = currentSessionId ?: run {
            appendStatus("세션 종료 실패: 활성 세션 없음")
            return
        }

        val startTime = currentSessionStartTime ?: System.currentTimeMillis()

        viewModelScope.launch {
            try {
                val totalDrops = receivedLogs.maxOfOrNull { it.dropCount } ?: 0
                val avgRate = if (receivedLogs.isNotEmpty()) {
                    receivedLogs.map { it.ratePerMin }.average()
                } else 0.0

                val warningCount = receivedLogs.count { it.status.equals("WARNING", ignoreCase = true) }
                val alertCount = receivedLogs.count { it.status.equals("ALERT", ignoreCase = true) }

                val summary = SessionSummary(
                    sessionId = sessionId,
                    startTime = startTime,
                    endTime = System.currentTimeMillis(),
                    totalDrops = totalDrops,
                    avgRate = avgRate,
                    warningCount = warningCount,
                    alertCount = alertCount
                )

                repository.updateSessionSummary(patient.id, summary)

                appendStatus(
                    "세션 종료 완료\n" +
                            "- totalDrops: $totalDrops\n" +
                            "- avgRate: ${"%.2f".format(avgRate)}\n" +
                            "- warning: $warningCount\n" +
                            "- alert: $alertCount"
                )

                currentSessionId = null
                currentSessionStartTime = null
                receivedLogs.clear()
                lastSavedLogId = null

                _sessionActive.value = false
                _sessionInfo.value = "선택 환자: ${patient.name} / ID: ${patient.id} / 병상: ${patient.bedNumber}"
            } catch (e: Exception) {
                appendStatus("세션 종료 실패: ${e.message}")
            }
        }
        _sessionStarting.value = false
    }

    private fun startReadingLoop() {
        readJob?.cancel()
        readJob = viewModelScope.launch {
            try {
                bluetoothClient.readLines { line ->
                    handleIncomingLine(line)
                }
                appendStatus("Bluetooth 수신 루프 종료")
                _connectionState.postValue(false)
            } catch (e: Exception) {
                appendStatus("수신 중 오류: ${e.message}")
                _connectionState.postValue(false)
            }
        }
    }

    private suspend fun handleIncomingLine(raw: String) {
        val parseResult = DropLogParser.parse(raw)

        parseResult
            .onSuccess { log ->
                appendStatus(
                    "[수신 성공] ${formatTimestamp(log.timestamp)}\n" +
                            "dropCount=${log.dropCount}, rate=${log.ratePerMin}, " +
                            "status=${log.status}, lastDropSec=${log.lastDropSec}"
                )

                val sessionId = currentSessionId
                val patient = _selectedPatient.value

                if (sessionId == null || patient == null) {
                    appendStatus("세션 비활성 상태이므로 업로드 생략")
                    return
                }

                val logId = log.stableLogId()
                if (lastSavedLogId == logId) {
                    appendStatus("중복 로그 감지 -> 저장 생략: $logId")
                    return
                }

                try {
                    repository.saveLog(patient.id, sessionId, log)
                    receivedLogs.add(log)
                    lastSavedLogId = logId
                    appendStatus("Firebase 저장 완료: ${patient.id} / ${sessionId.take(8)} / $logId")
                } catch (e: Exception) {
                    appendStatus("Firebase 저장 실패: ${e.message}")
                }
            }
            .onFailure { error ->
                appendStatus("파싱 실패: ${error.message}\n원본: $raw")
            }
    }

    private fun appendStatus(message: String) {
        val now = timeFormatter.format(Date())
        val entry = "[$now] $message"
        val current = _statusLog.value.orEmpty()

        _statusLog.postValue(
            if (current.isBlank() || current == "대기 중") {
                entry
            } else {
                "$entry\n\n$current".take(3500)
            }
        )
    }

    private fun formatTimestamp(timestamp: Long): String {
        return try {
            timeFormatter.format(Date(timestamp))
        } catch (_: Exception) {
            timestamp.toString()
        }
    }

    override fun onCleared() {
        super.onCleared()
        patientsListener?.remove()
        bluetoothClient.close()
    }
}