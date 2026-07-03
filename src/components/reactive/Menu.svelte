<script lang="ts">
    import { tick } from "svelte";
    import { userSocials, userEmail } from "../../data/user-contact.json";

    let droppedDown: boolean = $state(false);
    let menuButton: HTMLButtonElement | undefined;
    let drawer: HTMLDivElement | undefined;
    let firstMenuLink: HTMLAnchorElement | undefined;
    let previousFocus: HTMLElement | null = null;

    async function openMenu() {
        previousFocus = document.activeElement instanceof HTMLElement
            ? document.activeElement
            : null;
        droppedDown = true;
        await tick();
        firstMenuLink?.focus();
    }

    async function closeMenu() {
        droppedDown = false;
        await tick();
        (previousFocus ?? menuButton)?.focus();
    }

    function toggleMenu() {
        if (droppedDown) {
            closeMenu();
        } else {
            openMenu();
        }
    }

    function handleDrawerKeydown(event: KeyboardEvent) {
        if (event.key === "Escape") {
            event.preventDefault();
            closeMenu();
            return;
        }

        if (event.key !== "Tab" || !drawer) return;

        const focusable = Array.from(
            drawer.querySelectorAll<HTMLElement>('a[href], button:not([disabled])'),
        ).filter((element) => element.tabIndex !== -1);

        if (focusable.length === 0) return;

        const first = focusable[0];
        const last = focusable[focusable.length - 1];

        if (event.shiftKey && document.activeElement === first) {
            event.preventDefault();
            last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
            event.preventDefault();
            first.focus();
        }
    }

    $effect(() => {
        document.body.style.overflow = droppedDown ? "hidden" : "";
        return () => {
            document.body.style.overflow = "";
        };
    })
</script>

<button
    bind:this={menuButton}
    type="button"
    class="ml-auto my-auto shrink-0 cursor-pointer hover:brightness-125 md:hidden"
    aria-label="Open contact menu"
    aria-expanded={droppedDown}
    aria-controls="mobile-contact-menu"
    aria-haspopup="dialog"
    onclick={toggleMenu}
>
    <svg aria-hidden="true" class="w-8 h-8 stroke-accent" stroke-width="2" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M3 5H21 M3 12H21 M3 19H21" stroke-linecap="round" stroke-linejoin="round"></path>
    </svg>
</button>

{#if droppedDown}
<div
    bind:this={drawer}
    id="mobile-contact-menu"
    role="dialog"
    aria-modal="true"
    aria-label="Contact menu"
    class="fixed inset-0 z-40 flex h-lvh w-screen flex-row backdrop-blur-sm"
    onkeydown={handleDrawerKeydown}
>
    <div class="flex w-[min(22rem,82vw)] border-r border-accent bg-primary/95">
        <div class="my-auto ml-auto flex min-w-0 flex-col gap-8 p-6 text-right text-xl sm:p-8 sm:text-2xl">
            <a
            bind:this={firstMenuLink}
            class="break-all hover:brightness-125 duration-200"
            href={`mailto:${userEmail}`}>{userEmail}</a>
            {#each userSocials as social}
                <a class="hover:brightness-125 duration-200" href={social.link}>
                    {social.title}
                </a>
            {/each}
        </div>
    </div>
    <button type="button" tabindex="-1" class="flex-1" aria-label="Close contact menu" onclick={closeMenu}>
    </button>
</div>
{/if}
