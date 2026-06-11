"""
Data cleaning and utility functions for AI Job Market Analyzer.

Provides functions for:
- Cleaning invalid company names
- Standardizing company name formats
- Filtering data based on user selections
"""

import pandas as pd
import re


def clean_company_names(df: pd.DataFrame, company_col: str = "company") -> pd.DataFrame:
    """
    Clean and standardize company names.
    
    Removes:
    - Blank/null values
    - Special character only values (e.g., ****, ---, etc.)
    - Single characters or numbers
    
    Returns cleaned dataframe.
    """
    df = df.copy()
    
    # Remove null values
    df = df[df[company_col].notna()]
    
    # Remove blank strings
    df = df[df[company_col].str.strip() != ""]
    
    # Remove special-character-only names
    df = df[df[company_col].apply(lambda x: bool(re.search(r'[a-zA-Z0-9]', str(x))))]
    
    # Remove rows where company is just single char or numbers
    df = df[df[company_col].apply(lambda x: len(str(x).strip()) > 1)]
    
    # Standardize spacing and case
    df[company_col] = (
        df[company_col]
        .str.strip()
        .str.title()
        .str.replace(r'\s+', ' ', regex=True)  # Multiple spaces to single
    )
    
    return df


def get_unique_sorted_values(series: pd.Series) -> list:
    """Get unique, non-null values from a series, sorted alphabetically."""
    return sorted(series.dropna().unique().tolist())


def filter_data(
    df: pd.DataFrame,
    location: str = None,
    company: str = None,
    job_title: str = None,
) -> pd.DataFrame:
    """
    Filter dataframe by location, company, and/or job title.
    
    Returns filtered dataframe.
    """
    filtered = df.copy()
    
    if location and location != "All Locations":
        filtered = filtered[filtered["location"] == location]
    
    if company and company != "All Companies":
        filtered = filtered[filtered["company"] == company]
    
    if job_title and job_title != "All Job Titles":
        filtered = filtered[filtered["title"] == job_title]
    
    return filtered


def get_salary_stats_by_group(
    df: pd.DataFrame,
    group_col: str,
    salary_col: str = "salary_in_usd",
) -> pd.DataFrame:
    """
    Get salary statistics grouped by a column.
    
    Returns dataframe with mean, median, min, max, count.
    """
    stats = (
        df.groupby(group_col)[salary_col]
        .agg([
            ('Average', 'mean'),
            ('Median', 'median'),
            ('Min', 'min'),
            ('Max', 'max'),
            ('Count', 'count'),
        ])
        .round(0)
        .astype({'Count': int})
        .sort_values('Average', ascending=False)
    )
    return stats
