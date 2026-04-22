#!/usr/bin/env bash
set -e

PROJECT_NAME="IVMonitorUploader"

echo "========================================"
echo " Post-create setup started"
echo "========================================"

# 1) 현재 위치 점검
if [ ! -f "settings.gradle.kts" ] || [ ! -d "app" ]; then
  echo "[ERROR] 현재 폴더가 Android 프로젝트 루트가 아닙니다."
  echo "        IVMonitorUploader 폴더 안에서 실행하세요."
  exit 1
fi

echo "[OK] Android 프로젝트 루트 확인"

# 2) Firebase 설정 파일 확인
if [ -f "app/google-services.json" ]; then
  echo "[OK] app/google-services.json 존재"
else
  echo "[WARN] app/google-services.json 이 없습니다."
  echo "       Firebase Console에서 Android 앱 등록 후 app/ 폴더에 넣어야 합니다."
fi

# 3) local.properties / SDK 경로 확인
if [ -f "local.properties" ]; then
  echo "[OK] local.properties 존재"
  echo "------ local.properties ------"
  cat local.properties
  echo "------------------------------"
else
  echo "[WARN] local.properties 가 없습니다."
  if [ -n "$ANDROID_SDK_ROOT" ]; then
    SDK_PATH=$(echo "$ANDROID_SDK_ROOT" | sed 's#\\#/#g')
    echo "sdk.dir=$SDK_PATH" > local.properties
    echo "[OK] ANDROID_SDK_ROOT 기반으로 local.properties 생성"
  else
    echo "[WARN] ANDROID_SDK_ROOT 환경변수가 없어 자동 생성하지 못했습니다."
  fi
fi

# 4) gradlew 확인 / 생성 시도
if [ -f "gradlew" ]; then
  echo "[OK] gradlew already exists"
else
  echo "[INFO] gradlew 없음. 생성 시도"

  if command -v gradle >/dev/null 2>&1; then
    echo "[INFO] 시스템 gradle 발견 -> wrapper 생성"
    gradle wrapper
    echo "[OK] gradlew 생성 완료"
  else
    echo "[WARN] 시스템 gradle이 없습니다."
    echo "       Android Studio에서 프로젝트를 열고 Gradle Sync를 먼저 수행하세요."
    echo "       또는 gradle 설치 후 아래 명령 실행:"
    echo "       gradle wrapper"
  fi
fi

# 5) gradlew 실행 권한 부여
if [ -f "gradlew" ]; then
  chmod +x gradlew || true
  echo "[OK] gradlew 실행 권한 설정"
fi

# 6) Git 초기화
if [ -d ".git" ]; then
  echo "[OK] 이미 git 저장소입니다."
else
  git init
  echo "[OK] git init 완료"
fi

# 7) 기본 브랜치 main 설정 시도
git branch -M main || true

# 8) 첫 상태 점검
echo
echo "========== git status =========="
git status --short || true
echo "================================"
echo

# 9) Gradle 간단 점검
if [ -f "gradlew" ]; then
  echo "[INFO] Gradle wrapper 버전 확인"
  ./gradlew --version || true
else
  echo "[WARN] gradlew가 없어 Gradle 점검은 생략"
fi

# 10) 빌드 가능 여부 점검
if [ -f "gradlew" ] && [ -f "app/google-services.json" ]; then
  echo "[INFO] assembleDebug 실행 시도"
  ./gradlew assembleDebug || {
    echo "[WARN] assembleDebug 실패"
    echo "       Android Studio에서 Sync 후 오류 내용을 확인하세요."
  }
else
  echo "[WARN] 빌드 점검 생략"
  echo "       조건: gradlew 존재 + app/google-services.json 존재"
fi

echo
echo "========================================"
echo " Post-create setup finished"
echo "========================================"
echo
echo "[다음 단계]"
echo "1) Android Studio로 프로젝트 열기"
echo "2) app/google-services.json 넣기"
echo "3) Gradle Sync"
echo "4) Firestore 생성"
echo "5) 실제 기기에서 실행"
