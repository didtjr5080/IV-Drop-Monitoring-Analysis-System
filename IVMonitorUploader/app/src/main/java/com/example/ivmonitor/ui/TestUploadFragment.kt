package com.example.ivmonitor.ui

import android.os.Bundle
import android.view.View
import android.widget.ArrayAdapter
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import com.example.ivmonitor.R
import com.example.ivmonitor.databinding.FragmentTestUploadBinding

class TestUploadFragment : Fragment(R.layout.fragment_test_upload) {

    private var _binding: FragmentTestUploadBinding? = null
    private val binding get() = _binding!!
    private val viewModel: MainViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentTestUploadBinding.bind(view)

        setupStatusSpinner()
        setupSliders()
        setupButtons()

        viewModel.testMode.observe(viewLifecycleOwner) {
            updateUploadUi()
        }

        viewModel.sessionActive.observe(viewLifecycleOwner) {
            updateUploadUi()
        }

        updateUploadUi()
    }

    private fun updateUploadUi() {
        val isTestMode = viewModel.testMode.value == true
        val isSessionActive = viewModel.sessionActive.value == true
        val canUpload = isTestMode && isSessionActive

        android.util.Log.d(
            "UI_DEBUG",
            "testMode=$isTestMode, sessionActive=$isSessionActive, canUpload=$canUpload"
        )

        binding.layoutUploadForm.visibility =
            if (canUpload) View.VISIBLE else View.GONE

        binding.tvTestModeNotice.visibility =
            if (canUpload) View.GONE else View.VISIBLE

        binding.tvTestModeNotice.text = when {
            !isTestMode -> "테스트 연결 후 테스트 로그 업로드를 사용할 수 있습니다."
            !isSessionActive -> "세션 시작 후 테스트 로그 업로드를 사용할 수 있습니다."
            else -> ""
        }
    }

    private fun setupStatusSpinner() {
        val statusItems = listOf("NORMAL", "WARNING", "ALERT", "STOPPED")
        val adapter = ArrayAdapter(
            requireContext(),
            android.R.layout.simple_spinner_item,
            statusItems
        )
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        binding.spinnerStatus.adapter = adapter
    }

    private fun setupSliders() {
        fun refreshLabels() {
            binding.tvDropCountValue.text =
                "dropCount: ${binding.sliderDropCount.value.toInt()}"

            binding.tvRateValue.text =
                "ratePerMin: ${"%.1f".format(binding.sliderRatePerMin.value)}"

            binding.tvLastDropSecValue.text =
                "lastDropSec: ${"%.1f".format(binding.sliderLastDropSec.value)}"
        }

        binding.sliderDropCount.addOnChangeListener { _, _, _ -> refreshLabels() }
        binding.sliderRatePerMin.addOnChangeListener { _, _, _ -> refreshLabels() }
        binding.sliderLastDropSec.addOnChangeListener { _, _, _ -> refreshLabels() }

        refreshLabels()
    }

    private fun setupButtons() {
        binding.btnUploadTestLog.setOnClickListener {
            if (viewModel.testMode.value != true) {
                android.util.Log.e("UPLOAD_DEBUG", "blocked: testMode=false")
                return@setOnClickListener
            }

            if (viewModel.sessionActive.value != true) {
                android.util.Log.e("UPLOAD_DEBUG", "blocked: sessionActive=false")
                return@setOnClickListener
            }

            val dropCount = binding.sliderDropCount.value.toInt()
            val ratePerMin = binding.sliderRatePerMin.value.toDouble()
            val lastDropSec = binding.sliderLastDropSec.value.toDouble()
            val status = binding.spinnerStatus.selectedItem?.toString() ?: "NORMAL"

            android.util.Log.d(
                "UPLOAD_DEBUG",
                "button clicked dropCount=$dropCount ratePerMin=$ratePerMin lastDropSec=$lastDropSec status=$status"
            )

            viewModel.uploadManualLog(
                dropCount = dropCount,
                ratePerMin = ratePerMin,
                status = status,
                lastDropSec = lastDropSec
            )
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}