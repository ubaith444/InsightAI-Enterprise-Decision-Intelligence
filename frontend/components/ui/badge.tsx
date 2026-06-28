import { HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

export function Badge({ className, ...props }: HTMLAttributes<HTMLSpanElement>) {
  return <span className={cn("inline-flex items-center rounded-md border border-line bg-surface px-2 py-1 text-xs font-medium text-muted", className)} {...props} />;
}
