package com.example.ivmonitor.ui

import android.os.Bundle
import android.view.View
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import com.example.ivmonitor.R
import com.example.ivmonitor.databinding.FragmentSessionControlBinding


class SessionControlFragment : Fragment(R.layout.fragment_session_control) {

    private var _binding: FragmentSessionControlBinding? = null
    private val binding get() = _binding!!
    private val viewModel: MainViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentSessionControlBinding.bind(view)

        binding.btnOpenDrawer.setOnClickListener {
            (activity as? MainActivity)?.openDrawer()
        }

        binding.btnStartSession.setOnClickListener {
            viewModel.startSession()
        }

        binding.btnEndSession.setOnClickListener {
            viewModel.endSession()
        }

        viewModel.sessionInfo.observe(viewLifecycleOwner) {
            binding.tvSessionInfo.text = it
        }

        viewModel.connectionState.observe(viewLifecycleOwner) {
            updateButtons()
        }

        viewModel.sessionActive.observe(viewLifecycleOwner) {
            updateButtons()
        }

        viewModel.sessionStarting.observe(viewLifecycleOwner) {
            updateButtons()
        }

        updateButtons()
    }

    private fun updateButtons() {
        val connected = viewModel.connectionState.value == true
        val active = viewModel.sessionActive.value == true
        val starting = viewModel.sessionStarting.value == true

        android.util.Log.d(
            "UI_DEBUG",
            "connected=$connected, active=$active, starting=$starting"
        )

        binding.btnStartSession.visibility = View.VISIBLE
        binding.btnEndSession.visibility = View.VISIBLE

        binding.btnStartSession.isEnabled = connected && !active && !starting
        binding.btnEndSession.isEnabled = active && !starting
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}