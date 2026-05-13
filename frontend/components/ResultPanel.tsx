import {
  PLATFORM_DARK,
  PLATFORM_NAME,
  PLATFORM_TAG,
  PlatformCode,
  RouteResult,
} from "@/lib/api";

const ORDER: PlatformCode[] = ["palantir", "copilot", "custom", "ixi"];

export function ResultPanel({ result }: { result: RouteResult }) {
  const winnerColor = PLATFORM_DARK[result.primary];

  return (
    <section className="animate-fadeUp">
      <div className="mb-8 border-b-2 border-ink pb-3">
        <div className="font-mono text-[11px] uppercase tracking-eyebrow text-ink-soft">
          Result
        </div>
        <h2 className="mt-1 text-[26px] font-bold leading-tight tracking-tight text-ink">
          라우팅 결과
        </h2>
      </div>

      {/* Verdict */}
      <article className="grid grid-cols-1 gap-y-6 border-y-2 border-ink py-7 md:grid-cols-[1fr_280px] md:gap-x-10">
        <div>
          <div
            className="font-mono text-[11px] font-medium uppercase tracking-eyebrow"
            style={{ color: winnerColor }}
          >
            추천 플랫폼 · {result.primary.toUpperCase()}
          </div>
          <h3
            className="mt-3 text-[34px] font-bold leading-[1.15] tracking-tight md:text-[40px]"
            style={{ color: winnerColor }}
          >
            {result.verdict}
          </h3>
          <p className="mt-3 text-[17px] leading-snug text-ink-soft">
            {result.verdict_sub}
          </p>
        </div>

        <aside className="border-l-2 border-line pl-6">
          <div className="font-mono text-[10.5px] uppercase tracking-eyebrow text-ink-dim">
            Confidence
          </div>
          <div className="mt-1 flex items-baseline gap-1">
            <span
              className="text-[56px] font-bold leading-none tracking-tight"
              style={{ color: winnerColor }}
            >
              {result.confidence}
            </span>
            <span className="font-mono text-[14px] text-ink-dim">%</span>
          </div>
          <div className="mt-4 h-[3px] w-full bg-line-soft">
            <div
              className="h-full transition-all duration-700"
              style={{ width: `${result.confidence}%`, background: winnerColor }}
            />
          </div>
          <div className="mt-4 font-mono text-[10.5px] uppercase tracking-eyebrow text-ink-dim">
            Model
          </div>
          <div className="mt-1 font-mono text-[12px] text-ink">{result.model}</div>
        </aside>
      </article>

      {/* Scores */}
      <div className="mt-12">
        <div className="mb-5 flex items-baseline justify-between border-b border-line pb-2">
          <h4 className="text-[18px] font-bold tracking-tight text-ink">
            플랫폼별 점수
          </h4>
          <div className="font-mono text-[10.5px] uppercase tracking-eyebrow text-ink-dim">
            LLM Score · Rulebook
          </div>
        </div>

        <div className="grid grid-cols-1 gap-y-6 md:grid-cols-4 md:gap-x-8">
          {ORDER.map((code, i) => {
            const color = PLATFORM_DARK[code];
            const score = result.scores[code];
            const rule = result.rule_scores[code];
            const isWinner = code === result.primary;
            return (
              <div key={code}>
                <div className="flex items-baseline gap-2">
                  <span className="font-mono text-[11px] font-medium text-ink-dim">
                    0{i + 1}
                  </span>
                  <span
                    className="text-[14.5px] font-semibold leading-tight"
                    style={{ color }}
                  >
                    {PLATFORM_NAME[code]}
                  </span>
                </div>
                <div className="mt-1 font-mono text-[10.5px] uppercase tracking-eyebrow text-ink-dim">
                  {PLATFORM_TAG[code]}
                </div>

                <div className="mt-3 flex items-baseline gap-1.5">
                  <span
                    className="text-[40px] font-bold leading-none tracking-tight"
                    style={{ color }}
                  >
                    {score}
                  </span>
                  <span className="font-mono text-[11px] text-ink-dim">/100</span>
                </div>
                <div className="mt-2 h-[2px] w-full bg-line-soft">
                  <div
                    className="h-full transition-all duration-700"
                    style={{ width: `${score}%`, background: color }}
                  />
                </div>
                <div className="mt-2 font-mono text-[10.5px] uppercase tracking-eyebrow text-ink-dim">
                  Rulebook {rule}
                </div>

                {isWinner && (
                  <div
                    className="mt-3 inline-flex items-center gap-1 border px-2 py-0.5 font-mono text-[10px] uppercase tracking-eyebrow"
                    style={{ color, borderColor: color }}
                  >
                    ★ Pick
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Reasoning */}
      <div className="mt-12 grid grid-cols-1 gap-x-10 gap-y-4 md:grid-cols-[180px_1fr]">
        <div className="font-mono text-[10.5px] uppercase tracking-eyebrow text-ink-soft md:text-right">
          Reasoning<br />
          <span className="normal-case tracking-normal text-ink-dim">배치 근거</span>
        </div>
        <p className="text-[16.5px] leading-[1.75] text-ink">
          {result.reasoning}
        </p>
      </div>

      {/* Stack + Alternatives */}
      <div className="mt-14 grid grid-cols-1 gap-x-10 gap-y-10 border-t border-line pt-8 md:grid-cols-2">
        <SubBlock title="권장 구현 스택" eyebrow="Stack" items={result.stack} />
        <SubBlock
          title="대안 플랫폼 검토"
          eyebrow="Alternatives"
          items={result.alternatives}
        />
      </div>

      {/* Warnings */}
      {result.warnings.length > 0 && (
        <div className="mt-12">
          <div className="mb-4 flex items-baseline gap-3 border-b border-accent pb-2">
            <span className="font-mono text-[11px] uppercase tracking-eyebrow text-accent">
              Warnings
            </span>
            <span className="text-[16px] font-semibold text-ink">유의 사항</span>
          </div>
          <ul className="space-y-3">
            {result.warnings.map((w, i) => (
              <li
                key={i}
                className="flex gap-4 border-l-[3px] border-accent bg-accent-soft/60 px-5 py-3"
              >
                <span className="font-mono text-[11px] font-medium uppercase tracking-eyebrow text-accent">
                  0{i + 1}
                </span>
                <span className="text-[14.5px] leading-relaxed text-ink">{w}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}

function SubBlock({
  title,
  eyebrow,
  items,
}: {
  title: string;
  eyebrow: string;
  items: string[];
}) {
  return (
    <div>
      <div className="mb-3 flex items-baseline justify-between border-b border-line pb-1.5">
        <h4 className="text-[16px] font-bold tracking-tight text-ink">{title}</h4>
        <span className="font-mono text-[10.5px] uppercase tracking-eyebrow text-ink-dim">
          {eyebrow}
        </span>
      </div>
      <ul className="space-y-2.5">
        {items.length === 0 && (
          <li className="text-[14px] text-ink-dim">— 없음</li>
        )}
        {items.map((it, i) => (
          <li key={i} className="flex gap-3 text-[15px] leading-relaxed text-ink">
            <span className="mt-1 font-mono text-[11px] font-medium text-ink-dim">
              {String(i + 1).padStart(2, "0")}
            </span>
            <span>{it}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
