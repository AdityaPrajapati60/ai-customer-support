# %%
from pathlib import Path
import sys

from dotenv import load_dotenv


def find_project_root() -> Path:
    starts = [Path.cwd().resolve()]
    current_file = globals().get("__file__")
    if current_file:
        starts.insert(0, Path(current_file).resolve().parent)

    for start in starts:
        for candidate in (start, *start.parents):
            if (candidate / "pyproject.toml").is_file() and (
                candidate / "app"
            ).is_dir():
                return candidate

    raise FileNotFoundError(
        "Could not find the project root (expected pyproject.toml and app/). "
        "Open this file from the ai-customer-support workspace."
    )


PROJECT_ROOT = find_project_root()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from app.ai.decide import run_pipeline

# %% Edit the question and run this cell to see the pipeline result.
QUESTION = "I want my money back, this is ridiculous"

# %% Run classification, drafting, and deterministic decision logic.
result = run_pipeline(QUESTION)
print(result.model_dump_json(indent=2))
