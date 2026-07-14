import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        display: ["var(--font-fraunces)", "Georgia", "serif"],
        body: ["var(--font-plex-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-plex-mono)", "ui-monospace", "monospace"],
      },
      colors: {
        ink: {
          950: "#12141A",
          900: "#181B22",
          800: "#22262F",
          700: "#343A47",
        },
        manuscript: "#EDE7D6",
        redline: {
          DEFAULT: "#B23A2E",
          soft: "#D9B9AE",
        },
      },
    },
  },
  plugins: [],
};

export default config;
