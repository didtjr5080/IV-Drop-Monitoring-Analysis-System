package com.example.ivmonitor.model

data class SessionSummary(
    val sessionId: String = "",
    val startTime: Long = 0L,
    val endTime: Long? = null,
    val totalDrops: Int = 0,
    val avgRate: Double = 0.0,
    val warningCount: Int = 0,
    val alertCount: Int = 0
)
