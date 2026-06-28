<script lang="ts">
    import { type CollectionEntry } from 'astro:content';
    import { filters } from '../../stores/filters.store';
    import Filters from './Filters.svelte';
    import { cn } from '../../styles/cn';

    interface Props {
        allPosts: CollectionEntry<'posts'>[];
    }

    const { allPosts }: Props = $props();
    let sortedPosts: CollectionEntry<'posts'>[] = $state(allPosts);

    function getIntersectionLength(a: any[], b: any[]): number {
        const intersection = a.filter(value => b.includes(value));
        return intersection.length;
    }

    function sortPosts(filters: string[]) {
        if(!filters || filters.length == 0){
            sortedPosts = allPosts.sort((a: any, b: any) => b.data.date.valueOf() - a.data.date.valueOf());
            return;
        }
        
        sortedPosts = allPosts.sort((a: any, b: any) => getIntersectionLength(b.data.tags, filters) - getIntersectionLength(a.data.tags, filters));
    }

    filters.subscribe((value) => {
        sortPosts([...value]);
    })

    function compareTags(a: string, b: string): number {
        const includesA: boolean = $filters.includes(a);
        const includesB: boolean = $filters.includes(b);
        return includesA && includesB ? 0 : includesA ? -1 : 1; 
    }

    function getSortedTags(post: CollectionEntry<'posts'>): string[] {
        const sortedTags: string[] = [...post.data.tags];
        sortedTags.sort((a, b) => compareTags(a, b));
        return sortedTags;
    }
</script>

{#snippet postCard(post: CollectionEntry<'posts'>)}
    <a href={`/posts/${post.id}`} class="flex h-full min-h-32 min-w-0 flex-col justify-between gap-2 rounded-interactive border border-edge bg-linear-to-b from-secondary to-secondary/60 p-3 pointer-events-auto duration-200 hover:border-accent">
        <div class="min-w-0">
            <span class="text-sm text-primary-foreground/75">
                <time datetime={post.data.date.toISOString()}>
                    {post.data.date.toLocaleDateString('en-us', {year: 'numeric', month: 'short', day: 'numeric'})}
                </time>
            </span>
            <h2 class="break-words text-lg font-semibold">{post.data.title}</h2>
            <p class="break-words">{post.data.description}</p>
        </div>
        <div class="flex flex-row flex-wrap gap-x-2 gap-y-1 overflow-hidden text-accent">
            {#each getSortedTags(post) as tag}
                <span class={cn("break-words", ($filters.length > 0 && !$filters.includes(tag)) ? "opacity-60" : "font-black")}>{tag}</span>
            {/each}
        </div>
    </a>
{/snippet}

<Filters />

<div class="group grid min-w-0 grid-cols-1 gap-3 rounded-interactive p-3 pointer-events-none duration-200 hover:border-edge sm:grid-cols-2 sm:gap-4 sm:p-4 md:grid-cols-3">					
    {#each sortedPosts as post}
        {@render postCard(post)}
    {/each}
</div>
