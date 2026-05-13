"use client";

import { useState } from "react";
import { api, RouteResult, TicketCreate } from "@/lib/api";
import { ResultPanel } from "./ResultPanel";

const DOMAINS = [
  { v: "data",          label: "데이터·분석" },
  { v: "productivity",  label: "생산성·협업" },
  { v: "legacy",        label: "Legacy 연동" },
  { v: "workflow",      label: "내부 업무 프로세스" },
  { v: "knowledge",     label: "지식·문서 관리" },
  { v: "crossplatform", label: "크로스 플랫폼" },
] as const;

const FREQUENCY = [
  { v: "realtime",  label: "실시간 (분 단위)" },
  { v: "hourly",    label: "시간 단위" },
  { v: "daily",     label: "일 단위" },
  { v: "weekly",    label: "주 단위" },
  { v: "ondemand",  label: "온디맨드 (사용자 요청 시)" },
];

const SECURITY = [
  { v: "low",    label: "낮음" },
  { v: "medium", label: "중간" },
  { v: "high",   label: "높음 (PII/기밀)" },
];

const SCALE = [
  { v: "individual",  label: "개인" },
  { v: "team",        label: "팀 (10명 내외)" },
  { v: "department",  label: "부서 (100명+)" },
  { v: "company",     label: "전사" },
];

