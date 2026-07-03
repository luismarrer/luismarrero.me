<script lang="ts">
  export let value = "";
</script>

<label for="markdown-source" class="sr-only">Markdown input</label>
<textarea
    id="markdown-source"
    bind:value={value}
    aria-describedby="markdown-preview-heading"
    class="min-h-80 w-full min-w-0 flex-1 resize-y rounded-interactive border border-edge bg-secondary p-4 text-primary-foreground outline-none focus:border-accent md:h-[32rem]"
></textarea>
