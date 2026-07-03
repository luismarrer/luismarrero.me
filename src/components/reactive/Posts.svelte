<script lang="ts">
    import type { PostCardData } from '../../lib/posts';
    import { filters } from '../../stores/filters.store';
    import Filters from './Filters.svelte';
    import { cn } from '../../styles/cn';

    interface Props {
        posts: PostCardData[];
    }

    const { posts }: Props = $props();

    const dateFormatter = new Intl.DateTimeFormat('en-us', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        timeZone: 'UTC',
    });

    function getIntersectionLength(a: string[], b: string[]): number {
        return a.filter((value) => b.includes(value)).length;
    }

    function sortPosts(allPosts: PostCardData[], activeFilters: string[]): PostCardData[] {
        const byDate = [...allPosts].sort((a, b) => b.date.valueOf() - a.date.valueOf());

        if (activeFilters.length === 0) {
            return byDate;
        }

        return byDate.sort(
            (a, b) =>
                getIntersectionLength(b.tags, activeFilters) -
                getIntersectionLength(a.tags, activeFilters),
        );
    }

    function getSortedTags(tags: string[], activeFilters: string[]): string[] {
        return [...tags].sort(
            (a, b) => Number(activeFilters.includes(b)) - Number(activeFilters.includes(a)),
        );
    }

    const sortedPosts = $derived(sortPosts(posts, $filters));
</script>

{#snippet postCard(post: PostCardData)}
    <article
        lang={post.lang}
        class="flex h-full min-h-32 min-w-0 flex-col justify-between gap-2 rounded-interactive border border-edge bg-linear-to-b from-secondary to-secondary/60 p-3 duration-200 hover:border-accent"
    >
        <a href={`/posts/${post.id}`} class="min-w-0">
            <span class="text-sm text-primary-foreground/75">
                <time datetime={post.date.toISOString()}>{dateFormatter.format(post.date)}</time>
            </span>
            <h2 class="break-words text-lg font-semibold">{post.title}</h2>
            <p class="break-words">{post.description}</p>
        </a>

        <div class="flex flex-row flex-wrap gap-x-2 gap-y-1 overflow-hidden text-accent">
            {#each getSortedTags(post.tags, $filters) as tag}
                <span
                    class={cn(
                        "break-words font-semibold duration-200",
                        $filters.length > 0 && ($filters.includes(tag) ? "font-black" : "opacity-60"),
                    )}
                >
                    {tag}
                </span>
            {/each}
        </div>
    </article>
{/snippet}

<div class="flex flex-col gap-4">
    <Filters />

    <div class="grid min-w-0 grid-cols-1 gap-3 sm:grid-cols-2 sm:gap-4 md:grid-cols-3">
        {#each sortedPosts as post (post.id)}
            {@render postCard(post)}
        {/each}
    </div>
</div>