export function RouteForm() {
  const [title, setTitle] = useState("");
  const [requester, setRequester] = useState("");
  const [purpose, setPurpose] = useState("");
  const [systems, setSystems] = useState("");
  const [frequency, setFrequency] = useState("");
  const [constraints, setConstraints] = useState("");
  const [domains, setDomains] = useState<Set<string>>(new Set());
  const [security, setSecurity] = useState("");
  const [scale, setScale] = useState("");

  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [result, setResult] = useState<RouteResult | null>(null);
  const [savedTicketId, setSavedTicketId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const toggleDomain = (v: string) =>
    setDomains((prev) => {
      const next = new Set(prev);
      if (next.has(v)) next.delete(v);
      else next.add(v);
      return next;
    });

  const payload = () => ({
    purpose: purpose.trim(),
    domains: Array.from(domains),
    systems: systems.trim() || null,
    frequency: frequency || null,
    security: security || null,
    scale: scale || null,
    constraints: constraints.trim() || null,
  });

  const analyze = async () => {
    setError(null);
    if (purpose.trim().length < 5) {
      setError("Agent 목적을 5자 이상 입력해 주세요.");
      return;
    }
    setLoading(true);
    setSavedTicketId(null);
    try {
      const r = await api.route(payload());
      setResult(r);
    } catch (e: any) {
      setError(e.message || "분석 중 오류가 발생했습니다.");
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const save = async () => {
    setError(null);
    if (!title.trim()) {
      setError("이력으로 저장하려면 과제 제목을 입력해 주세요.");
      return;
    }
    setSaving(true);
    try {
      const created: TicketCreate = {
        ...payload(),
        title: title.trim(),
        requester: requester.trim() || "anonymous",
      };
      const t = await api.createTicket(created);
      setSavedTicketId(t.id);
      setResult(t.decision);
    } catch (e: any) {
      setError(e.message || "저장 중 오류가 발생했습니다.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-10">
      <section>
        <SectionHead eyebrow="Submission" title="Agent 스펙 입력" hint="제목·도메인·시스템 등 빈칸을 채울수록 라우팅 정확도가 올라갑니다." />

        <div className="grid grid-cols-1 gap-x-10 gap-y-7 md:grid-cols-12">
          <Field className="md:col-span-12" label="과제 제목" hint="이력 저장 시 필요">
            <Input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="예) ERP 일일 생산데이터 이상감지 알림"
            />
          </Field>

          <Field className="md:col-span-7" label="요청자 (이름 / 부서)">
            <Input
              value={requester}
              onChange={(e) => setRequester(e.target.value)}
              placeholder="전영환 / Personal Agent 기술팀"
            />
          </Field>

          <Field className="md:col-span-5" label="실행 빈도">
            <Select value={frequency} onChange={(e) => setFrequency(e.target.value)}>
              <option value="">선택하세요</option>
              {FREQUENCY.map((f) => (
                <option key={f.v} value={f.v}>{f.label}</option>
              ))}
            </Select>
          </Field>

          <Field className="md:col-span-12" label="Agent 목적" required>
            <Textarea
              value={purpose}
              onChange={(e) => setPurpose(e.target.value)}
              placeholder="예) 매일 오전 ERP에서 생산 데이터를 추출하여 이상값을 감지하고 담당자에게 알림을 보내는 Agent"
              rows={3}
            />
          </Field>

          <Field className="md:col-span-12" label="주요 도메인 / 업무 유형" hint="복수 선택 가능">
            <div className="flex flex-wrap gap-2.5">
              {DOMAINS.map((d) => {
                const active = domains.has(d.v);
                return (
                  <button
                    key={d.v}
                    type="button"
                    aria-pressed={active}
                    onClick={() => toggleDomain(d.v)}
                    className={
                      "inline-flex items-center gap-2 border-2 px-4 py-2 text-[14px] font-medium transition " +
                      (active
                        ? "border-ink bg-ink text-paper shadow-[3px_3px_0_0_#7A1F2B]"
                        : "border-line bg-paper text-ink-soft hover:border-ink hover:text-ink")
                    }
                  >
                    <span
                      className={
                        "inline-block h-2 w-2 rounded-full transition " +
                        (active ? "bg-accent" : "border border-line-strong bg-transparent")
                      }
                    />
                    {d.label}
                  </button>
                );
              })}
            </div>
          </Field>

          <Field className="md:col-span-12" label="연동 시스템">
            <Input
              value={systems}
              onChange={(e) => setSystems(e.target.value)}
              placeholder="예) SAP ERP, Oracle DB, Teams, SharePoint, Foundry"
            />
          </Field>

          <Field className="md:col-span-6" label="보안·데이터 민감도">
            <Pills value={security} onChange={setSecurity} options={SECURITY} />
          </Field>

          <Field className="md:col-span-6" label="예상 사용자 규모">
            <Pills value={scale} onChange={setScale} options={SCALE} />
          </Field>

          <Field className="md:col-span-12" label="추가 요구사항 / 제약사항">
            <Textarea
              value={constraints}
              onChange={(e) => setConstraints(e.target.value)}
              placeholder="예) Private 네트워크 내에서만 실행되어야 함, M365 계정으로 로그인한 사용자만 접근 가능"
              rows={2}
            />
          </Field>
        </div>

        <div className="mt-10 flex flex-col gap-3 md:flex-row">
          <button
            onClick={analyze}
            disabled={loading || saving}
            className="flex flex-1 items-center justify-center gap-3 bg-ink px-8 py-4 text-[16px] font-semibold tracking-tight text-paper transition hover:bg-accent disabled:cursor-not-allowed disabled:opacity-40"
          >
            {loading && <Spinner />}
            <span>{loading ? "분석 중…" : "최적 플랫폼 분석"}</span>
            <span aria-hidden className="text-paper/60">→</span>
          </button>
          <button
            onClick={save}
            disabled={loading || saving || !result}
            title={!result ? "먼저 분석을 실행해 주세요" : ""}
            className="border-2 border-ink bg-paper px-7 py-4 text-[16px] font-semibold tracking-tight text-ink transition hover:bg-paper-soft disabled:cursor-not-allowed disabled:border-line disabled:text-ink-dim"
          >
            {saving ? "저장 중…" : "이력으로 저장"}
          </button>
        </div>

        {savedTicketId && (
          <div className="mt-5 flex items-center gap-3 border-l-[3px] border-teal bg-paper-soft px-5 py-3 text-[14px] text-ink">
            <span className="font-mono text-[11px] uppercase tracking-eyebrow text-teal">✓ Saved</span>
            <span>
              과제 #{savedTicketId} 로 이력에 저장되었습니다.{" "}
              <a href={`/tickets`} className="font-semibold text-accent underline underline-offset-4 hover:text-accent-hov">
                이력 보기
              </a>
            </span>
          </div>
        )}

        {error && (
          <div className="mt-5 flex items-start gap-3 border-l-[3px] border-accent bg-accent-soft px-5 py-3 text-[14px] text-accent-hov">
            <span className="font-mono text-[11px] uppercase tracking-eyebrow text-accent">Error</span>
            <span>{error}</span>
          </div>
        )}
      </section>

      {result && <ResultPanel result={result} />}
    </div>
  );
}

/* ─── primitives ──────────────────────────────────────────────── */

function SectionHead({
  eyebrow,
  title,
  hint,
}: {
  eyebrow: string;
  title: string;
  hint?: string;
}) {
  return (
    <div className="mb-8 border-b-2 border-ink pb-3">
      <div className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between md:gap-6">
        <div>
          <div className="font-mono text-[11px] uppercase tracking-eyebrow text-ink-soft">
            {eyebrow}
          </div>
          <h2 className="mt-1 text-[26px] font-bold leading-tight tracking-tight text-ink">
            {title}
          </h2>
        </div>
        {hint && (
          <p className="max-w-sm text-[13.5px] leading-snug text-ink-soft md:text-right">
            {hint}
          </p>
        )}
      </div>
    </div>
  );
}

function Field({
  label,
  hint,
  required,
  className = "",
  children,
}: {
  label: string;
  hint?: string;
  required?: boolean;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <div className={className}>
      <label className="mb-2 flex items-baseline gap-2">
        <span className="font-mono text-[11px] uppercase tracking-eyebrow text-ink">
          {label}
        </span>
        {required && <span className="font-mono text-[11px] text-accent">*</span>}
        {hint && <span className="text-[12px] text-ink-dim">— {hint}</span>}
      </label>
      {children}
    </div>
  );
}

function Input(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      {...props}
      className="w-full border-0 border-b-2 border-line bg-transparent px-1 py-2.5 text-[16px] text-ink placeholder:text-ink-dim focus:border-ink focus:outline-none"
    />
  );
}

function Textarea({
  rows = 3,
  ...props
}: React.TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      rows={rows}
      {...props}
      className="w-full border border-line bg-paper px-4 py-3 text-[16px] leading-[1.55] text-ink placeholder:text-ink-dim focus:border-ink focus:outline-none"
    />
  );
}

function Select({
  children,
  ...props
}: React.SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select
      {...props}
      className="w-full appearance-none border-0 border-b-2 border-line bg-transparent bg-[url('data:image/svg+xml;utf8,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 12 12%22><path fill=%22%23171717%22 d=%22M6 8L2 4h8z%22/></svg>')] bg-[length:12px_12px] bg-[right_4px_center] bg-no-repeat py-2.5 pl-1 pr-8 text-[16px] text-ink focus:border-ink focus:outline-none"
    >
      {children}
    </select>
  );
}

function Pills({
  value,
  onChange,
  options,
}: {
  value: string;
  onChange: (v: string) => void;
  options: { v: string; label: string }[];
}) {
  return (
    <div className="flex flex-wrap gap-2.5">
      {options.map((o) => {
        const active = value === o.v;
        return (
          <button
            key={o.v}
            type="button"
            aria-pressed={active}
            onClick={() => onChange(active ? "" : o.v)}
            className={
              "border-2 px-4 py-2 text-[14px] font-medium transition " +
              (active
                ? "border-ink bg-ink text-paper shadow-[3px_3px_0_0_#7A1F2B]"
                : "border-line bg-paper text-ink-soft hover:border-ink hover:text-ink")
            }
          >
            {o.label}
          </button>
        );
      })}
    </div>
  );
}

function Spinner() {
  return (
    <span
      className="inline-block h-4 w-4 animate-spin-slow rounded-full border-2 border-paper/40 border-t-paper"
      aria-hidden
    />
  );
}
