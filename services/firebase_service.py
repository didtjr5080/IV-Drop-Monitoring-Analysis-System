from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from firebase_admin import credentials, firestore, initialize_app

from models.log import Log
from models.patient import Patient
from models.session import Session


@dataclass
class FirestoreService:
    service_account_path: str
    _client: Any | None = None

    def connect(self) -> None:
        if self._client is not None:
            return
        cred = credentials.Certificate(self.service_account_path)
        initialize_app(cred)
        self._client = firestore.client()

    def _db(self):
        if self._client is None:
            raise RuntimeError("Firestore client not initialized")
        return self._client

    def get_patients(self) -> list[Patient]:
        self.connect()
        docs = self._db().collection("patients").stream()
        patients: list[Patient] = []
        for doc in docs:
            data = doc.to_dict()
            patients.append(
                Patient(
                    patient_id=doc.id,
                    name=data.get("name", "Unknown"),
                    bed_number=str(data.get("bedNumber", "-")),
                    created_at=_to_datetime(data.get("createdAt")),
                )
            )
        return patients

    def get_sessions(self, patient_id: str) -> list[Session]:
        self.connect()
        docs = (
            self._db()
            .collection("patients")
            .document(patient_id)
            .collection("sessions")
            .stream()
        )
        sessions: list[Session] = []
        for doc in docs:
            data = doc.to_dict()
            sessions.append(
                Session(
                    session_id=doc.id,
                    start_time=_to_datetime(data.get("startTime")),
                    end_time=_to_datetime(data.get("endTime")),
                    total_drops=int(data.get("totalDrops", 0)),
                    avg_rate=float(data.get("avgRate", 0.0)),
                    warning_count=int(data.get("warningCount", 0)),
                    alert_count=int(data.get("alertCount", 0)),
                )
            )
        return sorted(sessions, key=lambda s: s.start_time, reverse=True)

    def get_logs(self, patient_id: str, session_id: str) -> list[Log]:
        self.connect()
        docs = (
            self._db()
            .collection("patients")
            .document(patient_id)
            .collection("sessions")
            .document(session_id)
            .collection("logs")
            .stream()
        )
        logs: list[Log] = []
        for doc in docs:
            data = doc.to_dict()
            logs.append(
                Log(
                    timestamp=_to_datetime(data.get("timestamp")),
                    drop_count=int(data.get("dropCount", 0)),
                    rate_per_min=float(data.get("ratePerMin", 0.0)),
                    status=str(data.get("status", "NORMAL")),
                    last_drop_sec=float(data.get("lastDropSec", 0.0)),
                )
            )
        return sorted(logs, key=lambda l: l.timestamp)

    def delete_session(self, patient_id: str, session_id: str) -> None:
        self.connect()
        session_ref = (
            self._db()
            .collection("patients")
            .document(patient_id)
            .collection("sessions")
            .document(session_id)
        )
        logs_ref = session_ref.collection("logs")
        batch = self._db().batch()
        count = 0
        for doc in logs_ref.stream():
            batch.delete(doc.reference)
            count += 1
            if count >= 450:
                batch.commit()
                batch = self._db().batch()
                count = 0
        if count > 0:
            batch.commit()
        session_ref.delete()


def _to_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return _ensure_aware(value)
    if value is None:
        return datetime.now(timezone.utc)
    try:
        return _ensure_aware(value.to_datetime())  # Firestore timestamp
    except Exception:
        return datetime.now(timezone.utc)


def _ensure_aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
