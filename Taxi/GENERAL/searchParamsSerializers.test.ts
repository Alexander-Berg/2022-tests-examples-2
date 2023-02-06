import timezoneMock from "timezone-mock";

import {
  serializeBooleanSearchParam,
  serializeNumericSearchParam,
  serializeIntegerSearchParam,
  serializeDateSearchParam,
  serializeArraySearchParam,
  serializeDateTimeSearchParam,
} from "./searchParamsSerializers";

timezoneMock.register("UTC");

describe("searchParamsSerializers", () => {
  describe.each([
    [true, "true"],
    [false, "false"],
  ])("serializeBooleanSearchParam(%p)", (input, expected) => {
    it(`returns ${expected}`, () => {
      expect(serializeBooleanSearchParam(input)).toBe(expected);
    });
  });

  describe.each([
    [42, "42"],
    [3.14, "3.14"],
    [42.0, "42"],
  ])("serializeNumericSearchParam(%p)", (input, expected) => {
    it(`returns ${expected}`, () => {
      expect(serializeNumericSearchParam(input)).toBe(expected);
    });
  });

  describe.each([
    [42, "42"],
    [42.0, "42"],
    [3.14, "3"],
    [42.69, "42"],
  ])("serializeIntegerSearchParam(%p)", (input, expected) => {
    it(`returns ${expected}`, () => {
      expect(serializeIntegerSearchParam(input)).toBe(expected);
    });
  });

  describe.each([[new Date(1970, 0, 1), "19700101"]])(
    "serializeDateSearchParam(%p)",
    (input, expected) => {
      it(`returns ${expected}`, () => {
        expect(serializeDateSearchParam(input)).toBe(expected);
      });
    }
  );

  describe.each([[new Date(1970, 0, 1, 0, 0, 0), "19700101T000000Z"]])(
    "serializeDateTimeSearchParam(%p)",
    (input, expected) => {
      it(`returns ${expected}`, () => {
        expect(serializeDateTimeSearchParam(input)).toBe(expected);
      });
    }
  );

  describe.each([
    [
      [42, 69],
      ["42", "69"],
    ],
  ])("serializeArraySearchParam(%p)", (input, expected) => {
    it(`returns ${expected}`, () => {
      expect(
        serializeArraySearchParam(serializeIntegerSearchParam)(input)
      ).toStrictEqual(expected);
    });
  });
});
