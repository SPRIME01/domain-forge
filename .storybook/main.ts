import type { StorybookConfig } from "@storybook/react-vite";
import { resolve } from "path";

const config: StorybookConfig = {
  stories: [
    "../domainforge/frontend/**/*.stories.@(js|jsx|ts|tsx)",
    "../domainforge/frontend/**/*.mdx",
  ],
  addons: [
    "@storybook/addon-links",
    "@storybook/addon-essentials",
    "@storybook/addon-interactions",
    "@storybook/addon-docs",
  ],
  framework: {
    name: "@storybook/react-vite",
    options: {},
  },
  docs: {
    autodocs: "tag",
    defaultName: "Documentation",
  },
  typescript: {
    reactDocgen: "react-docgen-typescript",
    check: true,
  },
  outputDir: resolve(__dirname, "../site/storybook"),
};

export default config;
