import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        base: "#0A0B10",
        surface: "#12141C",
        surface2: "#191C27",
        line: "#262A38",
        ink: "#EDEAE3",
        "ink-dim": "#9B9CAA",
        ember: "#FF6B45",
        "ember-dim": "#3A2119",
        chill: "#4FD1C5",
        "chill-dim": "#173330",
        amber: "#F2B84B",
      },
      fontFamily: {
        display: ["var(--font-display)", "serif"],
        mono: ["var(--font-mono)", "monospace"],
        sans: ["var(--font-sans)", "sans-serif"],
      },
    },
  },
  plugins: [],
};
export default config;
