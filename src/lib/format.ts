const intFmt = new Intl.NumberFormat("en-US");

export function fmtInt(n: number): string {
  return intFmt.format(Math.floor(n));
}

export function fmtBig(n: number): string {
  const a = Math.abs(n);
  if (a >= 1e9) return (n / 1e9).toFixed(1) + "B";
  if (a >= 1e6) return (n / 1e6).toFixed(1) + "M";
  return intFmt.format(Math.floor(n));
}

export function fmtRate(n: number): string {
  if (n >= 1000) return intFmt.format(Math.floor(n));
  if (n >= 1) return n.toFixed(1);
  return n.toFixed(2);
}

const timeFmts = new Map<string, Intl.DateTimeFormat>();

export function fmtLocalTime(utcMs: number, tzid: string): string {
  let f = timeFmts.get(tzid);
  if (!f) {
    f = new Intl.DateTimeFormat("en-GB", {
      timeZone: tzid,
      hour: "2-digit",
      minute: "2-digit",
      hourCycle: "h23",
    });
    timeFmts.set(tzid, f);
  }
  return f.format(new Date(utcMs));
}

export function fmtPct(x: number): string {
  return (x * 100).toFixed(1) + "%";
}
