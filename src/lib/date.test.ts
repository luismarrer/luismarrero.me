import { describe, expect, it } from "vitest";

import {
  formatDateOnly,
  getDateInTimeZone,
  isDateOnlyString,
  PUERTO_RICO_TIME_ZONE,
} from "./date";

describe("date helpers", () => {
  it("validates real date-only strings", () => {
    expect(isDateOnlyString("2026-07-03")).toBe(true);
    expect(isDateOnlyString("2026-02-29")).toBe(false);
    expect(isDateOnlyString("2026-7-3")).toBe(false);
  });

  it("formats date-only strings without local timezone drift", () => {
    expect(formatDateOnly("2026-07-03")).toBe("Jul 3, 2026");
  });

  it("reads Puerto Rico dates at UTC day boundaries", () => {
    expect(
      getDateInTimeZone(
        PUERTO_RICO_TIME_ZONE,
        new Date("2026-07-03T03:59:59.000Z"),
      ),
    ).toBe("2026-07-02");

    expect(
      getDateInTimeZone(
        PUERTO_RICO_TIME_ZONE,
        new Date("2026-07-03T04:00:00.000Z"),
      ),
    ).toBe("2026-07-03");
  });
});
