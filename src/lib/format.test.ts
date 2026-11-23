import { describe, expect, it } from "vitest";
import { fmtBig, fmtInt, fmtRate } from "./format";

describe("format", () => {
  it("floors and groups integers", () => {
    expect(fmtInt(1234567.9)).toBe("1,234,567");
  });

  it("abbreviates millions and billions with one decimal", () => {
    expect(fmtBig(999999)).toBe("999,999");
    expect(fmtBig(1000000)).toBe("1.0M");
    expect(fmtBig(7657885833)).toBe("7.7B");
    expect(fmtBig(999999999)).toBe("1000.0M");
    expect(fmtBig(1000000000)).toBe("1.0B");
    expect(fmtBig(4300)).toBe("4,300");
  });

  it("formats rates with adaptive precision", () => {
    expect(fmtRate(4.3)).toBe("4.3");
    expect(fmtRate(0.42)).toBe("0.42");
    expect(fmtRate(99000)).toBe("99,000");
  });
});
