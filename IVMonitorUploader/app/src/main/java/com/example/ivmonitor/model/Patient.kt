package com.example.ivmonitor.model

data class Patient(
    val id: String = "",
    val name: String = "",
    val bedNumber: String = "",
    val createdAt: Long = 0L
) {
    override fun toString(): String {
        return if (name.isNotBlank()) {
            "$name (${if (bedNumber.isNotBlank()) bedNumber else id})"
        } else {
            id
        }
    }
}