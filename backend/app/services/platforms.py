from app.schemas import PlatformMeta

PLATFORMS: list[PlatformMeta] = [
    PlatformMeta(
        code="palantir",
        name="Palantir AIP",
        tag="데이터·운영 분석",
        one_liner="Ontology 기반 비즈니스 데이터 의사결정. KPI·이상감지·예측.",
        strengths=[
            "대규모 데이터 파이프라인",
            "Ontology Objects/Actions",
            "운영 KPI 모니터링",
            "이상 감지·예측",
        ],
        weaknesses=[
            "M365 협업/문서 작업",
            "Legacy 단발 어댑터 통합",
            "소규모 단발 자동화",
        ],
        color="#0E9B7F",
    ),
    PlatformMeta(
        code="copilot",
        name="MS Copilot Studio",
        tag="생산성·협업",
        one_liner="M365 네이티브. Teams·Outlook·SharePoint·Graph API 기반 생산성.",
        strengths=[
            "전사 즉시 배포 (M365 라이선스)",
            "Teams/Outlook/SharePoint 깊은 통합",
            "사용자 접점 최다",
            "온디맨드 응답형",
        ],
        weaknesses=[
            "비-M365 시스템 통합 약함",
            "보안 high(격리) 환경 부적합",
            "복잡한 멀티스텝 워크플로우 한계",
        ],
        color="#1E6FBF",
    ),
    PlatformMeta(
        code="custom",
        name="Custom Agent (AWS/GCP)",
        tag="Legacy 연동 · 보안",
        one_liner="Private VPC 격리. UCube·UCRM·경영지원시스템 깊은 통합. LangGraph 기반.",
        strengths=[
            "사내 Legacy 시스템 깊은 연동 (UCube/UCRM)",
            "Private VPC 격리 실행",
            "복잡한 멀티스텝 자동화",
            "보안 민감 데이터",
        ],
        weaknesses=[
            "개발·운영 비용 최대",
            "사용자 접점 UI 약함",
            "단발 요청에 과한 투자",
        ],
        color="#B86800",
    ),
    PlatformMeta(
        code="ixi",
        name="ixi-Enterprise",
        tag="내부 업무 · 지식",
        one_liner="KnowledgeLake RAG + 사내 워크플로우(AI헬프데스크·결재·온보딩). 담당자 직접 제작.",
        strengths=[
            "KnowledgeLake 기반 RAG (사내 지식 검색)",
            "AI헬프데스크·결재·온보딩 자동화",
            "담당자 self-service 제작",
            "사내 환경 보안",
        ],
        weaknesses=[
            "외부 시스템 깊은 통합 한계",
            "실시간 데이터 파이프라인 약함",
            "데이터 분석 영역",
        ],
        color="#7B35B0",
    ),
]


def get_platforms() -> list[PlatformMeta]:
    return PLATFORMS


def get_platform(code: str) -> PlatformMeta | None:
    return next((p for p in PLATFORMS if p.code == code), None)
