import { describe, expect, it } from "vitest";

import { getPage } from "./pagination";
import { getPoemsPagePath } from "./poem-pagination";

interface TestPoem {
  date: string;
  model: string;
  poem: string;
  title: string;
}

function makePoems(count: number): TestPoem[] {
  return Array.from({ length: count }, (_, index) => {
    const day = String(index + 1).padStart(2, "0");

    return {
      date: `2026-01-${day}`,
      model: "test",
      poem: "Line one",
      title: `Poem ${index + 1}`,
    };
  });
}

describe("poem pagination", () => {
  it("returns the requested page slice and metadata", () => {
    const page = getPage(makePoems(125), 2, 60);

    expect(page.currentPage).toBe(2);
    expect(page.pageSize).toBe(60);
    expect(page.totalPages).toBe(3);
    expect(page.totalItems).toBe(125);
    expect(page.items).toHaveLength(60);
    expect(page.items[0].title).toBe("Poem 61");
  });

  it("clamps out-of-range page numbers", () => {
    expect(getPage(makePoems(5), 99, 2).currentPage).toBe(3);
    expect(getPage(makePoems(5), 0, 2).currentPage).toBe(1);
  });

  it("keeps the first archive page canonical", () => {
    expect(getPoemsPagePath(1)).toBe("/poems");
    expect(getPoemsPagePath(2)).toBe("/poems/page/2");
  });
});
