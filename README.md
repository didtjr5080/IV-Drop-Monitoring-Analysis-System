# 수액 점적 모니터링 및 분석 PC 프로그램

## 개요
PyQt6 기반 데스크톱 관제/분석 앱입니다. Firebase Firestore 또는 Mock 데이터로 환자별 점적 로그를 시각화합니다.

## 설치
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 실행
```bash
python main.py
```

## Firebase 설정
1. Firebase Admin SDK 서비스 계정 키(JSON) 다운로드
2. [config/settings.py](config/settings.py)에서 경로 지정
3. `use_mock_data = False`로 변경

## Mock 모드
[config/settings.py](config/settings.py)에서 `use_mock_data = True` 설정

## 데이터 구조 (Firestore)
```
patients/{patientId}
patients/{patientId}/sessions/{sessionId}
patients/{patientId}/sessions/{sessionId}/logs/{logId}
```

## 주요 기능
- 환자 리스트 / 검색
- 세션 테이블
- 분석 요약 카드
- 시간 대비 점적 속도/누적 차트
- WARNING/ALERT 타임라인

## 실행 체크
- PyQt6, matplotlib 설치 확인
- Firestore 서비스 계정 경로 확인
- 네트워크 방화벽 정책 확인
