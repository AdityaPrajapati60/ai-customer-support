# AI Customer Support

## Troubleshooting

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