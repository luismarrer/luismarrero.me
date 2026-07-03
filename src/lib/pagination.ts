export interface PageInput<T> {
  currentPage: number;
  items: T[];
  pageSize: number;
  totalPages: number;
  totalItems: number;
}

export function getPage<T>(
  items: T[],
  currentPage: number,
  pageSize: number,
): PageInput<T> {
  const totalItems = items.length;
  const totalPages = Math.max(Math.ceil(totalItems / pageSize), 1);
  const page = Math.min(Math.max(currentPage, 1), totalPages);
  const pageStart = (page - 1) * pageSize;

  return {
    currentPage: page,
    items: items.slice(pageStart, pageStart + pageSize),
    pageSize,
    totalPages,
    totalItems,
  };
}
