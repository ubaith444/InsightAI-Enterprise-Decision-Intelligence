import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#101113",
        muted: "#667085",
        line: "#E5E7EB",
        surface: "#F7F8FA",
        brand: "#0B5FFF",
        mint: "#12B886",
        amber: "#F59E0B",
        rose: "#E11D48"
      },
      boxShadow: {
        premium: "0 20px 70px rgba(16, 17, 19, 0.12)"
      }
    }
  },
  plugins: []
};

export default config;
