"use client";

import { create } from "zustand";
import type { User, Workspace } from "@/types";

type AuthState = {
  token: string | null;
  user: User | null;
  workspace: Workspace | null;
  setSession: (token: string, user: User) => void;
  setWorkspace: (workspace: Workspace) => void;
  logout: () => void;
};

export const useAuthStore = create<AuthState>((set) => ({
  token: typeof window !== "undefined" ? window.localStorage.getItem("insightai_token") : null,
  user: null,
  workspace: null,
  setSession: (token, user) => {
    window.localStorage.setItem("insightai_token", token);
    set({ token, user });
  },
  setWorkspace: (workspace) => set({ workspace }),
  logout: () => {
    window.localStorage.removeItem("insightai_token");
    set({ token: null, user: null, workspace: null });
  }
}));
