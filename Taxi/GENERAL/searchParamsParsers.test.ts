import timezoneMock from "timezone-mock";

import {
  parseBooleanSearchParam,
  parseNumericSearchParam,
  parseIntegerSearchParam,
  parseDateSearchParam,
  parseArraySearchParam,
} from "./searchParamsParsers";

timezoneMock.register("UTC");

describe("searchParamsParsers", () => {
  describe.each([
    ["true", true],
    [["true"], true],
    ["false", false],
    [["false"], false],
    ["foo", undefined],
    ["", undefined],
    [["true", "false"], undefined],
    [[], undefined],
  ])("parseBooleanSearchParam(%p)", (input, expected) => {
    it(`returns ${expected}`, () => {
      expect(parseBooleanSearchParam(input)).toBe(expected);
      if (typeof input === "string") {
        expect(parseBooleanSearchParam([input])).toBe(expected);
      }
    });
  });

  describe.each([
    ["42", 42],
    ["3.14", 3.14],
    ["42.", 42],
    [".42", 0.42],
    ["1E-2", 0.01],
    ["3.14a", undefined],
    ["foo", undefined],
    ["", undefined],
    [[], undefined],
    [["42", "69"], undefined],
  ])("parseNumericSearchParam(%p)", (input, expected) => {
    it(`returns ${expected}`, () => {
      expect(parseNumericSearchParam(input)).toBe(expected);
      if (typeof input === "string") {
        expect(parseNumericSearchParam([input])).toBe(expected);
      }
    });
  });

  describe.each([
    ["42", 42],
    ["3.14", undefined],
    ["42.", 42],
    ["42.0", 42],
    [".42", undefined],
    ["1E-2", undefined],
    ["3.14a", undefined],
    ["foo", undefined],
    ["", undefined],
    [[], undefined],
    [["42", "69"], undefined],
  ])("parseIntegerSearchParam(%p)", (input, expected) => {
    it(`returns ${expected}`, () => {
      expect(parseIntegerSearchParam(input)).toBe(expected);
      if (typeof input === "string") {
        expect(parseIntegerSearchParam([input])).toBe(expected);
      }
    });
  });

  describe.each([
    ["1970-01-01", new Date(0)],
    ["1970-01-01T00:42:00.000Z", new Date(1970, 0, 1, 0, 42, 0)],
    ["1970-01-01T00:00:00.000+03:00", new Date(1969, 11, 31, 21, 0, 0)],
    ["1970-01-42", undefined],
    ["1970-13-01", undefined],
    ["1970-01-01T25:00:00Z", undefined],
    ["", undefined],
    [[], undefined],
    [["1970-01-01", "1970-01-01"], undefined],
  ])("parseDateSearchParam(%p)", (input, expected) => {
    it(`returns ${expected}`, () => {
      expect(parseDateSearchParam(input)).toStrictEqual(expected);
      if (typeof input === "string") {
        expect(parseDateSearchParam([input])).toStrictEqual(expected);
      }
    });
  });

  describe.each([
    [["true"], [true]],
    [
      ["true", "false"],
      [true, false],
    ],
    [["true", "falze"], undefined],
    [[], undefined],
  ])("parseArraySearchParam(%p)", (input, expected) => {
    it(`returns ${expected}`, () => {
      expect(
        parseArraySearchParam(parseBooleanSearchParam)(input)
      ).toStrictEqual(expected);
    });
  });
});
