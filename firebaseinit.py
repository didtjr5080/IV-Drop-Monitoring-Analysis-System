from datetime import datetime, timezone, timedelta
import firebase_admin
from firebase_admin import credentials, firestore

SERVICE_ACCOUNT_PATH = "serviceAccountKey.json"

if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()
base_time = datetime.now(timezone.utc)

patients_seed = [
    {"patientId": "patient_001", "name": "김민수", "bedNumber": "A-101"},
    {"patientId": "patient_002", "name": "이서연", "bedNumber": "A-102"},
]

for i, patient in enumerate(patients_seed, start=1):
    patient_id = patient["patientId"]
    session_id = f"session_{i:03d}"

    patient_ref = db.collection("patients").document(patient_id)
    patient_ref.set({
        "name": patient["name"],
        "bedNumber": patient["bedNumber"],
        "createdAt": base_time,
    }, merge=True)

    session_ref = patient_ref.collection("sessions").document(session_id)

    warning_count = 0
    alert_count = 0
    total_drops = 0
    rates: list[float] = []

    for j in range(1, 31):
        log_time = base_time + timedelta(seconds=j * 30)
        log_id = f"log_{j:06d}"
        rate = 18.0 + (j * 0.6)
        status = "NORMAL"
        if rate >= 35.0:
            status = "WARNING"
            warning_count += 1
        if rate >= 42.0:
            status = "ALERT"
            alert_count += 1

        total_drops += int(rate)
        rates.append(rate)

        session_ref.collection("logs").document(log_id).set(
            {
                "timestamp": log_time,
                "dropCount": total_drops,
                "ratePerMin": rate,
                "status": status,
                "lastDropSec": round(60.0 / rate, 2),
            },
            merge=True,
        )

    avg_rate = sum(rates) / len(rates)
    session_ref.set(
        {
            "sessionId": session_id,
            "startTime": base_time,
            "endTime": None,
            "totalDrops": total_drops,
            "avgRate": avg_rate,
            "warningCount": warning_count,
            "alertCount": alert_count,
        },
        merge=True,
    )

print("여러 환자/세션/로그 시드 데이터 생성 완료")