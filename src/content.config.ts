import { glob } from "astro/loaders";
import { defineCollection, z } from "astro:content";

const posts = defineCollection({
  loader: glob({ base: "src/posts", pattern: "**/*.{md,mdx}" }),
  schema: z.object({
    title: z.string(),
    published: z.boolean(),
    description: z.string(),
    date: z.coerce.date(),
    tags: z.string().array(),
  }),
});

const ai_poems = defineCollection({
  loader: glob({ base: "src/ai_poems", pattern: "**/*.json" }),
  schema: z.object({
    model: z.string(),
    title: z.string(),
    date: z.string(), // or z.date() if you use Date objects
    poem: z.string(),
  }),
});

export const collections = { posts, ai_poems };
