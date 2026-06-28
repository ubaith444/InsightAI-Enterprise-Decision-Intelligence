"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { BarChart3 } from "lucide-react";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

export default function LoginPage() {
  const router = useRouter();
  const setSession = useAuthStore((state) => state.setSession);
  const [email, setEmail] = useState("admin@insightai.ai");
  const [password, setPassword] = useState("InsightAI123");
  const [message, setMessage] = useState("");

  async function submit(event: FormEvent) {
    event.preventDefault();
    setMessage("Signing in...");
    try {
      const session = await api.login(email, password);
      setSession(session.access_token, session.user);
      router.push("/dashboard");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Login failed");
    }
  }

  return (
    <main className="grid min-h-screen place-items-center bg-surface px-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <div className="mb-3 grid size-10 place-items-center rounded-md bg-ink text-white"><BarChart3 size={18} /></div>
          <CardTitle>Login to InsightAI</CardTitle>
          <p className="text-sm text-muted">Demo credentials are prefilled after the backend seed runs.</p>
        </CardHeader>
        <CardContent>
          <form className="space-y-4" onSubmit={submit}>
            <Input value={email} onChange={(event) => setEmail(event.target.value)} placeholder="Email" type="email" />
            <Input value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Password" type="password" />
            <Button className="w-full" type="submit">Login</Button>
            <Button className="w-full" variant="secondary" type="button" onClick={() => setMessage("Google login placeholder: connect OAuth credentials in production settings.")}>Google login placeholder</Button>
          </form>
          {message && <p className="mt-4 text-sm text-muted">{message}</p>}
          <p className="mt-5 text-sm text-muted">No workspace yet? <Link className="font-medium text-ink" href="/register">Create account</Link></p>
        </CardContent>
      </Card>
    </main>
  );
}
