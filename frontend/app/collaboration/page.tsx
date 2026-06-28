"use client";

import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, MessageSquare, Send } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/input";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";

export default function CollaborationPage() {
  const { token, workspace } = useAuthStore();
  const queryClient = useQueryClient();
  const [body, setBody] = useState("@finance Please review this dashboard before publishing.");
  const comments = useQuery({ queryKey: ["comments", token, workspace?.id], queryFn: () => api.comments(token as string, workspace?.id as string), enabled: Boolean(token && workspace?.id) });
  const activity = useQuery({ queryKey: ["activity", token, workspace?.id], queryFn: () => api.activityFeed(token as string, workspace?.id as string), enabled: Boolean(token && workspace?.id) });
  const approvals = useQuery({ queryKey: ["approvals", token, workspace?.id], queryFn: () => api.approvals(token as string, workspace?.id as string), enabled: Boolean(token && workspace?.id) });
  const createComment = useMutation({
    mutationFn: () => api.createComment(token as string, { workspace_id: workspace?.id, target_type: "dashboard", target_id: "workspace-home", body, mentions: ["finance"] }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["comments"] });
      queryClient.invalidateQueries({ queryKey: ["activity"] });
    }
  });
  const requestApproval = useMutation({
    mutationFn: () => api.requestApproval(token as string, { workspace_id: workspace?.id, target_type: "dashboard", target_id: "workspace-home", action: "publish_dashboard", requested_reason: "Publish executive dashboard" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["approvals"] });
      queryClient.invalidateQueries({ queryKey: ["activity"] });
    }
  });

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    createComment.mutate();
  }

  return (
    <AppShell title="Collaboration">
      <div className="grid gap-4 xl:grid-cols-[0.9fr_1.1fr]">
        <Card>
          <CardHeader><CardTitle>Comments and approvals</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <form className="space-y-3" onSubmit={submit}>
              <Textarea value={body} onChange={(event) => setBody(event.target.value)} />
              <Button type="submit" disabled={createComment.isPending}><MessageSquare size={16} /> Add comment</Button>
            </form>
            <Button variant="secondary" onClick={() => requestApproval.mutate()} disabled={requestApproval.isPending}><CheckCircle2 size={16} /> Request publish approval</Button>
          </CardContent>
        </Card>
        <div className="space-y-4">
          <Card>
            <CardHeader><CardTitle>Workspace comments</CardTitle></CardHeader>
            <CardContent className="space-y-2">
              {(comments.data ?? []).map((comment) => <div key={String(comment.id)} className="rounded-md border border-line p-3 text-sm">{String(comment.body)}</div>)}
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Approvals</CardTitle></CardHeader>
            <CardContent className="flex flex-wrap gap-2">
              {(approvals.data ?? []).map((approval) => <Badge key={String(approval.id)}>{String(approval.action)}: {String(approval.status)}</Badge>)}
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Activity feed</CardTitle></CardHeader>
            <CardContent className="space-y-2">
              {(activity.data ?? []).slice(0, 8).map((item) => <div key={String(item.id)} className="flex items-center gap-2 text-sm text-muted"><Send size={14} /> {String(item.action)} {String(item.entity_type)}</div>)}
            </CardContent>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
