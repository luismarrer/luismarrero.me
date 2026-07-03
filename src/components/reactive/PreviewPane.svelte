<script lang="ts">
  export let html = "";
</script>

<section
  aria-labelledby="markdown-preview-heading"
  aria-live="polite"
  class="prose prose-invert min-h-80 w-full min-w-0 max-w-none flex-1 overflow-auto rounded-interactive border border-edge bg-secondary/40 p-4 md:h-[32rem]"
>
  <h2 id="markdown-preview-heading" class="sr-only">Markdown preview</h2>
  {@html html}
</section>
