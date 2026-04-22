package com.example.ivmonitor.data

import com.example.ivmonitor.model.DropLog
import com.example.ivmonitor.model.Patient
import com.example.ivmonitor.model.SessionSummary
import com.google.firebase.firestore.FirebaseFirestore
import kotlinx.coroutines.tasks.await
import com.google.firebase.Timestamp
import com.google.firebase.firestore.ListenerRegistration

class FirestoreRepository(
    private val db: FirebaseFirestore = FirebaseFirestore.getInstance()
) {
    fun observePatients(
        onUpdate: (List<Patient>) -> Unit,
        onError: (Exception) -> Unit
    ): ListenerRegistration {

        return db.collection("patients")
            .addSnapshotListener { snapshot, error ->

                if (error != null) {
                    onError(error)
                    return@addSnapshotListener
                }

                val list = snapshot?.documents?.map { doc ->
                    Patient(
                        id = doc.id,
                        name = doc.getString("name").orEmpty(),
                        bedNumber = doc.getString("bedNumber").orEmpty(),
                        createdAt = doc.getTimestamp("createdAt")?.toDate()?.time ?: 0L
                    )
                } ?: emptyList()

                onUpdate(list)
            }
    }
    suspend fun getPatients(): List<Patient> {
        val snapshot = db.collection("patients").get().await()
        return snapshot.documents.map { doc ->
            Patient(
                id = doc.id,
                name = doc.getString("name").orEmpty(),
                bedNumber = doc.getString("bedNumber").orEmpty(),
                createdAt = doc.getTimestamp("createdAt")?.toDate()?.time ?: 0L
            )
        }.sortedBy { it.name }
    }

    suspend fun createSession(patientId: String, summary: SessionSummary) {
        db.collection("patients")
            .document(patientId)
            .collection("sessions")
            .document(summary.sessionId)
            .set(summary)
            .await()
    }

    suspend fun saveLog(patientId: String, sessionId: String, log: DropLog) {
        val logId = log.stableLogId()

        FirebaseFirestore.getInstance()
            .collection("patients")
            .document(patientId)
            .collection("sessions")
            .document(sessionId)
            .collection("logs")
            .document(logId)
            .set(log)
            .await()
    }

    suspend fun updateSessionSummary(patientId: String, session: SessionSummary) {
        db.collection("patients")
            .document(patientId)
            .collection("sessions")
            .document(session.sessionId)
            .set(session)
            .await()
    }
}


