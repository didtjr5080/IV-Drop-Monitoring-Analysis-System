package com.example.ivmonitor.bluetooth

import android.Manifest
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothSocket
import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import androidx.core.content.ContextCompat
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ensureActive
import kotlinx.coroutines.isActive
import kotlinx.coroutines.withContext
import java.io.BufferedReader
import java.io.InputStreamReader
import java.util.UUID
import kotlin.coroutines.coroutineContext

class BluetoothClient(
    private val context: Context,
    private val ioDispatcher: CoroutineDispatcher = Dispatchers.IO
) {

    private val bluetoothAdapter: BluetoothAdapter? = BluetoothAdapter.getDefaultAdapter()
    private var socket: BluetoothSocket? = null
    private var reader: BufferedReader? = null

    companion object {
        val SPP_UUID: UUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB")
    }

    fun isBluetoothSupported(): Boolean = bluetoothAdapter != null

    fun isBluetoothEnabled(): Boolean = bluetoothAdapter?.isEnabled == true

    private fun hasBluetoothConnectPermission(): Boolean {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            ContextCompat.checkSelfPermission(
                context,
                Manifest.permission.BLUETOOTH_CONNECT
            ) == PackageManager.PERMISSION_GRANTED
        } else {
            true
        }
    }

    @Throws(SecurityException::class, IllegalStateException::class)
    fun getPairedDevices(): List<BluetoothDevice> {
        if (!hasBluetoothConnectPermission()) {
            throw SecurityException("BLUETOOTH_CONNECT 권한이 없습니다.")
        }
        val adapter = bluetoothAdapter ?: throw IllegalStateException("Bluetooth 미지원 기기")
        return adapter.bondedDevices?.toList().orEmpty()
    }

    suspend fun connectByDeviceAddress(deviceAddress: String) = withContext(ioDispatcher) {
        if (!hasBluetoothConnectPermission()) {
            throw SecurityException("BLUETOOTH_CONNECT 권한이 없습니다.")
        }

        val adapter = bluetoothAdapter ?: throw IllegalStateException("Bluetooth 미지원 기기")
        if (!adapter.isEnabled) throw IllegalStateException("Bluetooth가 꺼져 있습니다.")

        val device = adapter.getRemoteDevice(deviceAddress)
        adapter.cancelDiscovery()

        close()

        val newSocket = device.createRfcommSocketToServiceRecord(SPP_UUID)
        newSocket.connect()

        socket = newSocket
        reader = BufferedReader(InputStreamReader(newSocket.inputStream))
    }

    suspend fun readLines(onLineReceived: suspend (String) -> Unit) = withContext(ioDispatcher) {
        val localReader = reader ?: throw IllegalStateException("Bluetooth reader가 초기화되지 않았습니다.")

        while (coroutineContext.isActive) {
            coroutineContext.ensureActive()
            val line = localReader.readLine() ?: break
            if (line.isNotBlank()) {
                onLineReceived(line)
            }
        }
    }

    fun isConnected(): Boolean = socket?.isConnected == true

    fun close() {
        try {
            reader?.close()
        } catch (_: Exception) {
        } finally {
            reader = null
        }

        try {
            socket?.close()
        } catch (_: Exception) {
        } finally {
            socket = null
        }
    }
}
