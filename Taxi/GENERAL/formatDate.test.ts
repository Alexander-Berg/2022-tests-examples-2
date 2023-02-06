import { formatDate } from "./formatDate";

describe("formatDate", () => {
  it("should format with defaults", () => {
    formatDate(new Date(0));
  });

  it("should format with locale and options", () => {
    formatDate(new Date(0), "en-US", {
      timeZone: "UTC",
      year: "numeric",
      month: "numeric",
      day: "numeric",
      hour: "numeric",
      minute: "numeric",
    });

    formatDate(new Date(0), "en-US", {
      timeZone: "UTC",
      year: "numeric",
      month: "long",
      day: "numeric",
    });

    formatDate(new Date(0), "en-US", {
      timeZone: "UTC",
      hour12: false,
      hour: "numeric",
      minute: "numeric",
    });
  });
});
