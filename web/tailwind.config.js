/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{vue,ts}"],
  theme: {
    extend: {
      fontFamily: {
        mono: ["Geist Mono", "JetBrains Mono", "ui-monospace", "monospace"],
      },
      colors: {
        bg: "#0A0A0A",
        surface: "#141414",
        "surface-2": "#1C1C1C",
        border: "#2A2A2A",
        "border-strong": "#3F3F3F",
        "text-primary": "#F5F5F5",
        "text-muted": "#A1A1A1",
        "text-dim": "#6B6B6B",
        accent: "#A3E635",
        "accent-dim": "#65A30D",
        danger: "#F87171",
      },
      borderRadius: { DEFAULT: "2px" },
      fontSize: {
        xs: ["11px", "1.45"],
        sm: ["12px", "1.45"],
        base: ["13px", "1.45"],
        lg: ["15px", "1.4"],
        xl: ["18px", "1.3"],
      },
    },
  },
  plugins: [],
};
