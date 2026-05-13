import Link from "next/link";
import { notFound } from "next/navigation";
import { api } from "@/lib/api";
import { ResultPanel } from "@/components/ResultPanel";

export const dynamic = "force-dynamic";

export default async function TicketDetail({
  params,
}: {
  params: { id: string };
}) {
  const id = Number(params.id);
  if (!Number.isFinite(id)) notFound();

  let ticket;
  try {
    ticket = await api.getTicket(id);
  } catch {
    notFound();
  }

  return (
    <div className="mx-auto max-w-[1180px] px-8 pt-10 pb-8">
      <Link
        href="/tickets"
        className="inline-block font-mono text-[11px] uppercase tracking-eyebrow text-ink-soft hover:text-accent"
      >
        ← 이력 목록
      </Link>

      <header className="mt-6 border-y-2 border-ink py-6">
        <div className="flex flex-wrap items-baseline gap-x-4 gap-y-1 font-mono text-[11px] uppercase tracking-eyebrow text-ink-soft">
          <span>#{String(ticket.id).padStart(4, "0")}</span>
          <span className="text-ink-dim">·</span>
          <span>{new Date(ticket.created_at).toLocaleString("ko-KR")}</span>
          <span className="text-ink-dim">·</span>
          <span>{ticket.requester}</span>
        </div>
        <h1 className="mt-3 text-[32px] font-bold leading-[1.2] tracking-tight text-ink md:text-[40px]">
          {ticket.title}
        </h1>
      </header>

      <section className="mt-10 grid grid-cols-1 gap-x-12 gap-y-6 md:grid-cols-[200px_1fr]">
        <div>
          <div className="font-mono text-[11px] uppercase tracking-eyebrow text-ink-soft">
            Submission
          </div>
          <h2 className="mt-1 text-[18px] font-bold leading-tight text-ink">
            접수 내용
          </h2>
          <p className="mt-2 text-[13px] text-ink-soft">
            요청 시점에 입력된 과제 스펙입니다.
          </p>
        </div>

        <dl className="divide-y divide-line border-y-2 border-line">
          <SpecRow label="목적">{ticket.purpose}</SpecRow>
          <SpecRow label="도메인">
            {ticket.domains.length ? ticket.domains.join(" · ") : "—"}
          </SpecRow>
          <SpecRow label="연동 시스템">{ticket.systems || "—"}</SpecRow>
          <SpecRow label="실행 빈도">{ticket.frequency || "—"}</SpecRow>
          <SpecRow label="보안 민감도">{ticket.security || "—"}</SpecRow>
          <SpecRow label="사용자 규모">{ticket.scale || "—"}</SpecRow>
          <SpecRow label="제약사항">{ticket.constraints || "—"}</SpecRow>
        </dl>
      </section>

      <div className="rule-heavy my-12" />

      {ticket.decision ? (
        <ResultPanel result={ticket.decision} />
      ) : (
        <div className="border-2 border-dashed border-line bg-paper-soft px-6 py-10 text-[16px] text-ink-soft">
          이 과제에 대한 라우팅 결정이 아직 없습니다.
        </div>
      )}
    </div>
  );
}

function SpecRow({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-1 py-3.5 md:flex-row md:gap-8">
      <dt className="font-mono text-[10.5px] uppercase tracking-eyebrow text-ink-soft md:w-32">
        {label}
      </dt>
      <dd className="flex-1 text-[15.5px] leading-[1.6] text-ink">{children}</dd>
    </div>
  );
}
