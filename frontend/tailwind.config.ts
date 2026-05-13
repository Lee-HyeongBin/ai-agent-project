import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        paper:         "#FFFFFF",
        "paper-soft":  "#FAFAFA",
        "paper-sub":   "#F4F4F5",
        ink:           "#171717",
        "ink-soft":    "#3F3F3F",
        "ink-dim":     "#5B5B5B",
        line:          "#E5E5E5",
        "line-soft":   "#EFEFEF",
        "line-strong": "#BFBFBF",

        accent:        "#7A1F2B",
        "accent-soft": "#F5E8EA",
        "accent-hov":  "#5C1620",

        teal:    "#0A7A63",
        blue1:   "#185793",
        amber1:  "#8A4F00",
        purple1: "#5F2890",
      },
      fontFamily: {
        sans: ['"Noto Sans KR"', '"Noto Sans"', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['"JetBrains Mono"', '"IBM Plex Mono"', 'ui-monospace', 'monospace'],
      },
      letterSpacing: {
        eyebrow: '0.18em',
      },
    },
  },
  plugins: [],
};

export default config;
