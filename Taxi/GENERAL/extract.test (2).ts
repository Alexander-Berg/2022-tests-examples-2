import { describe, expect, test } from "@jest/globals";
import { extract } from "./extract";

describe("extract", () => {
  test("message props extract", () => {
    const messages = extract(
      `\
import { Message } from "@superweb/intl";
<Message id="id" context="context" default="default" />
`
    );
    expect(messages).toEqual([
      {
        id: "id",
        context: "context",
        default: "default",
      },
    ]);
  });

  test("message params properties extract", () => {
    const messages = extract(`\
import { useMessage } from "@superweb/intl";
export const useText = () => {
const message = useMessage();
  return {
    msg1: message({
      id: "id1",
      context: "context1",
      default: "default1",
      values: { param: "param" }
    }),
    msg2: message({
      id: "id2",
      context: "context2",
      default: "default2"
    }),
  };
};`);
    expect(messages).toEqual([
      {
        id: "id1",
        context: "context1",
        default: "default1",
      },
      {
        id: "id2",
        context: "context2",
        default: "default2",
      },
    ]);
  });

  test("multiple extract", () => {
    const messages = extract(
      `\
import { Message, useMessage } from "@superweb/intl";
const message = useMessage();
const text = message({
  id: "id1",
  context: "context1",
  default: "default1",
  values: { param: "param" }
});
<Message id="id2" context="context2" default="default2" />
`
    );
    expect(messages).toEqual([
      {
        id: "id1",
        context: "context1",
        default: "default1",
      },
      {
        id: "id2",
        context: "context2",
        default: "default2",
      },
    ]);
  });

  test("template literal extract", () => {
    const messages = extract(
      `\
import { Message } from "@superweb/intl";
<Message id="id" context="context" default={\`default\`} />
`
    );
    expect(messages).toEqual([
      {
        id: "id",
        context: "context",
        default: "default",
      },
    ]);
  });
});
