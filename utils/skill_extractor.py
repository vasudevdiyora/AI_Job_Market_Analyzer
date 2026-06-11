"""
Skill extraction module for AI Job Market Analyzer.

Reads job descriptions from data/jobs_cleaned.csv, detects skills using keyword
matching, and writes:
- data/skill_frequency.csv
- data/jobs_with_skills.csv

Also prints:
- Top 20 skills table
- Skill frequency counts
"""

import re
from pathlib import Path
from typing import Dict, List, Pattern, Tuple

import pandas as pd


# Required skills to detect and their regex patterns.
# Patterns use word boundaries and common variants for robust matching.
SKILL_PATTERNS: Dict[str, str] = {
    "Python": r"\bpython\b",
    "Java": r"\bjava\b",
    "SQL": r"\bsql\b",
    "C++": r"\bc\+\+\b|\bcpp\b",
    "JavaScript": r"\bjavascript\b|\bjs\b",
    "React": r"\breact(?:\.js)?\b",
    "Node.js": r"\bnode\.?js\b|\bnodejs\b",
    "Spring Boot": r"\bspring\s*boot\b",
    "Docker": r"\bdocker\b",
    "Kubernetes": r"\bkubernetes\b|\bk8s\b",
    "AWS": r"\baws\b|\bamazon\s+web\s+services\b",
    "Azure": r"\bazure\b|\bmicrosoft\s+azure\b",
    "Git": r"\bgit\b|\bgithub\b|\bgitlab\b",
    "Power BI": r"\bpower\s*bi\b",
    "Tableau": r"\btableau\b",
    "Machine Learning": r"\bmachine\s+learning\b|\bml\b",
    "Deep Learning": r"\bdeep\s+learning\b|\bdl\b",
    "Data Analysis": r"\bdata\s+analysis\b|\bdata\s+analytics\b|\banalytical\b",
    "Excel": r"\bexcel\b|\bmicrosoft\s+excel\b",
}


def compile_skill_patterns(skill_patterns: Dict[str, str]) -> Dict[str, Pattern[str]]:
    """Compile regex patterns for efficient repeated matching."""
    return {skill: re.compile(pattern, re.IGNORECASE) for skill, pattern in skill_patterns.items()}


def extract_skills_from_text(text: str, compiled_patterns: Dict[str, Pattern[str]]) -> List[str]:
    """Return a sorted list of skills detected in a single job description."""
    if not isinstance(text, str) or not text.strip():
        return []

    found = [skill for skill, pattern in compiled_patterns.items() if pattern.search(text)]
    return sorted(found)


def build_skill_outputs(df: pd.DataFrame, description_col: str = "description") -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Build jobs_with_skills and skill_frequency dataframes."""
    compiled = compile_skill_patterns(SKILL_PATTERNS)

    # Detect skill list per job.
    df = df.copy()
    df["detected_skills"] = df[description_col].apply(lambda x: extract_skills_from_text(x, compiled))
    df["skill_count"] = df["detected_skills"].apply(len)
    df["skills_text"] = df["detected_skills"].apply(lambda s: ", ".join(s))

    # Create long format for frequency counts.
    exploded = df[["detected_skills"]].explode("detected_skills")
    exploded = exploded.dropna(subset=["detected_skills"])

    # Ensure all requested skills appear even if count is zero.
    base = pd.DataFrame({"skill": list(SKILL_PATTERNS.keys())})
    freq = (
        exploded.groupby("detected_skills")
        .size()
        .reset_index(name="frequency")
        .rename(columns={"detected_skills": "skill"})
    )

    skill_frequency = (
        base.merge(freq, on="skill", how="left")
        .fillna({"frequency": 0})
        .astype({"frequency": int})
        .sort_values(["frequency", "skill"], ascending=[False, True])
        .reset_index(drop=True)
    )

    # Build final jobs_with_skills with useful columns first.
    preferred_cols = [
        "job_id",
        "id",
        "title",
        "company",
        "location",
        "date_posted",
        "source",
        "link",
        "skill_count",
        "skills_text",
    ]
    existing = [c for c in preferred_cols if c in df.columns]
    jobs_with_skills = pd.concat([df[existing], df[["description", "detected_skills"]]], axis=1)

    return jobs_with_skills, skill_frequency


def print_top_20_and_counts(skill_frequency: pd.DataFrame) -> None:
    """Print top 20 skills and full frequency counts."""
    print("\n" + "=" * 80)
    print("TOP 20 SKILLS TABLE")
    print("=" * 80)
    top_20 = skill_frequency.head(20)
    print(top_20.to_string(index=False))

    print("\n" + "=" * 80)
    print("SKILL FREQUENCY COUNTS")
    print("=" * 80)
    for _, row in skill_frequency.iterrows():
        print(f"{row['skill']:<18} : {row['frequency']}")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"

    input_file = data_dir / "jobs_cleaned.csv"
    out_freq = data_dir / "skill_frequency.csv"
    out_jobs = data_dir / "jobs_with_skills.csv"

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    jobs_df = pd.read_csv(input_file)

    if "description" not in jobs_df.columns:
        raise ValueError("Required column 'description' not found in jobs_cleaned.csv")

    jobs_with_skills, skill_frequency = build_skill_outputs(jobs_df, description_col="description")

    # Save required outputs inside data/.
    skill_frequency.to_csv(out_freq, index=False)

    # Convert list column to pipe-separated string for CSV friendliness.
    jobs_export = jobs_with_skills.copy()
    jobs_export["detected_skills"] = jobs_export["detected_skills"].apply(lambda s: "|".join(s))
    jobs_export.to_csv(out_jobs, index=False)

    print(f"Input file          : {input_file}")
    print(f"Rows processed      : {len(jobs_df)}")
    print(f"Output generated    : {out_freq}")
    print(f"Output generated    : {out_jobs}")
    print_top_20_and_counts(skill_frequency)


if __name__ == "__main__":
    main()
