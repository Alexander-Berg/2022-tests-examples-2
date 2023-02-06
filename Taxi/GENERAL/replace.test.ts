import { describe, expect, test } from "@jest/globals";
import { replace } from "./replace";

describe("replace", () => {
  test("message props replace", () => {
    expect(
      replace(
        `\
import { Message } from "@superweb/intl";
export const Component = () => <Message id="id" context="context" default="default" />;`,
        {
          id: "default from tanker",
        }
      )
    ).toEqual(
      `\
import { Message } from "@superweb/intl";
export const Component = () => <Message id="id" context="context" default="default from tanker" />;`
    );
  });

  test("multiple keys", () => {
    expect(
      replace(
        `\
import { Message } from "@superweb/intl";
export const Component1 = () => <Message id="id1" context="context" default="default1" />;
export const Component2 = () => <Message id="id2" context="context" default="default2" />;
export const Component3 = () => <Message id="id" context="context" default="default" />;`,
        {
          id1: "default from tanker1",
          id2: "default from tanker2",
        }
      )
    ).toEqual(
      `\
import { Message } from "@superweb/intl";
export const Component1 = () => <Message id="id1" context="context" default="default from tanker1" />;
export const Component2 = () => <Message id="id2" context="context" default="default from tanker2" />;
export const Component3 = () => <Message id="id" context="context" default="default" />;`
    );
  });

  test("template literal replace", () => {
    expect(
      replace(
        `\
import { Message } from "@superweb/intl";
export const Component = () => <Message id="id" context="context" default={\`default\`}  />;`,
        {
          id: "default from tanker",
        }
      )
    ).toEqual(
      `\
import { Message } from "@superweb/intl";
export const Component = () => <Message id="id" context="context" default={\`default from tanker\`} />;`
    );
  });

  test("message params properties replace", () => {
    expect(
      replace(
        `\
import { useMessage } from "@superweb/intl";
export const useText = () => {
  const message = useMessage();
  return message({
    id: "id",
    context: "context",
    default: "default"
  });
};`,
        {
          id: "default from tanker",
        }
      )
    ).toEqual(`\
import { useMessage } from "@superweb/intl";
export const useText = () => {
  const message = useMessage();
  return message({
    id: "id",
    context: "context",
    default: "default from tanker"
  });
};`);
  });

  test("message params replace only one key", () => {
    expect(
      replace(
        `\
import { useMessage } from "@superweb/intl";
export const useText = () => {
  const message = useMessage();
  const mes1 = message({
    id: "id",
    context: "context",
    default: "default"
  });
  const mes2 = message({
    id: "id2",
    context: "context2",
    default: "default2"
  });
};`,
        {
          id: "default from tanker",
        }
      )
    ).toEqual(`\
import { useMessage } from "@superweb/intl";
export const useText = () => {
  const message = useMessage();
  const mes1 = message({
    id: "id",
    context: "context",
    default: "default from tanker"
  });
  const mes2 = message({
    id: "id2",
    context: "context2",
    default: "default2"
  });
};`);
  });

  test("handle escape sequences", () => {
    expect(
      replace(
        `\
import { Message } from "@superweb/intl";
export const Component = () => <Message id="id" context="context" default={\`default\`}  />;`,
        {
          id: `default from tanker\n`,
        }
      )
    ).toEqual(
      `\
import { Message } from "@superweb/intl";
export const Component = () => <Message id="id" context="context" default={\`default from tanker\n\`} />;`
    );
  });

  test("preserve escaped backslashes", () => {
    expect(
      replace(
        `\
import { Message } from "@superweb/intl";
export const Component = () => <Message id="id" context="context" default={\`default\`}  />;`,
        {
          id: `default from tanker\\n`,
        }
      )
    ).toEqual(
      `\
import { Message } from "@superweb/intl";
export const Component = () => <Message id="id" context="context" default={\`default from tanker\\n\`} />;`
    );
  });
});
