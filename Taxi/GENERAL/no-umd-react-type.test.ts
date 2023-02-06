import { ruleTester } from "../utils";
import { rule } from "./no-umd-react-type";

ruleTester.run("no-umd-react-type", rule, {
  valid: [
    {
      code: `(props: { children: React.ReactNode }) => null;`,
    },
    {
      parserOptions: { sourceType: "module" },
      code: `import React from "react"; (props: { children: React.ReactNode }) => null;`,
    },
  ],
  invalid: [
    {
      parserOptions: { sourceType: "module" },
      code: `(props: { children: React.ReactNode }) => null;`,
      errors: [{ messageId: "noUmdReactType" }],
    },
  ],
});
