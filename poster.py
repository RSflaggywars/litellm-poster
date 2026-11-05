#!/usr/bin/env python3
"""litellm-poster - ask a LiteLLM proxy and POST the answer to a webhook.

No third-party dependencies - uses only the Python standard library.

Configuration (flags override env vars):
  LITELLM_API_BASE   e.g. https://your-litellm-proxy.example.com
  LITELLM_API_KEY    proxy key (optional if your proxy is open)
  LITELLM_MODEL      default model name
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request


def post_json(url, payload, headers=None, timeout=120):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", **(headers or {})},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} from {url}: {body[:500]}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Could not reach {url}: {e.reason}") from e


def ask_litellm(api_base, api_key, model, prompt, system=None):
    url = api_base.rstrip("/") + "/chat/completions"
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    payload = {"model": model, "messages": messages}
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    _, body = post_json(url, payload, headers)
    try:
        data = json.loads(body)
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        raise RuntimeError(f"Unexpected LiteLLM response: {body[:500]}") from e


def main():
    p = argparse.ArgumentParser(
        description="Ask a LiteLLM proxy a question and POST the answer to a webhook."
    )
    p.add_argument("prompt", help="the prompt to send to the model")
    p.add_argument("--webhook", required=True,
                   help="URL to POST the AI's answer to (Discord webhook, n8n, etc.)")
    p.add_argument("--api-base",
                   default=os.environ.get("LITELLM_API_BASE"),
                   help="LiteLLM proxy base URL (or set LITELLM_API_BASE)")
    p.add_argument("--api-key", default=os.environ.get("LITELLM_API_KEY"),
                   help="LiteLLM API key (or set LITELLM_API_KEY)")
    p.add_argument("--model", default=os.environ.get("LITELLM_MODEL", "gpt-4o-mini"),
                   help="model name (or set LITELLM_MODEL)")
    p.add_argument("--system", help="optional system prompt")
    p.add_argument("--field", default="text",
                   help="JSON field name for the webhook payload (default: text; "
                        "use 'content' for Discord)")
    p.add_argument("--dry-run", action="store_true",
                   help="print the answer instead of posting it")
    args = p.parse_args()

    if not args.api_base:
        p.error("missing LiteLLM proxy URL: pass --api-base or set LITELLM_API_BASE")

    try:
        answer = ask_litellm(args.api_base, args.api_key, args.model,
                             args.prompt, args.system)
    except RuntimeError as e:
        print(f"Error calling LiteLLM: {e}", file=sys.stderr)
        return 1

    if args.dry_run:
        print(answer)
        return 0

    status, body = post_json(args.webhook, {args.field: answer})
    print(f"Posted to webhook (HTTP {status})")
    if body and body not in ("ok", "{}"):
        print(body[:200])
    return 0


if __name__ == "__main__":
    sys.exit(main())
