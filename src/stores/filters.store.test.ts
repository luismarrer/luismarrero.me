import { beforeEach, describe, expect, it } from "vitest";

import {
  addFilter,
  filters,
  removeFilter,
  toggleFilter,
} from "./filters.store";

describe("filters store", () => {
  beforeEach(() => {
    filters.set([]);
  });

  it("adds filters once and preserves insertion order", () => {
    addFilter("Astro");
    addFilter("Svelte");
    addFilter("Astro");

    expect(filters.get()).toEqual(["Astro", "Svelte"]);
  });

  it("removes an existing filter without mutating existing snapshots", () => {
    addFilter("Astro");
    addFilter("Svelte");
    const snapshot = filters.get();

    removeFilter("Astro");

    expect(filters.get()).toEqual(["Svelte"]);
    expect(snapshot).toEqual(["Astro", "Svelte"]);
  });

  it("ignores filters that are not present", () => {
    addFilter("Astro");

    removeFilter("Missing");

    expect(filters.get()).toEqual(["Astro"]);
  });

  it("toggles filters on and off", () => {
    toggleFilter("Astro");
    toggleFilter("Svelte");
    toggleFilter("Astro");

    expect(filters.get()).toEqual(["Svelte"]);
  });
});
