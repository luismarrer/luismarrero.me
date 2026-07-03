import { readdir, readFile } from "node:fs/promises";

import { describe, expect, it } from "vitest";

import { isDateOnlyString } from "../src/lib/date";

const poemsDir = new URL("../src/ai_poems/", import.meta.url);
const poemFilePattern = /^\d{4}-\d{2}-\d{2}\.json$/;
const poemKeys = ["date", "model", "poem", "title"];

function expectDateOnlyString(value: string) {
  expect(isDateOnlyString(value)).toBe(true);
}

describe("AI poem content", () => {
  it("keeps every poem JSON file schema-compatible", async () => {
    const filenames = (await readdir(poemsDir))
      .filter((filename) => filename.endsWith(".json"))
      .sort();

    expect(filenames.length).toBeGreaterThan(0);
    expect(new Set(filenames).size).toBe(filenames.length);

    const dates = new Set<string>();

    for (const filename of filenames) {
      expect(filename).toMatch(poemFilePattern);

      const raw = await readFile(new URL(filename, poemsDir), "utf8");
      const poem = JSON.parse(raw) as Record<string, unknown>;
      expect(Object.keys(poem).sort()).toEqual(poemKeys);

      const date = poem.date;
      const model = poem.model;
      const title = poem.title;
      const body = poem.poem;

      expect(typeof date).toBe("string");
      expect(typeof model).toBe("string");
      expect(typeof title).toBe("string");
      expect(typeof body).toBe("string");

      expectDateOnlyString(date as string);
      expect(date).toBe(filename.replace(/\.json$/, ""));
      expect(dates.has(date as string)).toBe(false);
      dates.add(date as string);
      expect((model as string).trim().length).toBeGreaterThan(0);
      expect((title as string).trim().length).toBeGreaterThan(0);
      expect((body as string).trim().length).toBeGreaterThan(0);
    }
  });
});
