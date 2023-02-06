import { ruleTester } from "../utils";
import { rule } from "./organize-imports";

ruleTester.run("organize-imports", rule, {
  valid: [
    {
      code: `
        import "./side-effects";
        import "@scoped/package";
        import "package";
        import "#subpath-import";
        import "../parent";
        import "./sibling";
      `,
    },
  ],
  invalid: [],
});
