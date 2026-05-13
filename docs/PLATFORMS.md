# 4 Pillar 플랫폼 룰북

이 문서는 두 가지 역할을 한다:
1. **Rule Router**(`backend/app/services/rule_router.py`)가 코드로 참조하는 정책의 원천.
2. **LLM Router**(`backend/app/prompts/router_system.md`)의 시스템 프롬프트에 임베드되는 자연어 가이드.

수정 시 두 곳이 동기화되어야 한다. 룰북이 변하면 ADR을 남긴다.

---

## 사내 자산 사전 — 회사 시스템 한 줄 정의

| 시스템 | 성격 | 주 매핑 |
|---|---|---|
| **UCube** | 사내 ERP (재무·생산·구매) | Custom |
| **UCRM** | 사내 CRM (고객·계약·청구) | Custom + Palantir |
| **경영지원시스템** | 결재·인사·총무 워크플로우 | Custom + ixi |
| **DataLake** | 사내 데이터 레이크 (대용량 분석 원천) | Palantir |
| **KnowledgeLake** | 사내 지식·문서 저장소 (RAG 소스) | ixi |
| **AI헬프데스크** | 사내 챗봇·티켓팅 | ixi (+ Teams 연동 시 Copilot) |
| **MS Teams** | 협업·메신저 | Copilot |
| **MS SharePoint** | 문서 협업·저장 | Copilot |

---

## 1. Palantir AIP

| 항목 | 값 |
|---|---|
| 코드 | `palantir` |
| 한 줄 | 데이터·운영 분석. Ontology(Objects/Actions) 기반 비즈니스 의사결정. |
| 강점 도메인 | 데이터·분석, KPI 모니터링, 이상 감지, 예측, 통합 데이터 파이프라인 |
| 강한 시스템 | **DataLake**, UCRM(고객 데이터), KPI 대시보드 |
| 약점 | M365 협업·문서 작업, Legacy 단일 어댑터 통합, 소규모 단발 자동화 |
| 보안 | 자체 governance 강력. 그러나 DataLake → Palantir 환경으로의 데이터 이동이 발생 — 일부 PII는 사전 합의 필요 |
| 스케일 | 부서~전사 |
| 실행 빈도 | 시간/일 단위 배치 + 실시간 일부 |

**라우팅 가산:** `data` 도메인, `realtime`/`hourly` 빈도, `department`+ 규모, `medium`+ 보안, DataLake 언급.
**라우팅 감산:** `productivity` 도메인, `individual` 규모.

---

## 2. MS Copilot Studio

| 항목 | 값 |
|---|---|
| 코드 | `copilot` |
| 한 줄 | M365 생태계 네이티브. 사용자 접점 최다. |
| 강점 도메인 | 생산성·협업, 문서 작업, 일정 조정, 이메일/회의록 처리 |
| 강한 시스템 | **MS Teams**, **MS SharePoint**, Outlook, OneDrive, Calendar, Graph API |
| 약점 | 비-M365 시스템 깊은 통합, 복잡한 멀티스텝 워크플로우, 보안 high 격리 환경 |
| 보안 | M365 테넌트 경계 내. 외부 호출은 별도 커넥터 필요 |
| 스케일 | 전사 (M365 라이선스 있으면 즉시 배포) |
| 실행 빈도 | 온디맨드 + 사용자 트리거 |

**라우팅 가산:** `productivity` 도메인, `company` 규모, `ondemand` 빈도, MS Teams/SharePoint 언급.
**라우팅 감산:** `high` 보안 (PII/기밀 + private 네트워크 요건), 사내 Legacy 시스템(UCube/UCRM/경영지원) 언급.

---

## 3. Custom Agent (AWS / GCP)

| 항목 | 값 |
|---|---|
| 코드 | `custom` |
| 한 줄 | 사내 Legacy 운영 시스템 연동 전담. Private VPC. 멀티스텝 자동화. |
| 강점 도메인 | Legacy 연동, 보안 민감, 복잡한 멀티스텝, 커스텀 워크플로우 |
| 강한 시스템 | **UCube** (사내 ERP), **UCRM** (사내 CRM), **경영지원시스템**, 자체 API |
| 약점 | 개발/운영 비용 가장 높음. 사용자 접점 UI 약함. |
| 보안 | private VPC 격리 실행 — 최강 |
| 스케일 | 팀~부서 |
| 실행 빈도 | 임의 (배치~실시간 모두 가능, 단 개발 비용 큼) |

**라우팅 가산:** `legacy` 도메인, `high` 보안, UCube/UCRM/경영지원시스템 언급, private 네트워크 요건.
**라우팅 감산:** `individual` 규모, 단순 온디맨드 요청.

**주의:** custom 은 항상 "왜 다른 3개로 안 되는가"의 근거가 명확해야 한다. 개발 비용이 가장 크기 때문.

---

## 4. ixi-Enterprise

| 항목 | 값 |
|---|---|
| 코드 | `ixi` |
| 한 줄 | 사내 내부 업무 워크플로우 + KnowledgeLake RAG. 담당자 직접 제작. |
| 강점 도메인 | 내부 업무 프로세스, 지식·문서 관리, 결재/온보딩, 부서 요청 처리 |
| 강한 시스템 | **KnowledgeLake**(사내 지식 저장소), **AI헬프데스크**, **경영지원시스템**(결재 연동) |
| 약점 | 외부 시스템 깊은 통합, 데이터 분석 영역 |
| 보안 | 사내 환경 내 운영 — 사실상 high |
| 스케일 | 부서~전사 |
| 실행 빈도 | 온디맨드 위주 |

**라우팅 가산:** `workflow` 도메인, `knowledge` 도메인, `ondemand` 빈도, KnowledgeLake/AI헬프데스크 언급.
**라우팅 감산:** Legacy 운영 데이터 깊은 통합, 실시간 데이터 파이프라인.

---

## 가중치 (Rule Router 초안)

각 플랫폼에 대해 다음 가중합으로 0~100 점수 산출:

```
score = base(50)
       + domain_match * 12      (각 매칭 도메인)
       + system_match * 10      (각 매칭 시스템 키워드)
       + frequency_fit * 8
       + security_fit * 10
       + scale_fit * 6
       - hard_constraint_violation * 30
```

LLM Router는 이 점수를 *수정 가능*. 단, 30점 이상 뒤집는 경우 자연어 근거 의무.

---

## 변경 이력

- 2026-05-13: 초안 작성 (Phase 0)
- 2026-05-14: 사내 자산 사전 추가 — UCube / UCRM / 경영지원시스템 / DataLake / KnowledgeLake / AI헬프데스크 / MS Teams / MS SharePoint 로 SYSTEM_AFFINITY 갈아엎음. 외부 일반 명칭(SAP/Oracle/MES/SCADA/Foundry/KMS 등) 제거. ADR-0003 참조.
