# DeepSeek API Kit - Comprehensive Documentation

## Overview

**DeepSeek API Kit** is a lightweight, OpenAI-compatible proxy server that provides seamless access to DeepSeek's language models through a familiar REST API interface. It features automatic session management, persistent chat history, and intelligent error recovery to ensure a reliable and smooth user experience.

The project is designed to be easily deployable and usable, whether you're integrating it into existing applications or using it as a standalone chat service.

---

## Features

- **OpenAI-Compatible API** – Drop-in replacement for OpenAI's `/v1/chat/completions` endpoint.
- **Persistent Chat Sessions** – Maintain conversation history across requests with automatic session persistence.
- **Auto-Reset Mechanism** – Automatically recovers from session expiry or invalid responses by resetting the session without manual intervention.
- **Streaming & Non-Streaming Modes** – Full support for both real-time streaming and standard JSON responses.
- **Model Selection** – Choose from four model variants:
  - `thinking_not_search` – reasoning enabled, no internet search.
  - `thinking_search` – reasoning enabled with internet search.
  - `not_thinking_not_search` – no reasoning, no search.
  - `not_thinking_search` – no reasoning, with search.
- **Utility Scripts** – Provided `send_with_session.py` for easy testing and interaction with the proxy.
- **Easy Setup** – Minimal configuration via environment variables.

---

## Requirements

- Python 3.8+
- pip (Python package manager)
- (Optional) Virtual environment (recommended)

---

## Installation

1. **Clone the repository** (or download the source):
   ```bash
   git clone https://github.com/Ryan-PG/deepseek-api-kit.git
   cd deepseek-api-kit
   ```

2. **Create and activate a virtual environment** (optional but recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and add your DeepSeek API key:
     ```
     DEEPSEEK_API_KEY=your_api_key_here
     ```

---

## Configuration

| Environment Variable | Description |
|----------------------|-------------|
| `DEEPSEEK_API_KEY`   | Your DeepSeek API key (required). |
| `SESSION_FILE`       | (Optional) Path to the session ID file (default: `.session_id`). |
| `SESSION_DATA_FILE`  | (Optional) Path to the session data JSON file (default: `.session_data.json`). |

All configuration can be set in the `.env` file or directly in the environment.

---

## Project Structure

```
deepseek-api-kit/
├── openai_proxy/
│   ├── __init__.py
│   └── main.py                # FastAPI application (main server)
├── common/
│   ├── __init__.py
│   ├── api.py                 # DeepSeek API client
│   ├── bypass.py              # Cloudflare bypass utilities
│   ├── CloudflareBypasser.py  # Cloudflare challenge solver
│   ├── config.py              # Configuration loader
│   ├── cookies.json           # Cookie storage
│   ├── pow.py                 # Proof-of-work helpers
│   ├── run_and_get_cookies.py # Cookie acquisition script
│   ├── server.py              # Server helpers
│   └── wasm/                  # WebAssembly modules
├── deepseek_chat/
│   ├── __init__.py
│   ├── main.py                # DeepSeek chat interface
│   ├── panel.html             # Web chat panel (optional)
│   └── session_store.py       # Session storage utilities
├── .env.example               # Example environment file
├── .session_data.json         # Persistent session data (auto-generated)
├── .session_id                # Session ID file (auto-generated)
├── deepseek-api.bat           # Windows batch script to run the server
├── example.py                 # Example usage script
├── requirements.txt           # Python dependencies
├── send_with_session.py       # Utility to send requests with session persistence
├── test_*.py                  # Test scripts
└── memory.md                  # This documentation file
```

---

## API Usage

### Base URL
`http://localhost:8000` (default port, configurable in code)

### Endpoints

#### `POST /v1/chat/completions`
This endpoint mirrors the OpenAI API specification with additional session management features.

**Request Body (JSON):**

| Field | Type | Description |
|-------|------|-------------|
| `messages` | `List[Message]` | Array of message objects with `role` and `content`. |
| `model` | `string` | One of the four model variants (see Features). Default: `thinking_not_search`. |
| `stream` | `boolean` | Enable streaming responses. Default: `false`. |
| `session_id` | `string` (optional) | Provide a specific session ID to continue a conversation. |
| `temperature` | `float` (optional) | Sampling temperature (not fully implemented). |
| `max_tokens` | `integer` (optional) | Max tokens (not fully implemented). |

**Message Object:**

```json
{
  "role": "user",          // "user", "assistant", or "system"
  "content": "Hello, world!"
}
```

**Example Request (Non-Streaming):**

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "What is the capital of France?"}],
    "model": "thinking_not_search",
    "stream": false
  }'
