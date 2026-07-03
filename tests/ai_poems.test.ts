import { readdir, readFile } from "node:fs/promises";

import { describe, expect, it } from "vitest";

const poemsDir = new URL("../src/ai_poems/", import.meta.url);
const poemFilePattern = /^\d{4}-\d{2}-\d{2}\.json$/;
const datePattern = /^\d{4}-\d{2}-\d{2}$/;
const poemKeys = ["date", "model", "poem", "title"];

function expectDateOnlyString(value: string) {
  expect(value).toMatch(datePattern);

  const parsed = new Date(`${value}T00:00:00.000Z`);
  expect(Number.isNaN(parsed.getTime())).toBe(false);
  expect(parsed.toISOString().slice(0, 10)).toBe(value);
}

describe("AI poem content", () => {
  it("keeps every poem JSON file schema-compatible", async () => {
    const filenames = (await readdir(poemsDir))
      .filter((filename) => filename.endsWith(".json"))
      .sort();

    expect(filenames.length).toBeGreaterThan(0);
    expect(new Set(filenames).size).toBe(filenames.length);

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
      expect((model as string).trim().length).toBeGreaterThan(0);
      expect((title as string).trim().length).toBeGreaterThan(0);
      expect((body as string).trim().length).toBeGreaterThan(0);
    }
  });
});
