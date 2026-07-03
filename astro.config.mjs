// @ts-check
import { defineConfig } from "astro/config";
import tailwindcss from "@tailwindcss/vite";
import svelte from "@astrojs/svelte";
import mdx from "@astrojs/mdx";
import sitemap from "@astrojs/sitemap";
import { siteUrl } from "./src/data/site.json";

const markdownParserTarget =
  process.env.MARKDOWN_PARSER_TARGET ?? "http://127.0.0.1:8000";

// https://astro.build/config
export default defineConfig({
  vite: {
    plugins: [tailwindcss()],
    server: {
      // The Markdown parser API only allows the production origin via CORS,
      // so during local dev we proxy requests through the dev server
      // (same-origin) to avoid the browser blocking them. By default this
      // points at the local parser repo so parser changes can be tested here.
      proxy: {
        "/api/markdown-parse": {
          target: markdownParserTarget,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api\/markdown-parse/, "/parse"),
        },
      },
    },
  },
  integrations: [svelte(), mdx(), sitemap()],
  site: siteUrl,
});
