export interface PostTag {
  count: number;
  name: string;
  path: string;
  slug: string;
}

interface TaggablePost {
  data: {
    tags: string[];
  };
}

export function slugifyTag(tag: string): string {
  const slug = tag
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");

  return slug || "tag";
}

export function getPostTagPath(tag: string): string {
  return getPostTagPathBySlug(slugifyTag(tag));
}

export function getPostTagPathBySlug(slug: string): string {
  return `/posts/tags/${slug}`;
}

export function getPostTags(posts: TaggablePost[]): PostTag[] {
  const tags = new Map<string, PostTag>();

  for (const post of posts) {
    for (const tag of new Set(post.data.tags)) {
      const slug = slugifyTag(tag);
      const existingTag = tags.get(slug);

      if (existingTag) {
        existingTag.count += 1;
        continue;
      }

      tags.set(slug, {
        count: 1,
        name: tag,
        path: getPostTagPathBySlug(slug),
        slug,
      });
    }
  }

  return [...tags.values()].sort((a, b) => a.name.localeCompare(b.name));
}
