import { formatCurrency } from "./formatCurrency";

describe("formatCurrency", () => {
  it("should format", () => {
    const number = 12345.1234;

    expect(formatCurrency(number, "en")).toBe("12,345.12");
  });
});
