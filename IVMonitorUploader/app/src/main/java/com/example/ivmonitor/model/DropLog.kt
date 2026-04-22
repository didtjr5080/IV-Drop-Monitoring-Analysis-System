package com.example.ivmonitor.model

data class DropLog(
    val timestamp: Long = 0L,
    val dropCount: Int = 0,
    val ratePerMin: Double = 0.0,   // 🔥 여기 수정
    val status: String = "",
    val lastDropSec: Double = 0.0
) {
    fun stableLogId(): String = "${timestamp}_${dropCount}"
}
