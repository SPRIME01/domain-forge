import React from "react";
import type { Preview } from "@storybook/react";
import { MantineProvider, createTheme } from "@mantine/core";

const theme = createTheme({
  primaryColor: "blue",
});

const preview: Preview = {
  parameters: {
    actions: { argTypesRegex: "^on[A-Z].*" },
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
  },
  decorators: [
    Story => (
      <MantineProvider theme={theme}>
        <Story />
      </MantineProvider>
    ),
  ],
};

export default preview;
