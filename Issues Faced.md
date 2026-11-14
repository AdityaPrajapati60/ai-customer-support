# Issues Faced and How They Were Solved

This document records issues encountered while setting up and running the
Harbor & Pine customer-support email processor, along with the fixes or recovery
steps.

## AI provider configuration

**Issue:** Requests to the OpenRouter API failed during provider setup.

**Resolution:** The application is configured to use Groq through its
OpenAI-compatible endpoint. Keep the provider key, endpoint, and model from the
same provider together. The current settings are `GROQ_API_KEY`,
`https://api.groq.com/openai/v1`, and `openai/gpt-oss-20b` by default. Do not
send an OpenRouter key to the Groq endpoint. If changing providers, update all
three settings together.

## Test 20: model did not call a required tool

**Issue:** Test 19 successfully generated a paddle-board recommendation, but
test 20 failed with `Tool choice is required, but model did not call a tool`.
The logs also showed malformed or unavailable `get_section` tool calls. The
reply was never sent.

**Resolution:** The reply agent no longer relies on the model to call
knowledge-base tools. The application loads the required sections and includes
them in the prompt, then requests the reply as prompted structured output. This
removes the tool-choice dependency from reply generation.

## Reply rejected for missing punctuation

**Issue:** A generated reply failed the output validator because it did not
end with sentence-ending punctuation. The retry also failed, exhausting the
output retry budget before Gmail sent the reply.

**Resolution:** The support agent now allows up to three output retries. The
validator still rejects empty, incomplete, or otherwise disallowed replies;
the additional retries give the model a bounded opportunity to correct its
draft.

## Gmail profile returned HTTP 500

**Issue:** Gmail returned HTTP 500 with `backendError` and “Unknown Error”
while requesting the account profile.

**Resolution:** This was a transient Gmail API backend failure. The poller logs
the error and continues polling, so let it retry rather than changing valid
credentials for a temporary server error.

## Failed email was not picked up again

**Issue:** After repeated processing failures, an email can reach the retry
limit and receive the `ai-processed` label. The poller searches for inbox
messages without this label, so that email will not be picked up automatically.

**Resolution:** After correcting the underlying issue, remove the
`ai-processed` label from the failed message so the poller can retry it.

## Reply looked shorter in Gmail than in the terminal

**Issue:** The terminal logged the full reply and marked the message
`processed`, but the reply looked shorter in Gmail's normal message view.

**What we verified:** The pipeline calls Gmail's send API with the complete
reply body, and `EmailMessage.set_content(body)` places that body in the email.
The `processed` log is written only after the send call succeeds. The sent
message's original MIME content was not checked, so the available evidence does
not show that Gmail received a truncated body.

**Resolution/check:** In Gmail, expand any collapsed or trimmed content in the
message view. Use **Show original** to inspect the actual sent message body.
If the original contains the full reply, no application fix is needed; Gmail's
normal view was hiding part of the content. If the original is also truncated,
capture that message and compare its body with the terminal's `processed`
reply before changing the sending code.

## `ModuleNotFoundError: No module named 'dotenv'`

**Issue:** Python could not import `dotenv`.

**Resolution:** The import is provided by the `python-dotenv` package. Sync the
project dependencies and verify the import using the project environment:

```powershell
uv sync
uv run python -c "import dotenv; print(dotenv.__file__)"
```

## Watcher used the wrong Python interpreter on Windows

**Issue:** A watcher child process could resolve a system Python that did not
have the project dependencies installed.

**Resolution:** Run both the watcher and its child process through `uv`:

```powershell
uv run watchfiles "uv run python -m app.poller" app .env
```

## PowerShell could not find `scoop`

**Issue:** PowerShell did not recognize the `scoop` command because Scoop's
shims directory was not on the current session's `PATH`.

**Resolution:** Use the existing Scoop script directly or add its shims
directory to the current session's `PATH`. Do not reinstall an existing Scoop
installation:

```powershell
& "$HOME\scoop\shims\scoop.ps1" --version
$env:Path += ";$HOME\scoop\shims"
```

## Code changes did not affect the running poller

**Issue:** A running watcher or poller can keep executing code loaded before a
fix was made. Logs may therefore continue to show old tool-calling behavior.

**Resolution:** Restart the watcher or poller after code changes. If a failed
message was already marked `ai-processed`, remove that label before retrying.

## Supabase CLI setup

**Issue:** Supabase CLI setup was blocked because `scoop` was not available by
name in PowerShell, even though Scoop was already installed.

**Resolution:** Invoke the Scoop script by its full path, add the Scoop shims
directory to the session's `PATH`, then install the Supabase CLI:

```powershell
& "$HOME\scoop\shims\scoop.ps1" bucket add supabase https://github.com/supabase/scoop-bucket.git
& "$HOME\scoop\shims\scoop.ps1" install supabase
```
