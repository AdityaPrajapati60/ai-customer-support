# AI Customer Support

## AI provider setup

The classifier and support agent both use Groq through PydanticAI's
OpenAI-compatible provider. Add the key to the project `.env` file:

```dotenv
GROQ_API_KEY=your-groq-api-key
CLASSIFIER_MODEL=openai/gpt-oss-20b
AGENT_MODEL=openai/gpt-oss-20b
```

The model variables are optional; `openai/gpt-oss-20b` is the default for both
classification and agent replies. It supports Groq tool use and structured
outputs. Do not commit `.env`. Groq requests use
`https://api.groq.com/openai/v1`.

Before drafting a reply, the application loads the required knowledge-base
sections and includes them in the prompt. Reply data is requested as prompted
structured output, so processing does not depend on the model choosing
knowledge-base tools or returning its result through a tool call.

## Local AI pipeline playground

Use `playground/ai_pipeline_playground.py` to run a customer question through
classification, answer drafting, and the final deterministic decision without
connecting to Gmail or sending an email. The default question is
`My board loses air overnight`. Edit `QUESTION` to try another message.

Run it from the project root:

```powershell
uv run python playground/ai_pipeline_playground.py
```

In VS Code, open the file and run its `# %%` cells with **Run Cell** or **Run
All** to use the Jupyter Interactive window. The script locates the project
root, adds it to `sys.path`, and loads the root `.env` before importing the
application. The playground needs `GROQ_API_KEY` and `DATABASE_URL` to classify
and draft answers using the configured model and Supabase knowledge base; it
does not need Gmail credentials.

The `result` variable is a `PipelineResult` Pydantic model containing:

- `classification`: the `Classification` model (category, language, escalation
  flag, reason, and acknowledgement).
- `agent_reply`: the `AgentReply` model (draft, reasoning, knowledge sufficiency,
  action-promise flag, and any detected issue), or `null` if reply drafting was
  skipped.
- `decision`: the `Decision` model (reply or escalation, final text, reason, and
  any proposed action).

Inspect individual fields with `result.classification`, `result.agent_reply`,
and `result.decision`. The final cell prints all available data as JSON.

## Troubleshooting

### Issues encountered and fixes

#### OpenRouter API request failed

The current application is configured for Groq, not OpenRouter. Keep the
provider settings together: use `GROQ_API_KEY`, the Groq model ID
(`openai/gpt-oss-20b` by default), and the Groq-compatible endpoint
`https://api.groq.com/openai/v1`. Do not use an OpenRouter key with the Groq
endpoint. If switching back to OpenRouter, configure its API key, endpoint, and
supported model together in the provider setup rather than mixing settings.

#### Test 20 failed with “Tool choice is required, but model did not call a tool”

Groq rejected a plain-text draft because the reply agent was relying on the
model to call knowledge-base tools and return its final answer through a tool.
The fix is to load the required knowledge-base sections in the application and
request the reply as prompted structured output. This avoids depending on the
model to choose or format tool calls. See [AI provider setup](#ai-provider-setup).

If a message has already reached the retry limit and received the
`ai-processed` label, remove that label after fixing the issue so the poller can
pick up the message again.

#### Reply rejected as incomplete or missing punctuation

The reply validator rejected a generated answer that did not end with
sentence-ending punctuation. PydanticAI retried once, but the next response
failed the same check and the message was not sent. The support agent now has a
bounded output retry allowance of three retries so the model has more chances
to correct an incomplete draft; the validator still blocks replies that fail
the completeness checks. Restart the poller after updating the code so it
loads the new retry setting. If the message was marked `ai-processed` after
repeated failures, remove that label before retrying it.

#### Gmail returned HTTP 500 `backendError`

The Gmail profile request temporarily returned Google's “Unknown Error.”
Because this is a Gmail API backend error, retry by letting the poller run
again. The poller logs the failure and continues polling; changing credentials
is not the fix for this transient response.

Other setup issues, including the missing `dotenv` module, the Windows watcher
using the wrong Python interpreter, and PowerShell not finding Scoop, are
covered in the troubleshooting sections below. Restart the watcher or poller
after code changes so it does not continue running an already-loaded version.

### `ModuleNotFoundError: No module named 'dotenv'`

The application imports `load_dotenv` from `dotenv`; the installable package is
`python-dotenv`, which is already listed in `pyproject.toml`. Make sure the
project environment is synchronized:

```powershell
uv sync
uv run python -c "import dotenv; print(dotenv.__file__)"
```

On Windows, `python` in a child process may resolve to a different interpreter
than the one managed by `uv`. Run the poller under `uv` explicitly when starting
it with `watchfiles`:

```powershell
uv run watchfiles "uv run python -m app.poller" app .env
```

### `scoop` is not recognized in PowerShell

Scoop was already installed under `$HOME\scoop`, but its shims directory was not
on the current PowerShell session's `PATH`. If the installer reports that this
directory exists, do not delete it or reinstall over it. Check for the existing
Scoop script and use it directly:

```powershell
Test-Path "$HOME\scoop\shims\scoop.ps1"
& "$HOME\scoop\shims\scoop.ps1" --version
```

Install the Supabase CLI with the existing Scoop installation:

```powershell
& "$HOME\scoop\shims\scoop.ps1" bucket add supabase https://github.com/supabase/scoop-bucket.git
& "$HOME\scoop\shims\scoop.ps1" install supabase
```

To use the `scoop` and `supabase` commands by name in the current PowerShell
window, add Scoop's shims directory to `PATH` and verify the CLI:

```powershell
$env:Path += ";$HOME\scoop\shims"
supabase --version
```

This `$env:Path` change applies only to the current PowerShell window. In a new
window, either add the shims directory again or invoke Scoop through the full
script path shown above.

## Knowledge base

The six Markdown files in `knowledge_base/` are the source for the Harbor & Pine
knowledge base. Each file represents a section, and each `##` heading becomes
one row in Supabase.

Apply the existing schema migration to the linked Supabase project, then seed or
update the entries:

```powershell
supabase db push
uv run python -m scripts.seed_knowledge_base
```

The seed script updates existing entries with the same section and title. This
overwrites database edits for those entries, so make future content changes in
the Markdown files and reseed only when that overwrite is intended.