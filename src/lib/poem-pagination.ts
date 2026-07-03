export { getPage, type PageInput } from "./pagination";

export function getPoemsPagePath(page: number): string {
  return page === 1 ? "/poems" : `/poems/page/${page}`;
}
