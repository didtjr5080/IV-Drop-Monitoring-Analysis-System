package com.example.ivmonitor.util

import com.example.ivmonitor.model.DropLog

object DropLogParser {

    fun parse(raw: String): Result<DropLog> {
        return try {
            val cleaned = raw.trim()
            if (cleaned.isBlank()) {
                return Result.failure(IllegalArgumentException("빈 문자열입니다."))
            }

            val pairs = cleaned.split(",")
                .mapNotNull { item ->
                    val idx = item.indexOf("=")
                    if (idx <= 0 || idx == item.length - 1) return@mapNotNull null
                    val key = item.substring(0, idx).trim()
                    val value = item.substring(idx + 1).trim()
                    key to value
                }
                .toMap()

            val timestamp = pairs["timestamp"]?.toLongOrNull()
                ?: return Result.failure(IllegalArgumentException("timestamp 파싱 실패"))
            val dropCount = pairs["dropCount"]?.toIntOrNull()
                ?: return Result.failure(IllegalArgumentException("dropCount 파싱 실패"))
            val ratePerMin = pairs["ratePerMin"]?.toDoubleOrNull()?.toInt()
                ?: return Result.failure(IllegalArgumentException("ratePerMin 파싱 실패"))
            val status = pairs["status"]?.trim()
                ?: return Result.failure(IllegalArgumentException("status 파싱 실패"))
            val lastDropSec = pairs["lastDropSec"]?.toDoubleOrNull()
                ?: return Result.failure(IllegalArgumentException("lastDropSec 파싱 실패"))

            Result.success(
                DropLog(
                    timestamp = timestamp,
                    dropCount = dropCount,
                    ratePerMin = ratePerMin.toDouble(),
                    status = status,
                    lastDropSec = lastDropSec
                )
            )
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
