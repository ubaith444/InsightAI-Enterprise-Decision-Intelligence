"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Activity, BarChart3, Bot, CreditCard, Database, FileSearch, FileText, GitBranch, History, Home, KeyRound, LayoutDashboard, LogOut, MessageSquare, PlugZap, Settings, ShieldCheck, TableProperties, Users } from "lucide-react";
import { ReactNode, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const nav = [
  { href: "/dashboard", label: "Home", icon: Home },
  { href: "/chat", label: "AI Chat", icon: Bot },
  { href: "/connections", label: "Connections", icon: Database },
  { href: "/integrations", label: "Integrations", icon: PlugZap },
  { href: "/schema", label: "Schema", icon: TableProperties },
  { href: "/knowledge", label: "Knowledge", icon: FileSearch },
  { href: "/semantic", label: "Semantic", icon: TableProperties },
  { href: "/lineage", label: "Lineage", icon: GitBranch },
  { href: "/realtime", label: "Realtime", icon: Activity },
  { href: "/history", label: "History", icon: History },
  { href: "/dashboards", label: "Dashboards", icon: LayoutDashboard },
  { href: "/reports", label: "Reports", icon: FileText },
  { href: "/billing", label: "Billing", icon: CreditCard },
  { href: "/api-keys", label: "API Keys", icon: KeyRound },
  { href: "/team", label: "Team", icon: Users },
  { href: "/collaboration", label: "Collaboration", icon: MessageSquare },
  { href: "/admin/agents", label: "Agents", icon: Bot, adminOnly: true },
  { href: "/admin", label: "Admin", icon: ShieldCheck, adminOnly: true },
  { href: "/settings", label: "Settings", icon: Settings }
];

const isAdminRole = (role?: string) => role === "Admin" || role === "Super Admin";

export function AppShell({ children, title, actions }: { children: ReactNode; title: string; actions?: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { token, user, workspace, setSession, setWorkspace, logout } = useAuthStore();

  const me = useQuery({
    queryKey: ["me", token],
    queryFn: () => api.me(token as string),
    enabled: Boolean(token && !user)
  });
  const workspaces = useQuery({
    queryKey: ["workspaces", token],
    queryFn: () => api.workspaces(token as string),
    enabled: Boolean(token)
  });

  useEffect(() => {
    if (me.data && token) setSession(token, me.data);
  }, [me.data, setSession, token]);

  useEffect(() => {
    if (!workspace && workspaces.data?.[0]) setWorkspace(workspaces.data[0]);
  }, [setWorkspace, workspace, workspaces.data]);

  useEffect(() => {
    if (!token) router.push("/login");
  }, [router, token]);

  return (
    <div className="min-h-screen bg-surface">
      <aside className="fixed inset-y-0 left-0 z-20 hidden w-64 border-r border-line bg-white lg:block">
        <div className="flex h-16 items-center gap-3 border-b border-line px-5">
          <div className="grid size-9 place-items-center rounded-md bg-ink text-white">
            <BarChart3 size={18} />
          </div>
          <div>
            <div className="font-semibold">InsightAI</div>
            <div className="text-xs text-muted">BI Copilot</div>
          </div>
        </div>
        <nav className="space-y-1 p-3">
          {nav.filter((item) => !item.adminOnly || isAdminRole(user?.role)).map((item) => {
            const Icon = item.icon;
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn("flex h-10 items-center gap-3 rounded-md px-3 text-sm text-muted hover:bg-surface hover:text-ink", active && "bg-surface text-ink")}
              >
                <Icon size={16} />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </aside>
      <main className="lg:pl-64">
        <header className="sticky top-0 z-10 flex min-h-16 items-center justify-between border-b border-line bg-white/90 px-4 backdrop-blur lg:px-8">
          <div>
            <div className="text-xs text-muted">{workspace?.name ?? "Loading workspace"} / {title}</div>
            <h1 className="text-lg font-semibold">{title}</h1>
          </div>
          <div className="flex items-center gap-3">
            <div className="hidden rounded-md border border-line bg-surface px-3 py-2 text-xs text-muted md:block">Command menu: Ask, connect, report</div>
            {actions}
            <Badge>{user?.role ?? "Session"}</Badge>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                logout();
                router.push("/login");
              }}
              title="Sign out"
            >
              <LogOut size={15} />
            </Button>
          </div>
        </header>
        <nav className="flex gap-2 overflow-x-auto border-b border-line bg-white px-4 py-2 lg:hidden">
          {nav.filter((item) => !item.adminOnly || isAdminRole(user?.role)).map((item) => (
            <Link key={item.href} href={item.href} className={cn("whitespace-nowrap rounded-md px-3 py-2 text-sm text-muted", pathname === item.href && "bg-surface text-ink")}>{item.label}</Link>
          ))}
        </nav>
        <div className="p-4 lg:p-8">{children}</div>
      </main>
    </div>
  );
}
