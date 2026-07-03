export const DATE_ONLY_PATTERN = /^\d{4}-\d{2}-\d{2}$/;
export const PUERTO_RICO_TIME_ZONE = "America/Puerto_Rico";

export function parseDateOnly(value: string): Date {
  if (!DATE_ONLY_PATTERN.test(value)) {
    throw new Error(`Expected date-only string in YYYY-MM-DD format: ${value}`);
  }

  const [year, month, day] = value.split("-").map(Number);
  const date = new Date(Date.UTC(year, month - 1, day));

  if (
    date.getUTCFullYear() !== year ||
    date.getUTCMonth() !== month - 1 ||
    date.getUTCDate() !== day
  ) {
    throw new Error(`Invalid date-only string: ${value}`);
  }

  return date;
}

export function isDateOnlyString(value: string): boolean {
  try {
    parseDateOnly(value);
    return true;
  } catch {
    return false;
  }
}

export function formatDateOnly(value: string, locale = "en-us"): string {
  return new Intl.DateTimeFormat(locale, {
    year: "numeric",
    month: "short",
    day: "numeric",
    timeZone: "UTC",
  }).format(parseDateOnly(value));
}

export function getDateInTimeZone(
  timeZone: string,
  now = new Date(),
): string {
  const parts = new Intl.DateTimeFormat("en", {
    timeZone,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(now);

  const getPart = (type: string) => {
    const part = parts.find((item) => item.type === type);
    if (!part) {
      throw new Error(`Could not read ${type} from ${timeZone} date parts`);
    }

    return part.value;
  };

  return `${getPart("year")}-${getPart("month")}-${getPart("day")}`;
}
