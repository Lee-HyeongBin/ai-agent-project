import Link from "next/link";
import { api, PLATFORM_NAME, PlatformCode } from "@/lib/api";

export const dynamic = "force-dynamic";

const DARK: Record<PlatformCode, string> = {
  palantir: "#0A7A63",
  copilot:  "#185793",
  custom:   "#8A4F00",
  ixi:      "#5F2890",
};

export default async function TicketsPage() {
  let tickets;
  let err: string | null = null;
  try {
    tickets = await api.listTickets({ limit: 100 });
  } catch (e: any) {
    err = e.message || "이력을 불러오지 못했습니다.";
    tickets = [];
  }

  return (
    <div className="mx-auto max-w-[1180px] px-8 pt-12 pb-8">
      <header className="mb-10">
        <div className="flex items-end justify-between gap-6">
          <div>
            <div className="font-mono text-[11px] uppercase tracking-eyebrow text-ink-soft">
              History
            </div>
            <h1 className="mt-3 text-[36px] font-bold leading-tight tracking-tight text-ink md:text-[44px]">
              라우팅 이력
            </h1>
          </div>
          <Link
            href="/"
            className="border-2 border-ink bg-paper px-5 py-2.5 text-[14px] font-semibold text-ink transition hover:bg-paper-soft"
          >
            + 새 과제 접수
          </Link>
        </div>
        <p className="mt-5 max-w-[62ch] text-[16px] leading-[1.65] text-ink-soft">
          접수·라우팅된 모든 Agent 과제는 결정 근거·점수·대안과 함께 영구 보관됩니다.
          행을 클릭하면 LLM의 자연어 근거 전문을 확인할 수 있습니다.
        </p>
      </header>

      <div className="rule-heavy mb-6" />

      {err && (
        <div className="mb-6 flex items-start gap-3 border-l-[3px] border-accent bg-accent-soft px-5 py-3 text-[14px] text-accent-hov">
          <span className="font-mono text-[11px] uppercase tracking-eyebrow text-accent">Error</span>
          <span>{err}</span>
        </div>
      )}

      {tickets.length === 0 ? (
        <EmptyState />
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="border-b-2 border-ink">
                <Th>No.</Th>
                <Th>제목 · 목적</Th>
                <Th>요청자</Th>
                <Th>플랫폼</Th>
                <Th className="text-right">신뢰도</Th>
                <Th>접수일</Th>
              </tr>
            </thead>
            <tbody>
              {tickets.map((t, idx) => (
                <tr
                  key={t.id}
                  className="border-b border-line align-top transition hover:bg-paper-soft"
                >
                  <Td>
                    <span className="font-mono text-[12px] font-medium text-ink-dim">
                      {String(idx + 1).padStart(2, "0")}
                    </span>
                  </Td>
                  <Td>
                    <Link
                      href={`/tickets/${t.id}`}
                      className="text-[16px] font-semibold leading-tight text-ink underline-offset-4 hover:text-accent hover:underline"
                    >
                      {t.title}
                    </Link>
                    <p className="mt-1 line-clamp-2 max-w-[60ch] text-[13.5px] leading-snug text-ink-soft">
                      {t.purpose}
                    </p>
                  </Td>
                  <Td>
                    <span className="text-[14px] text-ink">
                      {t.requester || "anonymous"}
                    </span>
                  </Td>
                  <Td>
                    {t.decision ? (
                      <PlatformTag code={t.decision.primary} />
                    ) : (
                      <span className="font-mono text-[12px] text-ink-dim">—</span>
                    )}
                  </Td>
                  <Td className="text-right">
                    {t.decision ? (
                      <span
                        className="text-[22px] font-bold leading-none tracking-tight"
                        style={{ color: DARK[t.decision.primary] }}
                      >
                        {t.decision.confidence}
                        <span className="ml-0.5 font-mono text-[11px] font-normal text-ink-dim">
                          %
                        </span>
                      </span>
                    ) : (
                      <span className="font-mono text-[12px] text-ink-dim">—</span>
                    )}
                  </Td>
                  <Td>
                    <span className="font-mono text-[11px] uppercase tracking-eyebrow text-ink-dim">
                      {new Date(t.created_at).toLocaleString("ko-KR", {
                        year: "2-digit",
                        month: "2-digit",
                        day: "2-digit",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </span>
                  </Td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function Th({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <th
      className={
        "px-3 py-3 text-left font-mono text-[10.5px] font-medium uppercase tracking-eyebrow text-ink-soft " +
        className
      }
    >
      {children}
    </th>
  );
}

function Td({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <td className={`px-3 py-5 align-top ${className}`}>{children}</td>;
}

function PlatformTag({ code }: { code: PlatformCode }) {
  const color = DARK[code];
  return (
    <span
      className="inline-flex items-center gap-2 border-l-[3px] pl-2 text-[14px] font-semibold leading-tight"
      style={{ borderColor: color, color }}
    >
      {PLATFORM_NAME[code]}
    </span>
  );
}

function EmptyState() {
  return (
    <div className="border-2 border-dashed border-line bg-paper-soft py-20 text-center">
      <p className="text-[18px] text-ink-soft">아직 접수된 과제가 없습니다.</p>
      <Link
        href="/"
        className="mt-6 inline-block bg-ink px-6 py-3 text-[14px] font-semibold text-paper transition hover:bg-accent"
      >
        첫 과제 접수하기 →
      </Link>
    </div>
  );
}
