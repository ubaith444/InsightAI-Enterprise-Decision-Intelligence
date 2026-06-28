"use client";

import { FormEvent, useState } from "react";
import { FileSearch, Plus } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input, Select, Textarea } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";

const documentTypes = ["pdf", "sop", "policy", "contract", "meeting_note"];

export default function KnowledgePage() {
  const { token, workspace } = useAuthStore();
  const [query, setQuery] = useState("revenue drop policy meeting notes");
  const [title, setTitle] = useState("Customer Renewal SOP");
  const [documentType, setDocumentType] = useState("sop");
  const [content, setContent] = useState("Renewal risk is reviewed weekly with account owners, contract terms, and executive meeting notes.");
  const [results, setResults] = useState<Record<string, unknown>[]>([]);
  const [message, setMessage] = useState("");
  const docs = useQuery({ queryKey: ["knowledge-documents", token, workspace?.id], queryFn: () => api.knowledgeDocuments(token as string, workspace?.id as string), enabled: Boolean(token && workspace?.id) });

  async function search(event: FormEvent) {
    event.preventDefault();
    if (!token || !workspace) return;
    const response = await api.searchKnowledge(token, { workspace_id: workspace.id, query, document_types: documentTypes, limit: 5 });
    setResults(response.results);
    setMessage(`${response.results.length} knowledge results found.`);
  }

  async function addDocument(event: FormEvent) {
    event.preventDefault();
    if (!token || !workspace) return;
    await api.createKnowledgeDocument(token, { workspace_id: workspace.id, title, document_type: documentType, content, tags: [documentType] });
    setMessage("Knowledge document added.");
    docs.refetch();
  }

  return (
    <AppShell title="Knowledge Search">
      <div className="grid gap-4 xl:grid-cols-[0.9fr_1.1fr]">
        <Card>
          <CardHeader><CardTitle>Search RAG Knowledge</CardTitle></CardHeader>
          <CardContent>
            <form className="space-y-3" onSubmit={search}>
              <Input value={query} onChange={(event) => setQuery(event.target.value)} />
              <div className="flex flex-wrap gap-2">
                {documentTypes.map((type) => <Badge key={type}>{type}</Badge>)}
              </div>
              <Button type="submit"><FileSearch size={16} /> Search knowledge</Button>
            </form>
            {message && <p className="mt-3 text-sm text-muted">{message}</p>}
            <div className="mt-4 space-y-3">
              {results.map((item) => (
                <div key={String(item.id)} className="rounded-md border border-line p-3">
                  <div className="flex items-center justify-between gap-3">
                    <div className="font-medium">{String(item.title)}</div>
                    <Badge>{String(item.document_type)}</Badge>
                  </div>
                  <p className="mt-2 text-sm text-muted">{String(item.summary)}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Knowledge Library</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <form className="space-y-3" onSubmit={addDocument}>
              <Input value={title} onChange={(event) => setTitle(event.target.value)} />
              <Select value={documentType} onChange={(event) => setDocumentType(event.target.value)}>
                {documentTypes.map((type) => <option key={type} value={type}>{type}</option>)}
              </Select>
              <Textarea value={content} onChange={(event) => setContent(event.target.value)} />
              <Button type="submit" variant="secondary"><Plus size={16} /> Add document</Button>
            </form>
            <div className="space-y-3">
              {(docs.data ?? []).slice(0, 8).map((item) => (
                <div className="rounded-md border border-line p-3" key={String(item.id)}>
                  <div className="font-medium">{String(item.title ?? item.name)}</div>
                  <div className="mt-1 text-xs text-muted">{String(item.document_type ?? "document")}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
