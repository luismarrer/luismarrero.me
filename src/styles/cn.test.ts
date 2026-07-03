import { describe, expect, it } from "vitest";

import { cn } from "./cn";

describe("cn", () => {
  it("combines clsx-compatible values", () => {
    expect(cn("base", ["font-bold", false && "hidden"], { "sr-only": true }))
      .toBe("base font-bold sr-only");
  });

  it("keeps the winning Tailwind class for conflicting utilities", () => {
    expect(cn("rounded-sm px-2 text-sm", "px-4", ["text-lg"])).toBe(
      "rounded-sm px-4 text-lg",
    );
  });
});
