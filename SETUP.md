# 환경 셋업 — 처음 실행하는 사람을 위한 가이드

본 문서는 **본 프로젝트를 처음으로 자기 PC에서 띄우는 사람을 위한** 단계별 가이드입니다.
사용자: leehyeongbin94@gmail.com 의 워크스테이션 (Windows 11, Ryzen 7800X3D, RAM 32GB).

> 일반 사용자용 README 와 달리 본 문서는 **OS 단까지** 설명합니다. 셋업이 끝나면 본 문서는 거의 다시 안 봐도 됩니다.

---

## 0. 사전 체크

| 항목 | 본 PC 상태 | 비고 |
|---|---|---|
| OS | Windows 11 26200 | OK |
| CPU 가상화 (펌웨어) | 활성 | BIOS 진입 불필요 |
| RAM | 32 GB | OK |
| 디스크 여유 | D:\\ 960 GB | OK |
| WSL2 | **미설치** | 설치 필요 (install_docker.ps1 이 자동 처리) |
| Docker Desktop | **미설치** | 설치 필요 (install_docker.ps1 이 자동 처리) |
| winget | v1.28 | OK |

---

## 1. 자동 설치 (관리자 PS 1회)

PowerShell 을 **관리자 권한으로** 실행한 뒤:

```powershell
cd D:\workspace\ai-agent-project
powershell -ExecutionPolicy Bypass -File .\install_docker.ps1
```

이 스크립트가 자동으로 처리하는 것:
1. WSL2 활성화 + Linux 커널 설치 (`wsl --install --no-distribution`)
2. Docker Desktop 설치 (`winget install Docker.DockerDesktop`)

**완료 후 시스템 재부팅** 1회. WSL2 커널 활성화에 필요합니다.

---

## 2. Docker Desktop 최초 실행

재부팅 후:

1. 시작 메뉴에서 **Docker Desktop** 실행
2. 라이선스 동의 화면 → "Accept"
3. 'Use the WSL 2 based engine' 옵션 유지 (기본값)
4. 로그인 안 해도 됩니다 (Skip)
5. 트레이 아이콘이 안정화되면 (~30초) 준비 완료

---

## 3. 환경변수 설정

```powershell
cd D:\workspace\ai-agent-project
Copy-Item .env.example .env
notepad .env   # ← ANTHROPIC_API_KEY 를 본인 키로 교체
```

> 키가 없거나 `sk-ant-xxx` 그대로 두면 백엔드가 자동으로 **룰북 fallback 모드** 로 동작합니다 (LLM 자연어 근거 없음, 점수만 제공).

---

## 4. 환경 검증

```powershell
.\verify_env.ps1
```

모든 항목이 OK 면 다음 단계로.

---

## 5. 빌드 & 실행

```powershell
docker compose up --build
```

- **첫 빌드는 3–8분** 정도 걸립니다 (frontend npm install + backend pip install + Postgres pull).
- 모든 서비스가 준비되면 로그에 다음이 나옵니다:
  - `agentplatform-db    | ... database system is ready to accept connections`
  - `agentplatform-backend | INFO:     Application startup complete.`
  - `agentplatform-frontend | ✓ Ready in ...ms`

브라우저:
- http://localhost:3000  — 메인 (Agent 과제 접수 + 라우팅 결과)
- http://localhost:8000/docs — FastAPI Swagger
- http://localhost:8000/healthz — 헬스체크

---

## 6. 종료 / 정리

```powershell
# 컨테이너만 정지 (DB 데이터 보존)
docker compose down

# DB 까지 초기화
docker compose down -v
```

---

## 7. 자주 마주치는 문제

| 증상 | 원인 / 해결 |
|---|---|
| `docker: command not found` | Docker Desktop 미설치 또는 시스템 재부팅 안 됨. |
| 첫 빌드에서 `npm install` 멈춤 | 회사 프록시. `frontend/Dockerfile` 안에서 `npm config set proxy ...` 필요할 수 있음. |
| 포트 충돌 (3000/8000/5432) | 다른 프로세스 점유. `Get-NetTCPConnection -LocalPort 3000` 으로 PID 확인 후 종료. |
| LLM 호출 401/403 | `.env` 의 키 오타. `docker compose restart backend` 로 재로드. |
| LLM 호출 timeout | 사내 방화벽이 api.anthropic.com 차단. 룰북 fallback 으로는 계속 동작. |
| WSL2 가 켜졌는데 distro 가 없다는 경고 | 무시해도 됩니다. Docker Desktop 은 자체 `docker-desktop` distro 를 사용. |

---

## 8. 본 PC 가 아닌 다른 PC 에서도 동일 환경 만들기

본 디렉토리 전체를 `git clone` 또는 USB 복사 후 동일 절차 (1단계부터) 진행하면 됩니다.
`.env` 만 별도 작성하면 끝.
