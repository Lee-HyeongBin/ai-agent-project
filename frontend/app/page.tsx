import { RouteForm } from "@/components/RouteForm";

const LEGEND = [
  { code: "palantir", name: "Palantir AIP",      tag: "데이터·운영 분석", color: "#0A7A63" },
  { code: "copilot",  name: "MS Copilot Studio", tag: "생산성·협업",     color: "#185793" },
  { code: "custom",   name: "Custom Agent",      tag: "Legacy·보안",     color: "#8A4F00" },
  { code: "ixi",      name: "ixi-Enterprise",    tag: "내부 업무·지식",   color: "#5F2890" },
];

export default function Home() {
  return (
    <div className="mx-auto max-w-[1180px] px-8 pt-12 pb-8">
      <header className="mb-12">
        <div className="font-mono text-[11px] uppercase tracking-eyebrow text-ink-soft">
          Routing
        </div>
        <h1 className="mt-3 text-[40px] font-bold leading-[1.15] tracking-tight text-ink md:text-[48px]">
          Work Agent Router
        </h1>
        <p className="mt-5 text-[17px] leading-[1.65] text-ink-soft">
          Agent 과제의 목적·도메인·연동 시스템·보안 민감도·사용자 규모를 입력하면,
          룰북과 LLM이 함께 4 Pillar 플랫폼 중 최적 배치를 분석하고 자연어 근거를 제시합니다.
          결정은 모두 영구 보관되어 사후 검토와 감사가 가능합니다.
        </p>
      </header>

      <section className="mb-10 border-y border-line py-6">
        <div className="mb-4 font-mono text-[11px] uppercase tracking-eyebrow text-ink-soft">
          4 Pillar Platforms
        </div>
        <div className="grid grid-cols-2 gap-y-4 md:grid-cols-4 md:gap-x-8">
          {LEGEND.map((p, i) => (
            <div key={p.code} className="flex items-baseline gap-3">
              <span className="font-mono text-[12px] font-medium text-ink-dim">
                0{i + 1}
              </span>
              <div>
                <div
                  className="text-[15px] font-semibold leading-tight"
                  style={{ color: p.color }}
                >
                  {p.name}
                </div>
                <div className="mt-1 font-mono text-[10.5px] uppercase tracking-eyebrow text-ink-dim">
                  {p.tag}
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      <RouteForm />
    </div>
  );
}
