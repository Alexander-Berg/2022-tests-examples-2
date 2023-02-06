import { describe, expect, test } from "@jest/globals";
import { extract } from "./extract";

describe("should extract flags", () => {
  test("multiple flags", () => {
    expect(
      extract(`\
        useFlag({
          id: "17d4da98-e2b6-45ec-b9b1-71904f3acbcc",
          description: "First test flag",
        });
        useFlag({
          id: "b0ad7c02-20e6-488a-84b2-128b60e57b47",
          description: "Second test flag",
        });
      `)
    ).toEqual([
      {
        id: "17d4da98-e2b6-45ec-b9b1-71904f3acbcc",
        description: "First test flag",
      },
      {
        id: "b0ad7c02-20e6-488a-84b2-128b60e57b47",
        description: "Second test flag",
      },
    ]);
  });

  test("no flags", () => {
    expect(
      extract(`\
        notUseFlag({ id: 1, description: "Not a flag" });
      `)
    ).toEqual([]);
  });
});

describe("should throw if encounters an invalid usaFlag invocation", () => {
  test("extra prop", () => {
    expect(() =>
      extract(`\
        useFlag({
          id: "682d11d6-37a0-42b4-a67b-befd331234c5",
          description: "This flag is in fact a dog",
          name: "Dog",
        });
      `)
    ).toThrow();
  });

  test("missing prop", () => {
    expect(() =>
      extract(`\
        useFlag({
          id: "facbc432-9494-4810-8f61-c4fb47dde2a5",
        });
      `)
    ).toThrow();
  });

  test("invalid argument type", () => {
    expect(() =>
      extract(`\
        useFlag("60779262-f684-483d-8c8d-ef1c09bdd03d");
      `)
    ).toThrow();
  });

  test("missing argument", () => {
    expect(() =>
      extract(`\
        useFlag();
      `)
    ).toThrow();
  });
});
