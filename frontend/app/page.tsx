import Link from "next/link";
import { ArrowRight, BarChart3, Bot, Database, Lock, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-white">
      <header className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
        <div className="flex items-center gap-3">
          <div className="grid size-9 place-items-center rounded-md bg-ink text-white">
            <BarChart3 size={18} />
          </div>
          <div className="font-semibold">InsightAI</div>
        </div>
        <div className="flex items-center gap-3">
          <Link href="/login" className="text-sm text-muted hover:text-ink">Login</Link>
          <Link href="/register"><Button size="sm">Start workspace <ArrowRight size={14} /></Button></Link>
        </div>
      </header>
      <section className="mx-auto grid max-w-7xl grid-cols-1 gap-10 px-6 py-12 lg:grid-cols-[0.9fr_1.1fr] lg:py-20">
        <div className="flex flex-col justify-center">
          <div className="mb-5 inline-flex w-fit items-center rounded-md border border-line bg-surface px-3 py-1 text-sm text-muted">AI-Powered Business Intelligence Copilot</div>
          <h1 className="text-5xl font-semibold leading-tight text-ink lg:text-6xl">InsightAI</h1>
          <p className="mt-5 max-w-xl text-lg leading-8 text-muted">
            Connect business data, ask questions in plain English, generate safe SQL or MongoDB queries, build dashboards, and ship executive-ready insights.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link href="/login"><Button>Open product <ArrowRight size={16} /></Button></Link>
            <Link href="/dashboard"><Button variant="secondary">View dashboard</Button></Link>
          </div>
        </div>
        <div className="rounded-lg border border-line bg-white p-4 shadow-premium">
          <div className="mb-4 flex items-center justify-between border-b border-line pb-3">
            <div>
              <div className="text-sm font-semibold">Revenue Intelligence</div>
              <div className="text-xs text-muted">Live workspace preview</div>
            </div>
            <div className="rounded-md bg-mint/10 px-2 py-1 text-xs font-medium text-mint">Read-only safe</div>
          </div>
          <div className="grid gap-3 md:grid-cols-3">
            {["$1.38M Revenue", "+14.2% Growth", "3 Risks"].map((item) => (
              <div key={item} className="rounded-md border border-line p-3 text-sm font-semibold">{item}</div>
            ))}
          </div>
          <div className="mt-4 grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
            <div className="h-64 rounded-md border border-line p-4">
              <div className="mb-4 flex h-full items-end gap-3">
                {[42, 58, 64, 52, 76, 88].map((height, index) => (
                  <div key={index} className="flex flex-1 items-end rounded-md bg-brand/10">
                    <div className="w-full rounded-md bg-brand" style={{ height: `${height}%` }} />
                  </div>
                ))}
              </div>
            </div>
            <div className="space-y-3">
              {[Bot, Database, ShieldCheck].map((Icon, index) => (
                <div key={index} className="flex items-center gap-3 rounded-md border border-line p-3">
                  <Icon size={18} className="text-brand" />
                  <div>
                    <div className="text-sm font-medium">{["Ask questions", "Inspect schema", "Validate queries"][index]}</div>
                    <div className="text-xs text-muted">{["Plain-English analytics", "Postgres and MongoDB ready", "Blocks write operations"][index]}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
      <section className="border-t border-line bg-surface py-16">
        <div className="mx-auto grid max-w-7xl gap-4 px-6 md:grid-cols-4">
          {["Features", "How it works", "Use cases", "Security"].map((title, index) => (
            <div key={title} className="rounded-md border border-line bg-white p-5">
              <div className="font-semibold">{title}</div>
              <p className="mt-2 text-sm leading-6 text-muted">
                {[
                  "Ask AI questions, validate safe queries, generate charts, dashboards, reports, exports, and alerts.",
                  "Connect a workspace database, inspect schema, ask a question, review confidence, then save the answer.",
                  "Sales, customer success, finance, operations, inventory, and executive reporting workflows.",
                  "RBAC, workspace isolation, encrypted connection strings, audit logs, query safety, and rate limits."
                ][index]}
              </p>
            </div>
          ))}
        </div>
      </section>
      <section className="mx-auto grid max-w-7xl gap-8 px-6 py-16 lg:grid-cols-[0.8fr_1.2fr]">
        <div>
          <h2 className="text-3xl font-semibold">Demo dashboard preview</h2>
          <p className="mt-3 text-muted">A preloaded workspace includes sales, customers, products, orders, employees, regions, expenses, and inventory datasets.</p>
          <div className="mt-6 flex gap-3">
            <Link href="/pricing"><Button variant="secondary">Pricing</Button></Link>
            <Link href="/register"><Button>Try demo</Button></Link>
          </div>
        </div>
        <div className="grid gap-3 md:grid-cols-3">
          {["Revenue trend", "Regional performance", "Low inventory"].map((item) => (
            <div key={item} className="rounded-md border border-line p-4">
              <div className="text-sm font-medium">{item}</div>
              <div className="mt-4 h-24 rounded-md bg-brand/10" />
            </div>
          ))}
        </div>
      </section>
      <section className="border-t border-line py-16">
        <div className="mx-auto grid max-w-7xl gap-6 px-6 md:grid-cols-2">
          <div>
            <h2 className="text-3xl font-semibold">FAQ</h2>
            {["Does InsightAI execute write queries?", "Can I use mock AI locally?", "Is this multi-tenant?"].map((q) => (
              <div key={q} className="mt-4 rounded-md border border-line p-4">
                <div className="font-medium">{q}</div>
                <div className="mt-2 text-sm text-muted">InsightAI is built for read-only governed analytics, deterministic local fallback, and workspace-scoped data isolation.</div>
              </div>
            ))}
          </div>
          <div className="rounded-md bg-ink p-8 text-white">
            <Lock size={24} />
            <h2 className="mt-4 text-3xl font-semibold">Build governed AI analytics.</h2>
            <p className="mt-3 text-white/70">Launch a demo workspace with prebuilt dashboards, reports, saved prompts, and multi-agent query governance.</p>
            <Link href="/register" className="mt-6 inline-flex"><Button>Start workspace <ArrowRight size={16} /></Button></Link>
          </div>
        </div>
      </section>
    </main>
  );
}
