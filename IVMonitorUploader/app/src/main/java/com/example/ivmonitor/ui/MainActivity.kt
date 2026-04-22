package com.example.ivmonitor.ui
// test git change
import android.os.Bundle
import android.view.MenuItem
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.GravityCompat
import com.example.ivmonitor.R
import com.example.ivmonitor.databinding.ActivityMainBinding
import com.google.android.material.navigation.NavigationView
import com.google.android.material.tabs.TabLayoutMediator
import android.util.Log
import com.google.firebase.firestore.FirebaseFirestore
class MainActivity : AppCompatActivity(), NavigationView.OnNavigationItemSelectedListener {

    private lateinit var binding: ActivityMainBinding
    private val viewModel: MainViewModel by viewModels()

    val tabTitles = listOf("환자/연결", "세션", "테스트 업로드", "상태 로그")

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupToolbar()
        setupPager()
        setupDrawer()
        observeHeaderState()
        testFirestore()
    }

    private fun setupToolbar() {
        setSupportActionBar(binding.toolbar)

        binding.toolbar.setNavigationOnClickListener {
            openDrawer()
        }
    }

    private fun testFirestore() {
        FirebaseFirestore.getInstance()
            .collection("debug")
            .document("ping")
            .set(
                mapOf(
                    "time" to System.currentTimeMillis(),
                    "message" to "firestore_test"
                )
            )
            .addOnSuccessListener {
                Log.d("FIRESTORE_TEST", "write success")
            }
            .addOnFailureListener { e ->
                Log.e("FIRESTORE_TEST", "write fail", e)
            }
    }

    private fun setupPager() {
        binding.viewPager.adapter = MainPagerAdapter(this)

        TabLayoutMediator(binding.tabLayout, binding.viewPager) { tab, position ->
            tab.text = tabTitles[position]
        }.attach()

        binding.viewPager.registerOnPageChangeCallback(object :
            androidx.viewpager2.widget.ViewPager2.OnPageChangeCallback() {
            override fun onPageSelected(position: Int) {
                super.onPageSelected(position)
                when (position) {
                    0 -> binding.navigationView.setCheckedItem(R.id.nav_patient_connection)
                    1 -> binding.navigationView.setCheckedItem(R.id.nav_session_control)
                    2 -> binding.navigationView.setCheckedItem(R.id.nav_status_log)
                }
            }
        })
    }

    private fun setupDrawer() {
        binding.navigationView.setNavigationItemSelectedListener(this)
        binding.navigationView.setCheckedItem(R.id.nav_patient_connection)
    }

    private fun observeHeaderState() {
        viewModel.connectionState.observe(this) { connected ->
            if (connected) {
                binding.layoutConnectionBadge.setBackgroundResource(R.drawable.bg_status_badge_connected)
                binding.viewConnectionDot.setBackgroundResource(R.drawable.bg_dot_green)
                binding.tvConnectionBadge.text = "연결됨"
            } else {
                binding.layoutConnectionBadge.setBackgroundResource(R.drawable.bg_status_badge_disconnected)
                binding.viewConnectionDot.setBackgroundResource(R.drawable.bg_dot_red)
                binding.tvConnectionBadge.text = "미연결"
            }
        }
    }

    override fun onNavigationItemSelected(item: MenuItem): Boolean {
        when (item.itemId) {
            R.id.nav_patient_connection -> binding.viewPager.currentItem = 0
            R.id.nav_session_control -> binding.viewPager.currentItem = 1
            R.id.nav_status_log -> binding.viewPager.currentItem = 2
        }

        binding.drawerLayout.closeDrawer(GravityCompat.START)
        return true
    }

    fun openDrawer() {
        binding.drawerLayout.openDrawer(GravityCompat.START)
    }

    override fun onBackPressed() {
        if (binding.drawerLayout.isDrawerOpen(GravityCompat.START)) {
            binding.drawerLayout.closeDrawer(GravityCompat.START)
        } else {
            super.onBackPressed()
        }
    }
}