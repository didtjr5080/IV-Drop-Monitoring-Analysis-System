package com.example.ivmonitor.ui

import androidx.appcompat.app.AppCompatActivity
import androidx.fragment.app.Fragment
import androidx.viewpager2.adapter.FragmentStateAdapter

class MainPagerAdapter(activity: AppCompatActivity) : FragmentStateAdapter(activity) {

    override fun getItemCount(): Int = 4

    override fun createFragment(position: Int): Fragment {
        return when (position) {
            0 -> PatientConnectionFragment()
            1 -> SessionControlFragment()
            2 -> TestUploadFragment()
            3 -> StatusLogFragment()
            else -> PatientConnectionFragment()
        }
    }
}