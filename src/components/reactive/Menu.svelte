<script lang="ts">
    import { userSocials, userEmail } from "../../data/user-contact.json";
    import { slide, blur } from "svelte/transition";

    let droppedDown: boolean = $state(false);

    $effect(() => {
        document.body.style.overflow = droppedDown ? "hidden" : "";
    })
</script>

<button class="ml-auto my-auto shrink-0 cursor-pointer hover:brightness-125 md:hidden" aria-label="Drop Down Menu" aria-expanded={droppedDown} onclick={() => droppedDown = !droppedDown}>
    <svg class="w-8 h-8 stroke-accent" stroke-width="2" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M3 5H21 M3 12H21 M3 19H21" stroke-linecap="round" stroke-linejoin="round"></path>
    </svg>
</button>

{#if droppedDown}
<div transition:blur class="fixed inset-0 z-40 flex h-lvh w-screen flex-row backdrop-blur-sm">
    <div transition:slide={{axis: "x"}} class="flex w-[min(22rem,82vw)] border-r border-accent bg-primary/95">
        <div class="my-auto ml-auto flex min-w-0 flex-col gap-8 p-6 text-right text-xl sm:p-8 sm:text-2xl">
            <a
            class="break-all hover:brightness-125 duration-200"
            href={`mailto:${userEmail}`}>{userEmail}</a>
            {#each userSocials as social}
                <a class="hover:brightness-125 duration-200" href={social.link}>
                    {social.title}
                </a>
            {/each}
        </div>
    </div>
    <button class="flex-1" aria-label="Exit Drop Down Menu" onclick={() => droppedDown = !droppedDown}>
    </button>
</div>
{/if}
