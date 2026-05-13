import { api } from "@/lib/api";
import { PlatformCode } from "@/lib/api";

export const dynamic = "force-dynamic";

const DARK: Record<PlatformCode, string> = {
  palantir: "#0A7A63",
  copilot:  "#185793",
  custom:   "#8A4F00",
  ixi:      "#5F2890",
};

const TINT: Record<PlatformCode, string> = {
  palantir: "#F0F7F4",
  copilot:  "#F0F5FA",
  custom:   "#F8F2E6",
  ixi:      "#F5EFFA",
};

export default async function PlatformsPage() {
  let platforms;
  let err: string | null = null;
  try {
    platforms = await api.platforms();
  } catch (e: any) {
    err = e.message || "플랫폼 정보를 불러오지 못했습니다.";
    platforms = [];
  }

  return (
    <div className="mx-auto max-w-[1180px] px-8 pt-12 pb-8">
      <header className="mb-10">
        <div className="font-mono text-[11px] uppercase tracking-eyebrow text-ink-soft">
          Reference
        </div>
        <h1 className="mt-3 text-[36px] font-bold leading-tight tracking-tight text-ink md:text-[44px]">
          플랫폼 가이드
        </h1>
        <div className="mt-5 grid grid-cols-1 gap-x-12 gap-y-3 md:grid-cols-[1fr_auto]">
          <p className="max-w-[68ch] text-[16px] leading-[1.65] text-ink-soft">
            라우팅 결정의 기반이 되는 4개 플랫폼. 각 플랫폼은 강점과 회피 영역이 뚜렷합니다.
            상세 룰북은{" "}
            <code className="bg-paper-sub px-1.5 py-0.5 font-mono text-[13px] text-ink">
              docs/PLATFORMS.md
            </code>
            에 있습니다.
          </p>
        </div>
      </header>

      <div className="rule-heavy mb-14" />

      {err && (
        <div className="mb-8 flex items-start gap-3 border-l-[3px] border-accent bg-accent-soft px-5 py-3 text-[14px] text-accent-hov">
          <span className="font-mono text-[11px] uppercase tracking-eyebrow text-accent">Error</span>
          <span>{err}</span>
        </div>
      )}

      <div className="space-y-20">
        {platforms.map((p, i) => (
          <PlatformChapter key={p.code} platform={p} index={i} />
        ))}
      </div>
    </div>
  );
}

type Platform = {
  code: PlatformCode;
  name: string;
  tag: string;
  one_liner: string;
  strengths: string[];
  weaknesses: string[];
  color: string;
};

function PlatformChapter({
  platform: p,
  index,
}: {
  platform: Platform;
  index: number;
}) {
  const color = DARK[p.code];
  const tint = TINT[p.code];
  const flipped = index % 2 === 1;

  return (
    <article>
      <div className="grid grid-cols-1 gap-x-10 gap-y-6 md:grid-cols-12">
        <div
          className={
            "md:col-span-3 " +
            (flipped ? "md:order-last md:text-right" : "")
          }
        >
          <div
            className="font-mono text-[10.5px] uppercase tracking-eyebrow"
            style={{ color }}
          >
            Pillar No. {String(index + 1).padStart(2, "0")}
          </div>
          <div
            className="mt-3 text-[88px] font-bold leading-[0.9] tracking-[-0.04em] md:text-[112px]"
            style={{ color }}
          >
            {String(index + 1).padStart(2, "0")}
          </div>
          <div
            className="mt-4 h-[4px] w-[72px]"
            style={{
              background: color,
              marginLeft: flipped ? "auto" : 0,
            }}
          />
          <div className="mt-3 font-mono text-[11px] uppercase tracking-eyebrow text-ink-soft">
            {p.tag}
          </div>
        </div>

        <div className="md:col-span-9">
          <h2
            className="text-[36px] font-bold leading-[1.05] tracking-tight md:text-[44px]"
            style={{ color }}
          >
            {p.name}
          </h2>

          <p className="mt-4 max-w-[60ch] text-[17px] leading-[1.6] text-ink-soft">
            {p.one_liner}
          </p>

          <div
            className="mt-7 grid grid-cols-1 gap-x-10 gap-y-7 px-6 py-6 md:grid-cols-2"
            style={{ background: tint }}
          >
            <div>
              <div className="mb-3 flex items-baseline gap-2 border-b border-ink/20 pb-1.5">
                <span
                  className="font-mono text-[10.5px] uppercase tracking-eyebrow"
                  style={{ color }}
                >
                  ✓ Strengths
                </span>
                <span className="text-[14px] font-semibold text-ink">
                  강점 도메인
                </span>
              </div>
              <ul className="space-y-2">
                {p.strengths.map((s, j) => (
                  <li
                    key={j}
                    className="flex gap-3 text-[15px] leading-relaxed text-ink"
                  >
                    <span
                      className="mt-1 font-mono text-[11px] font-medium"
                      style={{ color }}
                    >
                      {String(j + 1).padStart(2, "0")}
                    </span>
                    <span>{s}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <div className="mb-3 flex items-baseline gap-2 border-b border-ink/20 pb-1.5">
                <span className="font-mono text-[10.5px] uppercase tracking-eyebrow text-accent">
                  ✗ Avoid
                </span>
                <span className="text-[14px] font-semibold text-ink">
                  약점 / 회피 영역
                </span>
              </div>
              <ul className="space-y-2">
                {p.weaknesses.map((w, j) => (
                  <li
                    key={j}
                    className="flex gap-3 text-[15px] leading-relaxed text-ink-soft"
                  >
                    <span className="mt-1 font-mono text-[11px] font-medium text-accent">
                      {String(j + 1).padStart(2, "0")}
                    </span>
                    <span>{w}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>

      {index < 3 && <div className="mt-14 rule-heavy" />}
    </article>
  );
}
