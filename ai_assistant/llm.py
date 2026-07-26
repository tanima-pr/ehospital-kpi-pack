"""
llm.py — one tiny wrapper so every other script calls the model the same way.
Works with Google Gemini (FREE, no credit card), Anthropic (Claude), or OpenAI.
Set PROVIDER in your .env file, put your key there too (see .env.example).
"""
import os
from dotenv import load_dotenv
load_dotenv()

PROVIDER = os.getenv("PROVIDER", "gemini").lower()  # "gemini", "anthropic", or "openai"


def ask(system, user, temperature=0.0, max_tokens=1024):
    """Send a system + user prompt, return the model's text reply."""
    if PROVIDER == "gemini":
        # Gemini offers a free API. We talk to it through the OpenAI library
        # by pointing at Google's OpenAI-compatible address — no extra install.
        from openai import OpenAI
        client = OpenAI(
            api_key=os.environ["GEMINI_API_KEY"],
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
        resp = client.chat.completions.create(
            model="gemini-flash-lite-latest",   # free tier ~1,000 req/day (vs 20 for full flash)
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": user}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        text = resp.choices[0].message.content
        u = resp.usage
        usage = (u.prompt_tokens, u.completion_tokens)
    elif PROVIDER == "anthropic":
        from anthropic import Anthropic
        client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        resp = client.messages.create(
            model="claude-sonnet-4-5",          # cheap + strong; swap if needed
            system=system,
            messages=[{"role": "user", "content": user}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        text = resp.content[0].text
        usage = (resp.usage.input_tokens, resp.usage.output_tokens)
    else:  # openai
        from openai import OpenAI
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        resp = client.chat.completions.create(
            model="gpt-4o-mini",                # cheap + capable
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": user}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        text = resp.choices[0].message.content
        u = resp.usage
        usage = (u.prompt_tokens, u.completion_tokens)

    return text, usage


if __name__ == "__main__":
    reply, (inp, out) = ask(
        system="You are a concise assistant.",
        user="In one sentence, what is a system prompt?",
    )
    print(reply)
    print(f"\n[tokens] input={inp} output={out}")
