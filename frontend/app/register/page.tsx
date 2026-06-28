"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

export default function RegisterPage() {
  const router = useRouter();
  const setSession = useAuthStore((state) => state.setSession);
  const [message, setMessage] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setMessage("Creating workspace...");
    try {
      const session = await api.register(String(form.get("email")), String(form.get("full_name")), String(form.get("password")));
      setSession(session.access_token, session.user);
      router.push("/dashboard");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Registration failed");
    }
  }

  return (
    <main className="grid min-h-screen place-items-center bg-surface px-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Create InsightAI workspace</CardTitle>
          <p className="text-sm text-muted">JWT auth and RBAC are enabled from the first account.</p>
        </CardHeader>
        <CardContent>
          <form className="space-y-4" onSubmit={submit}>
            <Input name="full_name" placeholder="Full name" required />
            <Input name="email" placeholder="Email" required type="email" />
            <Input name="password" placeholder="Password" required type="password" minLength={8} />
            <Button className="w-full" type="submit">Create account</Button>
          </form>
          {message && <p className="mt-4 text-sm text-muted">{message}</p>}
          <p className="mt-5 text-sm text-muted">Already have an account? <Link className="font-medium text-ink" href="/login">Login</Link></p>
        </CardContent>
      </Card>
    </main>
  );
}
