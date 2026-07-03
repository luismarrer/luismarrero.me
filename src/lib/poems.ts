import { getCollection, type CollectionEntry } from "astro:content";

import {
  formatDateOnly,
  getDateInTimeZone,
  PUERTO_RICO_TIME_ZONE,
} from "./date";
import { getPage, getPoemsPagePath, type PageInput } from "./poem-pagination";

export type PoemEntry = CollectionEntry<"ai_poems">;
export type Poem = PoemEntry["data"];

export const POEMS_PER_PAGE = 60;

export interface PoemsPage
  extends Omit<PageInput<Poem>, "items" | "totalItems"> {
  poems: Poem[];
  totalPoems: number;
}

export function sortPoemsNewestFirst(poems: Poem[]): Poem[] {
  return [...poems].sort((a, b) => b.date.localeCompare(a.date));
}

export function getPoemsPage(
  poems: Poem[],
  currentPage: number,
  pageSize = POEMS_PER_PAGE,
): PoemsPage {
  const page = getPage(poems, currentPage, pageSize);

  return {
    currentPage: page.currentPage,
    poems: page.items,
    pageSize: page.pageSize,
    totalPages: page.totalPages,
    totalPoems: page.totalItems,
  };
}

export { getPoemsPagePath };

export async function getPoemEntries(): Promise<PoemEntry[]> {
  return getCollection("ai_poems");
}

export async function getAllPoems(): Promise<Poem[]> {
  const entries = await getPoemEntries();
  return sortPoemsNewestFirst(entries.map((entry) => entry.data));
}

export async function getAllPoemPages(
  pageSize = POEMS_PER_PAGE,
): Promise<PoemsPage[]> {
  const poems = await getAllPoems();
  const totalPages = Math.max(Math.ceil(poems.length / pageSize), 1);

  return Array.from({ length: totalPages }, (_, index) =>
    getPoemsPage(poems, index + 1, pageSize),
  );
}

export async function getTodayPoem(now = new Date()): Promise<Poem | null> {
  const today = getDateInTimeZone(PUERTO_RICO_TIME_ZONE, now);
  const entries = await getPoemEntries();
  return entries.find((entry) => entry.data.date === today)?.data ?? null;
}

export async function getPoemStaticPaths() {
  const entries = await getPoemEntries();

  return entries.map((entry) => ({
    params: { date: entry.data.date },
    props: entry.data,
  }));
}

export async function getPoemArchiveStaticPaths() {
  const pages = await getAllPoemPages();

  return pages.slice(1).map((page) => ({
    params: { page: String(page.currentPage) },
    props: page,
  }));
}

export const formatPoemDate = formatDateOnly;
