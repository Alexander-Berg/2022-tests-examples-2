import { ruleTester } from "../utils";
import { rule } from "./no-react-type";

ruleTester.run("no-react-type", rule, {
  valid: [
    {
      code: "React.useRef()",
    },
  ],
  invalid: [
    {
      code: "let Component: React.ComponentType<Props>;",
      errors: [
        {
          messageId: "noReactType",
          data: { name: "ComponentType" },
        },
      ],
    },
    {
      code: `type Key = React.Attributes["key"]`,
      errors: [
        {
          messageId: "noReactType",
          data: { name: "Attributes" },
        },
      ],
    },
    {
      code: "(props: { children: React.ReactNode }) => {}",
      errors: [
        {
          messageId: "noReactType",
          data: { name: "ReactNode" },
        },
      ],
    },
  ],
});
