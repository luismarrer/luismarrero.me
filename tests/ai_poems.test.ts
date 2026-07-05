import { readdir, readFile } from "node:fs/promises";

import { describe, expect, it } from "vitest";

import { isDateOnlyString } from "../src/lib/date";

const poemsDir = new URL("../src/ai_poems/", import.meta.url);
const fallbackPoemsPath = new URL("../src/data/fallback-poems.json", import.meta.url);
const poemFilePattern = /^\d{4}-\d{2}-\d{2}\.json$/;
const poemKeys = ["date", "model", "poem", "title"];
const fallbackPoemKeys = ["poem", "title"];

function expectDateOnlyString(value: string) {
  expect(isDateOnlyString(value)).toBe(true);
}

function normalizeTitle(value: string) {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

function normalizeBody(value: string) {
  return value.normalize("NFC").toLowerCase().replace(/\s+/g, " ").trim();
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

  it("keeps the fallback poem bank valid and unpublished", async () => {
    const filenames = (await readdir(poemsDir))
      .filter((filename) => filename.endsWith(".json"))
      .sort();
    const publishedTitleKeys = new Set<string>();
    const publishedBodyKeys = new Set<string>();

    for (const filename of filenames) {
      const raw = await readFile(new URL(filename, poemsDir), "utf8");
      const poem = JSON.parse(raw) as Record<string, unknown>;
      publishedTitleKeys.add(normalizeTitle(poem.title as string));
      publishedBodyKeys.add(normalizeBody(poem.poem as string));
    }

    const rawFallbackPoems = await readFile(fallbackPoemsPath, "utf8");
    const fallbackPoems = JSON.parse(rawFallbackPoems) as Record<string, unknown>[];
    const fallbackTitleKeys = new Set<string>();
    const fallbackBodyKeys = new Set<string>();

    expect(Array.isArray(fallbackPoems)).toBe(true);
    expect(fallbackPoems.length).toBeGreaterThan(0);

    for (const fallbackPoem of fallbackPoems) {
      expect(Object.keys(fallbackPoem).sort()).toEqual(fallbackPoemKeys);

      const title = fallbackPoem.title;
      const body = fallbackPoem.poem;

      expect(typeof title).toBe("string");
      expect(typeof body).toBe("string");

      const titleKey = normalizeTitle(title as string);
      const bodyKey = normalizeBody(body as string);

      expect(titleKey.length).toBeGreaterThan(0);
      expect(bodyKey.length).toBeGreaterThan(0);
      expect(fallbackTitleKeys.has(titleKey)).toBe(false);
      expect(fallbackBodyKeys.has(bodyKey)).toBe(false);
      expect(publishedTitleKeys.has(titleKey)).toBe(false);
      expect(publishedBodyKeys.has(bodyKey)).toBe(false);

      fallbackTitleKeys.add(titleKey);
      fallbackBodyKeys.add(bodyKey);
    }
  });
});
