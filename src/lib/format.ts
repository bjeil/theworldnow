const intFmt = new Intl.NumberFormat("en-US");

export function fmtInt(n: number): string {
  return intFmt.format(Math.floor(n));
}

export function fmtRate(n: number): string {
  if (n >= 1000) return intFmt.format(Math.floor(n));
  if (n >= 1) return n.toFixed(1);
  return n.toFixed(2);
}
