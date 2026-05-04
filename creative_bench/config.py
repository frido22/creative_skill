from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"
SKILL_PATH = ROOT / "skills" / "creative" / "SKILL.md"
README_PATH = ROOT / "README.md"


@dataclass(frozen=True)
class Settings:
    gen_model: str
    judge_model: str
    temperature: float
    seed: int
    reasoning_effort: str
    max_workers: int
    root: Path = ROOT
    data_dir: Path = DATA_DIR
    results_dir: Path = RESULTS_DIR
    skill_path: Path = SKILL_PATH
    readme_path: Path = README_PATH


def load_settings() -> Settings:
    load_dotenv()
    return Settings(
        gen_model=os.getenv("GEN_MODEL", "gpt-5.5"),
        judge_model=os.getenv("JUDGE_MODEL", "gpt-5.5"),
        temperature=float(os.getenv("TEMPERATURE", "0.8")),
        seed=int(os.getenv("SEED", "42")),
        reasoning_effort=os.getenv("REASONING_EFFORT", "medium"),
        max_workers=int(os.getenv("MAX_WORKERS", "12")),
    )


def require_api_key() -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required for real benchmark runs.")
    return api_key
