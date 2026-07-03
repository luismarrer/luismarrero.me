<script lang="ts">
    import { getPostTagPath } from '../../lib/post-tags';

    interface Props {
        tags: string[];
    }

    const { tags }: Props = $props();
</script>

{#snippet tag(title: string)}
    <a
        href={getPostTagPath(title)}
        class="inline-block h-fit w-fit rounded-interactive border border-accent bg-transparent px-2 py-1 font-semibold text-accent duration-200 hover:bg-accent hover:text-primary"
    >
        {title}
    </a>
{/snippet}

<div class="flex flex-row flex-wrap justify-center gap-2 mt-4 text-lg">
    {#each tags as title}
        {@render tag(title)}
    {/each}
</div>
