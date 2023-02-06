import { formatNumber } from "./formatNumber";

describe("formatNumber", () => {
  it("should format", () => {
    const number = 12345.1234;

    expect(formatNumber(number, "en")).toBe("12,345.123");
  });
});
