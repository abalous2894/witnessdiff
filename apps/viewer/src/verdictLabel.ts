/** Human-readable verdict label for tight UI spaces. */
export function formatVerdict(verdict: string): string {
  return verdict.replaceAll("_", " ");
}
