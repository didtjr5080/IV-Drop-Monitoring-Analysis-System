package com.example.ivmonitor.ui

import android.Manifest
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.util.Log
import android.view.View
import android.view.ViewGroup
import android.widget.AdapterView
import android.widget.ArrayAdapter
import android.widget.TextView
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import com.example.ivmonitor.R
import com.example.ivmonitor.databinding.FragmentPatientConnectionBinding
import com.example.ivmonitor.model.Patient
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.LiveData


class PatientConnectionFragment : Fragment(R.layout.fragment_patient_connection) {

    private var _binding: FragmentPatientConnectionBinding? = null
    private val binding get() = _binding!!
    private val viewModel: MainViewModel by activityViewModels()
    private val _testMode = MutableLiveData(false)
    val testMode: LiveData<Boolean> = _testMode
    private val permissionLauncher =
        registerForActivityResult(ActivityResultContracts.RequestMultiplePermissions()) { result ->
            val allGranted = result.values.all { it }
            if (allGranted) {
                viewModel.connectBluetooth()
            }
        }



    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentPatientConnectionBinding.bind(view)

        // 📌 Drawer 버튼
        binding.btnOpenDrawer.setOnClickListener {
            (activity as? MainActivity)?.openDrawer()
        }

        // 📌 연결 버튼 (실제 / 테스트 / 해제 선택)
        binding.btnConnect.setOnClickListener {
            val options = arrayOf("실제 HC-05 연결", "테스트 연결(가상)", "테스트 연결 해제")

            com.google.android.material.dialog.MaterialAlertDialogBuilder(requireContext())
                .setTitle("연결 방식 선택")
                .setItems(options) { _, which ->
                    when (which) {
                        0 -> {
                            if (hasRequiredBluetoothPermissions()) {
                                viewModel.connectBluetooth()
                            } else {
                                requestBluetoothPermissions()
                            }
                        }
                        1 -> {
                            viewModel.enableTestMode()
                        }
                        2 -> {
                            viewModel.disableTestMode()
                        }
                    }
                }
                .show()
        }

        // 📌 Bluetooth 상태 텍스트
        viewModel.bluetoothInfo.observe(viewLifecycleOwner) {
            binding.tvBluetoothInfo.text = it
        }

        // 📌 환자 목록 → Spinner
        viewModel.patients.observe(viewLifecycleOwner) { patients ->
            android.util.Log.d("PATIENT_DEBUG", "patients size=${patients.size}")
            setupSpinner(patients)
        }

        // 📌 선택된 환자 표시
        viewModel.selectedPatient.observe(viewLifecycleOwner) { patient ->
            binding.tvSelectedPatient.text = if (patient != null) {
                "선택: ${patient.name} / ID: ${patient.id} / 병상: ${patient.bedNumber}"
            } else {
                "선택된 환자 없음"
            }
        }

        // 📌 연결 상태 (Bluetooth + TestMode 통합)
        viewModel.connectionState.observe(viewLifecycleOwner) { connected ->
            val isTestMode = viewModel.testMode.value == true
            binding.btnConnect.text = when {
                isTestMode -> "테스트 연결됨"
                connected -> "HC-05 연결됨"
                else -> "연결 선택"
            }
        }

        // 📌 TestMode 상태 변화 시 버튼 업데이트
        viewModel.testMode.observe(viewLifecycleOwner) { isTestMode ->
            val connected = viewModel.connectionState.value == true
            binding.btnConnect.text = when {
                isTestMode -> "테스트 연결됨"
                connected -> "HC-05 연결됨"
                else -> "연결 선택"
            }
        }

        // 📌 초기 환자 로드
        if (viewModel.patients.value.isNullOrEmpty()) {
            viewModel.startPatientsListener()
        }
    }

    private fun setupSpinner(items: List<Patient>) {
        Log.d("PATIENT_DEBUG", "setupSpinner size=${items.size}, items=$items")

        val displayItems = if (items.isEmpty()) {
            listOf(Patient(
                id = "",
                name = "환자 없음",
                bedNumber = "",
                createdAt = 0L
            ))
        } else {
            items
        }

        val adapter = object : ArrayAdapter<Patient>(
            requireContext(),
            android.R.layout.simple_spinner_item,
            displayItems
        ) {
            override fun getView(
                position: Int,
                convertView: View?,
                parent: ViewGroup
            ): View {
                val view = super.getView(position, convertView, parent)
                (view as? TextView)?.apply {
                    text = displayItems[position].name
                    setTextColor(ContextCompat.getColor(requireContext(), R.color.text_primary))
                }
                return view
            }

            override fun getDropDownView(
                position: Int,
                convertView: View?,
                parent: ViewGroup
            ): View {
                val view = super.getDropDownView(position, convertView, parent)
                (view as? TextView)?.apply {
                    text = "${displayItems[position].name} / ${displayItems[position].bedNumber}"
                    setTextColor(ContextCompat.getColor(requireContext(), R.color.text_primary))
                    setBackgroundColor(ContextCompat.getColor(requireContext(), R.color.bg_surface))
                }
                return view
            }
        }

        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        binding.spinnerPatients.adapter = adapter

        binding.spinnerPatients.isEnabled = items.isNotEmpty()

        binding.spinnerPatients.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(
                parent: AdapterView<*>?,
                view: View?,
                position: Int,
                id: Long
            ) {
                if (items.isEmpty()) {
                    viewModel.selectPatient(null)
                    return
                }

                val patient = items.getOrNull(position)
                Log.d("PATIENT_DEBUG", "selected patient=$patient")
                viewModel.selectPatient(patient)
            }

            override fun onNothingSelected(parent: AdapterView<*>?) {
                Log.d("PATIENT_DEBUG", "onNothingSelected")
                viewModel.selectPatient(null)
            }
        }
    }

    private fun hasRequiredBluetoothPermissions(): Boolean {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            val connectGranted = ContextCompat.checkSelfPermission(
                requireContext(),
                Manifest.permission.BLUETOOTH_CONNECT
            ) == PackageManager.PERMISSION_GRANTED

            val scanGranted = ContextCompat.checkSelfPermission(
                requireContext(),
                Manifest.permission.BLUETOOTH_SCAN
            ) == PackageManager.PERMISSION_GRANTED

            connectGranted && scanGranted
        } else {
            true
        }
    }

    private fun requestBluetoothPermissions() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            permissionLauncher.launch(
                arrayOf(
                    Manifest.permission.BLUETOOTH_CONNECT,
                    Manifest.permission.BLUETOOTH_SCAN
                )
            )
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}