import { glob } from "astro/loaders";
import { defineCollection, z } from "astro:content";

import { isDateOnlyString } from "./lib/date";

const posts = defineCollection({
  loader: glob({ base: "src/posts", pattern: "**/*.{md,mdx}" }),
  schema: z.object({
    title: z.string(),
    published: z.boolean(),
    description: z.string(),
    date: z.coerce.date(),
    tags: z.string().array(),
    lang: z.enum(["en", "es"]).default("es"),
  }),
});

const ai_poems = defineCollection({
  loader: glob({ base: "src/ai_poems", pattern: "**/*.json" }),
  schema: z.object({
    model: z.string().refine((value) => value.trim().length > 0),
    title: z.string().refine((value) => value.trim().length > 0),
    date: z
      .string()
      .refine(
        isDateOnlyString,
        "AI poem dates must be real YYYY-MM-DD date-only strings",
      ),
    poem: z.string().refine((value) => value.trim().length > 0),
  }),
});

export const collections = { posts, ai_poems };
