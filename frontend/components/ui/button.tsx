import { ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost" | "danger";
  size?: "sm" | "md";
};

export function Button({ className, variant = "primary", size = "md", ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-md border font-medium transition disabled:cursor-not-allowed disabled:opacity-50",
        size === "sm" ? "h-8 px-3 text-xs" : "h-10 px-4 text-sm",
        variant === "primary" && "border-ink bg-ink text-white hover:bg-black",
        variant === "secondary" && "border-line bg-white text-ink hover:bg-surface",
        variant === "ghost" && "border-transparent bg-transparent text-ink hover:bg-surface",
        variant === "danger" && "border-rose bg-rose text-white hover:bg-red-700",
        className
      )}
      {...props}
    />
  );
}
