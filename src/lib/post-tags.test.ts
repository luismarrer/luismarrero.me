import { describe, expect, it } from "vitest";

import { getPostTags, slugifyTag } from "./post-tags";

describe("post tags", () => {
  it("creates stable URL slugs", () => {
    expect(slugifyTag("Astro")).toBe("astro");
    expect(slugifyTag("Rendimiento Web")).toBe("rendimiento-web");
    expect(slugifyTag("Tipografía")).toBe("tipografia");
  });

  it("deduplicates and counts tags by slug", () => {
    const tags = getPostTags([
      { data: { tags: ["Astro", "CSS", "Astro"] } },
      { data: { tags: ["astro", "MDX"] } },
    ]);

    expect(tags).toEqual([
      { count: 2, name: "Astro", path: "/posts/tags/astro", slug: "astro" },
      { count: 1, name: "CSS", path: "/posts/tags/css", slug: "css" },
      { count: 1, name: "MDX", path: "/posts/tags/mdx", slug: "mdx" },
    ]);
  });
});
