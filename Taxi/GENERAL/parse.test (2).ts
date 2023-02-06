import { parse, ParserOptions } from "@babel/parser";
import { describe, expect, test } from "@jest/globals";
import { parseCode } from "./parse";

const options: ParserOptions = {
  sourceType: "module",
  plugins: ["typescript", "jsx"],
};

describe("Message", () => {
  describe("ok", () => {
    test("basic", () => {
      const messages = parseCode(
        parse(
          `\
import { Message } from "@superweb/intl";
<Message id="id" context="context" default="default" />
                 `,
          options
        )
      );
      expect(messages.length).toBe(1);
      expect(messages[0]!.id.node.start).toBe(54);
      expect(messages[0]!.id.node.end).toBe(58);
      expect(messages[0]!.id.node.value).toBe("id");
      expect(messages[0]!.context.node.value).toBe("context");
      expect(messages[0]!.default.node.type).toBe("StringLiteral");
      expect(
        messages[0]!.default.node.type === "StringLiteral"
          ? messages[0]!.default.node.value
          : messages[0]!.default.node.value.raw
      ).toBe("default");
    });

    test("template literal", () => {
      const messages = parseCode(
        parse(
          `\
import { Message } from "@superweb/intl";
<Message id="id" context="context" default={\`default\`} />
         `,
          options
        )
      );
      expect(messages.length).toBe(1);
      expect(messages[0]!.id.node.start).toBe(54);
      expect(messages[0]!.id.node.end).toBe(58);
      expect(messages[0]!.id.node.value).toBe("id");
      expect(messages[0]!.context.node.value).toBe("context");
      expect(messages[0]!.default.node.type).toBe("TemplateElement");
      expect(
        messages[0]!.default.node.type === "StringLiteral"
          ? messages[0]!.default.node.value
          : messages[0]!.default.node.value.raw
      ).toBe("default");
    });
  });

  describe("error", () => {
    test("missing attribute", () => {
      expect(() =>
        parseCode(
          parse(
            `\
import { Message } from "@superweb/intl";
<Message id="id" default="default"/>`,
            options
          )
        )
      ).toThrow();
    });

    test("invalid attributes", () => {
      expect(() =>
        parseCode(
          parse(
            `\
import { Message } from "@superweb/intl";
<Message id={1} context="context" default="default" />
           `,
            options
          )
        )
      ).toThrow();
    });

    test("unextractable", () => {
      expect(() =>
        parseCode(
          parse(
            `\
import { Message } from "@superweb/intl";
<Message id="id" context="context" default={\`def\${a}ult\`} />
           `,
            options
          )
        )
      ).toThrow();
    });
  });
});

describe("useMessages", () => {
  describe("ok", () => {
    test("basic", () => {
      const messages = parseCode(
        parse(
          `\
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
};`,
          options
        )
      );
      expect(messages.length).toBe(2);
      expect(messages[0]!.id.node.start).toBe(155);
      expect(messages[0]!.id.node.end).toBe(160);
      expect(messages[0]!.id.node.value).toBe("id1");
      expect(messages[0]!.context.node.value).toBe("context1");
      expect(messages[0]!.default.node.type).toBe("StringLiteral");

      expect(
        messages[0]!.default.node.type === "StringLiteral"
          ? messages[0]!.default.node.value
          : messages[0]!.default.node.value.raw
      ).toBe("default1");

      expect(messages[1]!.id.node.value).toBe("id2");
      expect(messages[1]!.context.node.value).toBe("context2");
      expect(messages[1]!.default.node.type).toBe("StringLiteral");
      expect(
        messages[1]!.default.node.type === "StringLiteral"
          ? messages[1]!.default.node.value
          : messages[1]!.default.node.value.raw
      ).toBe("default2");
    });

    test("no false positives", () => {
      expect(
        parseCode(
          parse(
            `\
import { Message } from "ui";
const useMessage = (message: string) => {};
<Message />;
useMessage("message");
`,
            options
          )
        )
      ).toEqual([]);
    });

    test("import alias", () => {
      const messages = parseCode(
        parse(
          `\
import { 
  Message as IntlMessage,
  useMessage as useIntlMessage
} from "@superweb/intl";

<IntlMessage
  id="id1"
  context="context1"
  default="default1"
/>;

const message = useIntlMessage();

message({
  id: "id2",
  context: "context2",
  default: "default2",
});       
  `,
          options
        )
      );
      expect(messages.length).toBe(2);
      expect(messages[0]!.id.node.start).toBe(111);
      expect(messages[0]!.id.node.end).toBe(116);
      expect(messages[0]!.id.node.value).toBe("id1");
      expect(messages[0]!.context.node.value).toBe("context1");
      expect(messages[0]!.default.node.type).toBe("StringLiteral");
      expect(
        messages[0]!.default.node.type === "StringLiteral"
          ? messages[0]!.default.node.value
          : messages[0]!.default.node.value.raw
      ).toBe("default1");

      expect(messages[1]!.id.node.value).toBe("id2");
      expect(messages[1]!.context.node.value).toBe("context2");
      expect(messages[1]!.default.node.type).toBe("StringLiteral");
      expect(
        messages[1]!.default.node.type === "StringLiteral"
          ? messages[1]!.default.node.value
          : messages[1]!.default.node.value.raw
      ).toBe("default2");
    });

    test("star import", () => {
      const messages = parseCode(
        parse(
          `\
import * as intl from "@superweb/intl";

<intl.Message
  id="id1"
  context="context1"
  default="default1"
/>;

const message = intl.useMessage();

message({
  id: "id2",
  context: "context2",
  default: "default2",
});
`,
          options
        )
      );
      expect(messages.length).toBe(2);
      expect(messages[0]!.id.node.start).toBe(60);
      expect(messages[0]!.id.node.end).toBe(65);
      expect(messages[0]!.id.node.value).toBe("id1");
      expect(messages[0]!.context.node.value).toBe("context1");
      expect(messages[0]!.default.node.type).toBe("StringLiteral");
      expect(
        messages[0]!.default.node.type === "StringLiteral"
          ? messages[0]!.default.node.value
          : messages[0]!.default.node.value.raw
      ).toBe("default1");

      expect(messages[1]!.id.node.value).toBe("id2");
      expect(messages[1]!.context.node.value).toBe("context2");
      expect(messages[1]!.default.node.type).toBe("StringLiteral");
      expect(
        messages[1]!.default.node.type === "StringLiteral"
          ? messages[1]!.default.node.value
          : messages[1]!.default.node.value.raw
      ).toBe("default2");
    });
  });
});
