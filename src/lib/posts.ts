import { getCollection, type CollectionEntry } from "astro:content";

import { type PageInput, getPage } from "./pagination";
import {
  getPostTagPathBySlug,
  getPostTags,
  slugifyTag,
  type PostTag,
} from "./post-tags";

export type PostEntry = CollectionEntry<"posts">;

export const POSTS_PER_PAGE = 12;

export interface PostsPage
  extends Omit<PageInput<PostEntry>, "items" | "totalItems"> {
  basePath: string;
  posts: PostEntry[];
  totalPosts: number;
}

export interface PostTagPageProps {
  page: PostsPage;
  tag: PostTag;
  tags: PostTag[];
}

export interface PostCardData {
  date: Date;
  description: string;
  id: string;
  lang: string;
  tags: string[];
  title: string;
}

export function toPostCardData(post: PostEntry): PostCardData {
  return {
    date: post.data.date,
    description: post.data.description,
    id: post.id,
    lang: post.data.lang,
    tags: post.data.tags,
    title: post.data.title,
  };
}

export function sortPostsNewestFirst(posts: PostEntry[]): PostEntry[] {
  return [...posts].sort(
    (a, b) => b.data.date.valueOf() - a.data.date.valueOf(),
  );
}

export function formatPostDate(date: Date, locale = "en-us"): string {
  return new Intl.DateTimeFormat(locale, {
    year: "numeric",
    month: "short",
    day: "numeric",
    timeZone: "UTC",
  }).format(date);
}

export function getArchivePagePath(basePath: string, page: number): string {
  const normalizedBasePath = basePath.replace(/\/+$/, "") || "/";
  return page === 1 ? normalizedBasePath : `${normalizedBasePath}/page/${page}`;
}

export function getPostsPage(
  posts: PostEntry[],
  currentPage: number,
  basePath = "/posts",
  pageSize = POSTS_PER_PAGE,
): PostsPage {
  const page = getPage(posts, currentPage, pageSize);

  return {
    basePath,
    currentPage: page.currentPage,
    pageSize: page.pageSize,
    posts: page.items,
    totalPages: page.totalPages,
    totalPosts: page.totalItems,
  };
}

export function getPostsForTag(posts: PostEntry[], tagSlug: string): PostEntry[] {
  return posts.filter((post) =>
    post.data.tags.some((tag) => slugifyTag(tag) === tagSlug),
  );
}

export async function getPublishedPosts(): Promise<PostEntry[]> {
  const posts = await getCollection("posts");
  return sortPostsNewestFirst(posts.filter((post) => post.data.published));
}

export async function getPostTagStaticPaths() {
  const posts = await getPublishedPosts();
  const tags = getPostTags(posts);

  return tags.map((tag) => ({
    params: { tag: tag.slug },
    props: {
      page: getPostsPage(getPostsForTag(posts, tag.slug), 1, tag.path),
      tag,
      tags,
    } satisfies PostTagPageProps,
  }));
}

export async function getPostTagArchiveStaticPaths() {
  const posts = await getPublishedPosts();
  const tags = getPostTags(posts);
  const paths: Array<{
    params: { page: string; tag: string };
    props: PostTagPageProps;
  }> = [];

  for (const tag of tags) {
    const tagPosts = getPostsForTag(posts, tag.slug);
    const totalPages = Math.max(Math.ceil(tagPosts.length / POSTS_PER_PAGE), 1);

    for (let pageNumber = 2; pageNumber <= totalPages; pageNumber += 1) {
      paths.push({
        params: { page: String(pageNumber), tag: tag.slug },
        props: {
          page: getPostsPage(tagPosts, pageNumber, getPostTagPathBySlug(tag.slug)),
          tag,
          tags,
        },
      });
    }
  }

  return paths;
}

export { getPostTags, slugifyTag };
