package com.example.ivmonitor.ui

import android.os.Bundle
import android.view.View
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import com.example.ivmonitor.R
import com.example.ivmonitor.databinding.FragmentStatusLogBinding

class StatusLogFragment : Fragment(R.layout.fragment_status_log) {

    private var _binding: FragmentStatusLogBinding? = null
    private val binding get() = _binding!!
    private val viewModel: MainViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentStatusLogBinding.bind(view)

        binding.btnOpenDrawer.setOnClickListener {
            (activity as? MainActivity)?.openDrawer()
        }

        viewModel.statusLog.observe(viewLifecycleOwner) {
            binding.tvStatus.text = it
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}