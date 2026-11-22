import { describe, expect, it } from "vitest";
import { fmtInt, fmtRate } from "./format";

describe("format", () => {
  it("floors and groups integers", () => {
    expect(fmtInt(1234567.9)).toBe("1,234,567");
  });

  it("formats rates with adaptive precision", () => {
    expect(fmtRate(4.3)).toBe("4.3");
    expect(fmtRate(0.42)).toBe("0.42");
    expect(fmtRate(99000)).toBe("99,000");
  });
});
