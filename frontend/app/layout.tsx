import "./globals.css";
import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Agent Router — 4 Pillar Routing",
  description: "4 Pillar Agent 플랫폼 라우팅 결정 시스템",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body className="min-h-screen bg-paper text-ink">
        <header className="border-b border-line bg-paper">
          <div className="mx-auto flex max-w-[1180px] items-center justify-between px-8 py-4">
            <Link href="/" className="flex items-baseline gap-3">
              <span className="grid h-7 w-7 place-items-center bg-ink font-mono text-[11px] font-semibold tracking-tight text-paper">
                AR
              </span>
              <span className="text-[17px] font-semibold tracking-tight text-ink">
                Agent Router
              </span>
              <span className="hidden font-mono text-[11px] uppercase tracking-eyebrow text-ink-dim md:inline">
                4 Pillar
              </span>
            </Link>

            <nav className="flex items-center gap-1 text-[14px]">
              <NavLink href="/">라우팅</NavLink>
              <NavLink href="/tickets">이력</NavLink>
              <NavLink href="/platforms">플랫폼 가이드</NavLink>
            </nav>
          </div>
        </header>

        <main>{children}</main>

        <footer className="mt-20 border-t border-line">
          <div className="mx-auto flex max-w-[1180px] flex-col gap-2 px-8 py-5 text-[12px] md:flex-row md:items-center md:justify-between">
            <div className="font-mono uppercase tracking-eyebrow text-ink-soft">
              AgentPlatform · 4 Pillar Federated Router
            </div>
            <div className="text-ink-dim">
              Personal Agent 기술팀 · CTO Office
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}

function NavLink({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <Link
      href={href}
      className="px-3 py-1.5 font-medium text-ink-soft transition hover:text-ink"
    >
      {children}
    </Link>
  );
}
