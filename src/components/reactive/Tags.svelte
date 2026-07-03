<script lang="ts">
    import { filters, toggleFilter } from '../../stores/filters.store';
    import { cn } from '../../styles/cn';

    interface TagItem {
        name: string;
        count?: number;
    }

    interface Props {
        tags: TagItem[];
        showCounts?: boolean;
        class?: string;
    }

    const { tags, showCounts = false, class: className = '' }: Props = $props();
</script>

{#snippet tagButton(item: TagItem)}
    {@const isActive = $filters.includes(item.name)}
    <button
        type="button"
        aria-pressed={isActive}
        onclick={() => toggleFilter(item.name)}
        class={cn(
            "inline-block h-fit w-fit rounded-interactive border px-2 py-1 font-semibold duration-200 hover:cursor-pointer",
            isActive
                ? "border-primary-foreground bg-primary text-primary-foreground"
                : "border-accent bg-transparent text-accent hover:bg-accent hover:text-primary",
        )}
    >
        {item.name}{#if showCounts && item.count !== undefined} <span class="opacity-65">{item.count}</span>{/if}
    </button>
{/snippet}

<div class={cn("flex flex-row flex-wrap gap-2", className)}>
    {#each tags as item}
        {@render tagButton(item)}
    {/each}
</div>
