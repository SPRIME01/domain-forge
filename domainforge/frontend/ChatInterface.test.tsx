import { render, screen, fireEvent, waitFor, cleanup } from "@testing-library/react";
import { describe, test, expect, afterEach, vi } from "vitest";
import axios from "axios";
import ChatInterface from "./ChatInterface";

/**
 * Type definitions for Chat API responses
 */
interface IChatResponse {
  messages: string[];
}

// Use Vitest's mocking functionality
vi.mock("axios", () => ({
  default: {
    post: vi.fn(),
  },
}));

const mockedAxios = axios as unknown as { post: ReturnType<typeof vi.fn> };

/**
 * Test suite for the ChatInterface component
 * Tests user input handling, message sending, and error handling
 */
describe("ChatInterface Component", () => {
  // Cleanup after each test
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  test("should render chat interface with initial empty state", () => {
    render(<ChatInterface />);

    const inputField = screen.getByRole("textbox", { name: /message input/i });
    const sendButton = screen.getByRole("button", { name: /send/i });

    expect(inputField, "Input field should be rendered").toBeInTheDocument();
    expect(sendButton, "Send button should be rendered").toBeInTheDocument();
    expect(inputField, "Input field should be empty").toHaveValue("");
  });

  test("should allow entering text in the input field", () => {
    render(<ChatInterface />);

    // Get the input field and type into it
    const inputElement = screen.getByRole("textbox", { name: /message input/i });
    fireEvent.change(inputElement, { target: { value: "Hello AI" } });

    expect(inputElement, "Input field should contain entered text").toHaveValue("Hello AI");
  });

  test("should send message when button is clicked and display response", async () => {
    // Mock API response
    const mockResponse: IChatResponse = {
      messages: ["I am the AI assistant. How can I help?"],
    };

    mockedAxios.post.mockResolvedValueOnce({
      data: mockResponse,
    });

    render(<ChatInterface />);

    // Enter text and click send
    const inputElement = screen.getByRole("textbox", { name: /message input/i });
    const sendButton = screen.getByRole("button", { name: /send/i });

    fireEvent.change(inputElement, { target: { value: "Hello AI" } });
    fireEvent.click(sendButton);

    // Verify axios post was called correctly
    expect(mockedAxios.post).toHaveBeenCalledWith("/api/chat/send", { content: "Hello AI" });
    expect(mockedAxios.post).toHaveBeenCalledTimes(1);

    // Wait for AI response to appear
    await waitFor(() => {
      const userMessage = screen.getByText(/you: hello ai/i);
      const aiResponse = screen.getByText(/ai: i am the ai assistant/i);

      expect(userMessage, "User message should be displayed").toBeInTheDocument();
      expect(aiResponse, "AI response should be displayed").toBeInTheDocument();
    });

    // Check that input was cleared after sending
    expect(inputElement, "Input field should be cleared after sending").toHaveValue("");
  });

  test("should send message when Enter key is pressed", async () => {
    // Mock API response
    const mockResponse: IChatResponse = {
      messages: ["How can I help with your domain model?"],
    };

    mockedAxios.post.mockResolvedValueOnce({
      data: mockResponse,
    });

    render(<ChatInterface />);

    // Enter text and press Enter
    const inputElement = screen.getByRole("textbox", { name: /message input/i });
    fireEvent.change(inputElement, { target: { value: "Create a User entity" } });
    fireEvent.keyPress(inputElement, { key: "Enter", code: "Enter", charCode: 13 });

    // Verify axios post was called correctly
    expect(mockedAxios.post).toHaveBeenCalledWith("/api/chat/send", {
      content: "Create a User entity",
    });
    expect(mockedAxios.post).toHaveBeenCalledTimes(1);

    // Wait for response
    await waitFor(() => {
      const aiResponse = screen.getByText(/ai: how can i help with your domain model/i);
      expect(
        aiResponse,
        "AI response should be displayed after pressing Enter"
      ).toBeInTheDocument();
    });
  });

  test("should handle API errors gracefully", async () => {
    // Mock API error response
    const networkError = new Error("Network Error");
    mockedAxios.post.mockRejectedValueOnce(networkError);

    // Update spy implementation
    const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});

    render(<ChatInterface />);

    // Enter text and click send
    const inputElement = screen.getByRole("textbox", { name: /message input/i });
    const sendButton = screen.getByRole("button", { name: /send/i });

    fireEvent.change(inputElement, { target: { value: "Hello" } });
    fireEvent.click(sendButton);

    // Verify error was logged
    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalled();
      expect(consoleSpy).toHaveBeenCalledWith(expect.any(String), networkError);
    });

    // Verify user message still appears (even though API failed)
    const userMessage = screen.getByText(/you: hello/i);
    expect(userMessage, "User message should appear even when API fails").toBeInTheDocument();

    // Clean up spy
    consoleSpy.mockRestore();
  });
});
