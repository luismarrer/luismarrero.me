<script lang="ts">
    import { filters, removeFilter } from '../../stores/filters.store.ts';
</script>

{#snippet filter(title: string)}
    <button
        type="button"
        aria-label={`Remove ${title} filter`}
        onclick={() => removeFilter(title)}
        class="group hover:cursor-pointer hover:opacity-60 duration-200"
    >
        <div class="w-fit px-2 bg-primary border rounded-interactive border-primary-foreground group-hover:-translate-y-1/4 group-hover:-rotate-2 duration-200">
            <span class="text-primary-foreground font-semibold">{ title }</span>
        </div>    
    </button>
{/snippet}

{#if $filters.length > 0}
    <div class="flex min-w-0 gap-3 p-3 pb-0 sm:gap-4 sm:p-4 sm:pb-0">
        <svg aria-hidden="true" class="my-auto h-6 w-6 shrink-0 stroke-edge" stroke-width="2" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 5H11 M3 12H16 M3 19H21" stroke-linecap="round" stroke-linejoin="round"></path>
        </svg>

        <div class="flex min-w-0 flex-wrap gap-2 opacity-60 sm:gap-4">
            {#each $filters as title}
                {@render filter(title)}
            {/each}
        </div>
    </div>
{/if}
