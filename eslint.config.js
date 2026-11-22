import ts from "typescript-eslint";
import svelte from "eslint-plugin-svelte";

export default [
  ...ts.configs.recommended,
  ...svelte.configs.recommended,
  {
    ignores: ["dist/", "node_modules/", "data/", "public/data/"],
  },
];
