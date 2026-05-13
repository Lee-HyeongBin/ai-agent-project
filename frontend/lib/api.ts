// 백엔드 클라이언트.
//
// 브라우저(클라이언트 컴포넌트)는 NEXT_PUBLIC_API_BASE 를,
// 서버사이드(서버 컴포넌트/액션)는 INTERNAL_API_BASE 를 사용.
//
// 둘 다 비어있으면 브라우저는 동일 오리진 상대경로, 서버는 backend:8000 가정.

export type PlatformCode = "palantir" | "copilot" | "custom" | "ixi";

export interface RouteRequest {
  purpose: string;
  domains: string[];
  systems?: string | null;
  frequency?: string | null;
  security?: string | null;
  scale?: string | null;
  constraints?: string | null;
}

export interface TicketCreate extends RouteRequest {
  title: string;
  requester: string;
}

export interface PlatformScores {
  palantir: number;
  copilot: number;
  custom: number;
  ixi: number;
}

export interface RouteResult {
  primary: PlatformCode;
  confidence: number;
  verdict: string;
  verdict_sub: string;
  reasoning: string;
  scores: PlatformScores;
  rule_scores: PlatformScores;
  stack: string[];
  alternatives: string[];
  warnings: string[];
  model: string;
}

export interface TicketOut {
  id: number;
  title: string;
  purpose: string;
  domains: string[];
  systems: string | null;
  frequency: string | null;
  security: string | null;
  scale: string | null;
  constraints: string | null;
  requester: string;
  created_at: string;
  decision: RouteResult | null;
}

export interface PlatformMeta {
  code: PlatformCode;
  name: string;
  tag: string;
  one_liner: string;
  strengths: string[];
  weaknesses: string[];
  color: string;
}

function clientBase(): string {
  return process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
}

function serverBase(): string {
  return (
    process.env.INTERNAL_API_BASE ||
    process.env.NEXT_PUBLIC_API_BASE ||
    "http://backend:8000"
  );
}

function base(): string {
  return typeof window === "undefined" ? serverBase() : clientBase();
}

async function jsonFetch<T>(
  path: string,
  init?: RequestInit & { cache?: RequestCache }
): Promise<T> {
  const res = await fetch(`${base()}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
    cache: init?.cache ?? "no-store",
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`API ${res.status}: ${text || res.statusText}`);
  }
  return (await res.json()) as T;
}

export const api = {
  route: (req: RouteRequest) =>
    jsonFetch<RouteResult>("/api/route", {
      method: "POST",
      body: JSON.stringify(req),
    }),
  createTicket: (req: TicketCreate) =>
    jsonFetch<TicketOut>("/api/tickets", {
      method: "POST",
      body: JSON.stringify(req),
    }),
  listTickets: (params?: { limit?: number; offset?: number; platform?: string }) => {
    const q = new URLSearchParams();
    if (params?.limit) q.set("limit", String(params.limit));
    if (params?.offset) q.set("offset", String(params.offset));
    if (params?.platform) q.set("platform", params.platform);
    const qs = q.toString();
    return jsonFetch<TicketOut[]>(`/api/tickets${qs ? "?" + qs : ""}`);
  },
  getTicket: (id: number) => jsonFetch<TicketOut>(`/api/tickets/${id}`),
  platforms: () => jsonFetch<PlatformMeta[]>("/api/platforms"),
};

// PLATFORM_COLOR: 원본(다크 배경에서 채도 살린) 톤. 라이트 디자인 진입 후에는
// PLATFORM_DARK 를 일관 사용. 본 상수는 backwards-compat용.
export const PLATFORM_COLOR: Record<PlatformCode, string> = {
  palantir: "#0E9B7F",
  copilot: "#1E6FBF",
  custom: "#B86800",
  ixi: "#7B35B0",
};

// PLATFORM_DARK: editorial 라이트 톤(흰 배경 위) 텍스트·라인용. 채도 조금 낮춰 가독성 ↑.
export const PLATFORM_DARK: Record<PlatformCode, string> = {
  palantir: "#0A7A63",
  copilot:  "#185793",
  custom:   "#8A4F00",
  ixi:      "#5F2890",
};

// PLATFORM_TINT: 카드/패널 배경에 사용하는 매우 연한 톤. (1차 인상은 거의 흰색)
export const PLATFORM_TINT: Record<PlatformCode, string> = {
  palantir: "#F0F7F4",
  copilot:  "#F0F5FA",
  custom:   "#F8F2E6",
  ixi:      "#F5EFFA",
};

export const PLATFORM_NAME: Record<PlatformCode, string> = {
  palantir: "Palantir AIP",
  copilot: "MS Copilot Studio",
  custom: "Custom Agent",
  ixi: "ixi-Enterprise",
};

export const PLATFORM_TAG: Record<PlatformCode, string> = {
  palantir: "데이터·운영 분석",
  copilot: "생산성·협업",
  custom: "Legacy 연동·보안",
  ixi: "내부 업무·지식",
};
