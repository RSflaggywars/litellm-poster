# litellm-poster

A tiny CLI tool that asks a [LiteLLM](https://docs.litellm.ai/) proxy a question
and POSTs the AI's answer to any webhook URL you choose — Discord, Slack
(incoming webhook format), n8n, a custom server, etc.

No dependencies. Python 3.8+ standard library only.

## Setup

```sh
# optional: set once instead of passing flags every time
setx LITELLM_API_BASE "https://your-litellm-proxy.example.com"
setx LITELLM_API_KEY "sk-..."
setx LITELLM_MODEL "gpt-4o-mini"
```

(Windows `setx` — on Linux/macOS use `export` in your shell profile.)

## Usage

```sh
python poster.py "What is the capital of France?" --webhook https://discord.com/api/webhooks/...
```

Flags:

| Flag | Description |
|---|---|
| `--webhook URL` | **required** — where to POST the answer |
| `--api-base URL` | LiteLLM proxy URL (or `LITELLM_API_BASE`) |
| `--api-key KEY` | proxy key (or `LITELLM_API_KEY`) |
| `--model NAME` | model name (or `LITELLM_MODEL`, default `gpt-4o-mini`) |
| `--system TEXT` | optional system prompt |
| `--field NAME` | webhook JSON field, default `text` — use `content` for Discord |
| `--dry-run` | print the answer instead of posting |

## Examples

```sh
# Discord webhook (Discord expects the "content" field)
python poster.py "Summarize today's top news headline" \
  --webhook https://discord.com/api/webhooks/123/abc \
  --field content

# Test without posting
python poster.py "Say hello" --webhook http://localhost:9999/hook --dry-run
```

## Webhook payload

The tool POSTs JSON: `{"<field>": "<AI answer>"}`.

- Discord: `--field content`
- Generic/custom: default `--field text` works if your endpoint accepts `{"text": ...}`

## License

MIT
