import { atom } from "nanostores";

export const filters = atom<string[]>([]);

export function addFilter(filter: string) {
  if (filters.get().includes(filter)) {
    return;
  }

  filters.set([...filters.get(), filter]);
}

export function removeFilter(filter: string) {
  const currentFilters: string[] = filters.get();
  const indexToRemove: number = currentFilters.indexOf(filter, 0);

  if (indexToRemove < 0) {
    return;
  }

  filters.set(currentFilters.filter((currentFilter) => currentFilter !== filter));
}

export function toggleFilter(filter: string) {
  if (filters.get().includes(filter)) {
    removeFilter(filter);
    return;
  }

  addFilter(filter);
}
