# IVMonitorUploader

Android(Kotlin) + Firebase Firestore + HC-05 Bluetooth 기반 수액 점적 업로드 앱 골격입니다.

## 생성 후 해야 할 일
1. Android Studio로 이 폴더 열기
2. app/google-services.json 추가
3. Firebase Console에서 Firestore 생성
4. Gradle Sync 실행
5. 실제 안드로이드 기기에서 HC-05와 페어링
6. 앱 실행 후 권한 허용

## Firestore 구조
patients/{patientId}/sessions/{sessionId}
patients/{patientId}/sessions/{sessionId}/logs/{logId}