```

**Example Response (Non-Streaming):**

```json
{
  "id": "chatcmpl-<session_id>",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "thinking_not_search",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "The capital of France is Paris.",
        "reasoning_content": "(optional thinking process)"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0
  },
  "session_id": "abc-123",
  "response_message_id": 42
}
```

**Example Request (Streaming):**

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Tell me a joke."}],
    "model": "thinking_search",
    "stream": true
  }'
```

Streaming responses are Server-Sent Events (SSE) with `data:` prefixes, compatible with OpenAI's streaming format.

---

#### `GET /v1/models`
Returns the list of available models.

**Example Response:**

```json
{
  "object": "list",
  "data": [
    {"id": "thinking_not_search", "object": "model", "created": 1677610602, "owned_by": "you"},
    {"id": "thinking_search", "object": "model", "created": 1677610602, "owned_by": "you"},
    {"id": "not_thinking_not_search", "object": "model", "created": 1677610602, "owned_by": "you"},
    {"id": "not_thinking_search", "object": "model", "created": 1677610602, "owned_by": "you"}
  ]
}
```

---

## Session Management

The proxy automatically handles chat sessions to maintain conversation history. Here's how it works:

- **Session Creation** – When no `session_id` is provided, the server creates a new session via the DeepSeek API and stores the ID in memory and on disk (`.session_data.json` and `.session_id`).
- **Persistence** – Sessions are saved to files, so they survive server restarts. This allows you to continue conversations even after restarting the proxy.
- **History** – Each session tracks the last `response_message_id`, enabling the server to carry the conversation forward with each new request.
- **Session ID Usage** – Clients can provide a `session_id` in requests to resume a specific conversation. If no session exists with that ID, the server will ignore it and use the current active session.

---

## Auto-Reset Mechanism (Error Recovery)

The server includes a robust auto-reset feature to handle common failure scenarios automatically:

1. **Session Expiry / Invalid Session** – If the DeepSeek API returns an error related to an invalid or expired session, the proxy detects this (via keyword matching) and resets the session.
2. **Empty or Unparsable Responses** – If the DeepSeek API returns an empty response or a malformed/unparsable payload, the system treats this as a session error and triggers a reset.
3. **Detection Keywords** – The `is_session_error()` function scans error messages for keywords like `"session"`, `"not found"`, `"invalid"`, `"expired"`, `"empty response"`, `"unparsable"`, etc.
4. **Retry Logic** – On detecting such an error, the server:
   - Clears the in-memory session.
   - Creates a new session via `api.create_chat_session()`.
   - Updates `.session_data.json` and `.session_id` with the new session.
   - For non-streaming requests, it retries the original request automatically (up to one retry).
   - For streaming requests, it sends an error chunk back to the client, informing them to retry with the new session.

This ensures that the proxy remains functional without requiring manual intervention (e.g., deleting files and restarting).

---

## Utility Scripts

### `send_with_session.py`
This script provides a command-line interface for sending requests while automatically managing session persistence. It reads the current session ID from `.session_id` and reuses it across requests.

**Usage:**
```bash
python send_with_session.py "Your message here"
```

It will print the response from the proxy, and if the session is reset, it updates the session files accordingly.

### `deepseek-api.bat` (Windows)
A simple batch file to start the FastAPI server. You can use it as an entry point.

---

## Testing

Several test scripts are included to verify functionality:

- `test_session.py` – Basic session creation and usage.
- `test_session_fixed.py` – Session handling with error recovery.
- `test_conversation.py` – Multi-turn conversation test.
- `example.py` – Demonstrates basic usage of the proxy.

You can run these individually to ensure the system works as expected.

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **Server won't start** | Check that `DEEPSEEK_API_KEY` is set in `.env` and that all dependencies are installed. |
| **"Session not found" errors** | The auto-reset mechanism should handle this automatically. If not, delete `.session_data.json` and `.session_id` and restart the server. |
| **Empty responses from DeepSeek** | The server will automatically reset the session and retry. If the issue persists, check your internet connection and DeepSeek API availability. |
| **Cloudflare challenges** | The `common/bypass.py` module attempts to solve Cloudflare challenges. If you encounter issues, you may need to manually obtain cookies and place them in `common/cookies.json`. |

### Logging

The server logs all requests and responses with timestamps. Check the console output for debugging information.

---

## License

This project is open-source and available under the [MIT License](LICENSE).

---

## Contributing

Contributions are welcome! Please submit issues and pull requests on the [GitHub repository](https://github.com/Ryan-PG/deepseek-api-kit).

---

## Acknowledgments

- DeepSeek for providing the language model API.
- FastAPI for the web framework.
- All contributors and users of this project.

---

*Last Updated: June 2026*