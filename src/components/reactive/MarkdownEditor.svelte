<script lang="ts">
  import EditorPane from "@/components/reactive/EditorPane.svelte";
  import PreviewPane from "@/components/reactive/PreviewPane.svelte";
  import { onMount } from "svelte";
  import { debounce } from "ts-debounce";

  let text = "# Hola\n## mundo\n_Esto_ **es** *markdown*\n\n";
  let html = "";

  // In production we call the parser directly (its CORS allows that origin).
  // In dev the request is proxied through the Astro dev server (see
  // astro.config.mjs) so the browser doesn't hit a CORS wall on localhost.
  const PARSE_URL = import.meta.env.DEV
    ? "/api/markdown-parse"
    : "https://markdown-regex.vercel.app/parse";

  async function parse() {
    try {
      const res = await fetch(PARSE_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const { html: parsed } = await res.json();
      html = parsed;
    } catch (err) {
      console.error("Parse failed:", err);
      html = `<p class="text-red-500">No se pudo convertir el Markdown.</p>`;
    }
  }

  onMount(() => parse());                 // primera carga
  const parseDebounced = debounce(parse, 300);
  $: text && parseDebounced();            // solo cuando cambia `text`
</script>


<EditorPane bind:value={text} />
<PreviewPane {html} />
