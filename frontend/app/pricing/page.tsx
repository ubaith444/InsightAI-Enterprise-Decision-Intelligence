import Link from "next/link";
import { BarChart3, Check } from "lucide-react";
import { Button } from "@/components/ui/button";

const plans = [
  { name: "Starter", price: "$49", features: ["Demo workspace", "Saved prompts", "CSV exports"] },
  { name: "Business", price: "$199", features: ["Multi-agent AI", "Scheduled reports", "Workspace RBAC"] },
  { name: "Enterprise", price: "Custom", features: ["Private deployment", "Advanced governance", "Custom connectors"] }
];

export default function PricingPage() {
  return (
    <main className="min-h-screen bg-white">
      <header className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
        <Link href="/" className="flex items-center gap-3">
          <div className="grid size-9 place-items-center rounded-md bg-ink text-white"><BarChart3 size={18} /></div>
          <span className="font-semibold">InsightAI</span>
        </Link>
        <Link href="/register"><Button size="sm">Start workspace</Button></Link>
      </header>
      <section className="mx-auto max-w-7xl px-6 py-16">
        <h1 className="text-5xl font-semibold">Pricing</h1>
        <p className="mt-4 max-w-2xl text-muted">Plans for teams that need safe AI analytics, governed data access, and executive-ready reporting.</p>
        <div className="mt-10 grid gap-4 md:grid-cols-3">
          {plans.map((plan) => (
            <div key={plan.name} className="rounded-md border border-line p-6">
              <div className="text-lg font-semibold">{plan.name}</div>
              <div className="mt-4 text-3xl font-semibold">{plan.price}</div>
              <ul className="mt-6 space-y-3 text-sm text-muted">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-center gap-2"><Check size={15} className="text-mint" /> {feature}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
