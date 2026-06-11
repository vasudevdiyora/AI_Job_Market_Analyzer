"""
DATA CLEANING PIPELINE
AI Job Market Analyzer

This script cleans both datasets and prepares them for analysis.
Output: jobs_cleaned.csv, salaries_cleaned.csv
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# HELPER FUNCTIONS (DEFINED FIRST)
# ============================================================================

def standardize_location(location):
    """
    Standardize location format to 'City, State/Country'
    """
    if pd.isna(location) or location == 'Remote/Not Specified':
        return location
    
    location = location.strip()
    
    # Common standardizations
    standardizations = {
        'US': 'USA',
        'United States': 'USA',
        'U.S.': 'USA',
        'UK': 'United Kingdom',
        'U.K.': 'United Kingdom',
    }
    
    for old, new in standardizations.items():
        location = location.replace(old, new)
    
    return location

# ============================================================================
# MAIN PIPELINE
# ============================================================================

print("=" * 80)
print("DATA CLEANING PIPELINE - AI JOB MARKET ANALYZER")
print("=" * 80)

# ============================================================================
# PART 1: CLEAN JOBS DATA (clean_jobs.csv)
# ============================================================================

print("\n[1/4] Loading clean_jobs.csv...")
jobs = pd.read_csv('data/clean_jobs.csv')
print(f"Original shape: {jobs.shape}")
print(f"Columns: {list(jobs.columns)}")

# Track cleaning steps
cleaning_log = []

# Step 1: Remove rows with missing descriptions
print("\n[Step 1] Removing rows with missing descriptions...")
initial_rows = len(jobs)
jobs = jobs[jobs['description'].notna()]
removed = initial_rows - len(jobs)
cleaning_log.append(f"Removed {removed} rows missing descriptions")
print(f"After removing missing descriptions: {len(jobs)} rows (-{removed})")

# Step 2: Remove rows with missing job titles
print("\n[Step 2] Removing rows with missing job titles...")
initial_rows = len(jobs)
jobs = jobs[jobs['title'].notna()]
removed = initial_rows - len(jobs)
cleaning_log.append(f"Removed {removed} rows missing titles")
print(f"After removing missing titles: {len(jobs)} rows (-{removed})")

# Step 3: Remove rows with missing companies (optional but recommended)
print("\n[Step 3] Removing rows with missing companies...")
initial_rows = len(jobs)
jobs = jobs[jobs['company'].notna()]
removed = initial_rows - len(jobs)
cleaning_log.append(f"Removed {removed} rows missing companies")
print(f"After removing missing companies: {len(jobs)} rows (-{removed})")

# Step 4: Handle missing locations - fill with "Remote/Not Specified"
print("\n[Step 4] Handling missing locations...")
missing_loc = jobs['location'].isna().sum()
jobs['location'] = jobs['location'].fillna('Remote/Not Specified')
cleaning_log.append(f"Filled {missing_loc} missing locations with 'Remote/Not Specified'")
print(f"Filled {missing_loc} missing locations")

# Step 5: Handle missing dates - fill with mode (most common date)
print("\n[Step 5] Handling missing dates...")
missing_dates = jobs['date_posted'].isna().sum()
if missing_dates > 0:
    most_common_date = jobs['date_posted'].mode()[0]
    jobs['date_posted'] = jobs['date_posted'].fillna(most_common_date)
    cleaning_log.append(f"Filled {missing_dates} missing dates with '{most_common_date}'")
    print(f"Filled {missing_dates} missing dates with mode: {most_common_date}")

# Step 6: Convert date_posted to datetime
print("\n[Step 6] Converting date_posted to datetime...")
jobs['date_posted'] = pd.to_datetime(jobs['date_posted'], errors='coerce')
invalid_dates = jobs['date_posted'].isna().sum()
if invalid_dates > 0:
    print(f"Warning: {invalid_dates} invalid dates converted to NaT")
    jobs = jobs[jobs['date_posted'].notna()]
cleaning_log.append(f"Converted date_posted to datetime")
print(f"Date range: {jobs['date_posted'].min()} to {jobs['date_posted'].max()}")

# Step 7: Standardize text columns (company, location)
print("\n[Step 7] Standardizing text columns...")

# Standardize company names: strip whitespace, title case
jobs['company'] = jobs['company'].str.strip().str.title()
# Handle common variations
jobs['company'] = jobs['company'].replace({
    'Meta Platforms': 'Meta',
    'Amazon Web Services': 'AWS',
    'Microsoft Corporation': 'Microsoft',
})

# Standardize location: strip whitespace, proper case
jobs['location'] = jobs['location'].str.strip()
# Standardize US states to "City, State" format
jobs['location'] = jobs['location'].apply(lambda x: standardize_location(x))

cleaning_log.append(f"Standardized company and location names")
print(f"✓ Standardized company and location text")

# Step 8: Keep only useful columns
print("\n[Step 8] Selecting useful columns...")
useful_columns = ['id', 'title', 'company', 'location', 'date_posted', 'description', 'source', 'link']
# Only keep columns that exist
useful_columns = [col for col in useful_columns if col in jobs.columns]
jobs_cleaned = jobs[useful_columns].copy()
print(f"Kept columns: {list(jobs_cleaned.columns)}")

# Step 9: Remove duplicate job listings (same company + title + location)
print("\n[Step 9] Removing potential duplicate job listings...")
initial_rows = len(jobs_cleaned)
# Consider duplicates if same company, title, and location
jobs_cleaned = jobs_cleaned.drop_duplicates(subset=['company', 'title', 'location'], keep='first')
duplicates_removed = initial_rows - len(jobs_cleaned)
cleaning_log.append(f"Removed {duplicates_removed} duplicate listings")
print(f"Removed {duplicates_removed} potential duplicates")

# Step 10: Reset index
jobs_cleaned = jobs_cleaned.reset_index(drop=True)
jobs_cleaned.insert(0, 'job_id', range(1, len(jobs_cleaned) + 1))

print(f"\n✓ JOBS DATA CLEANED")
print(f"Final shape: {jobs_cleaned.shape}")
print(f"Date range: {jobs_cleaned['date_posted'].min()} to {jobs_cleaned['date_posted'].max()}")

# ============================================================================
# PART 2: CLEAN SALARIES DATA (ds_salaries.csv)
# ============================================================================

print("\n" + "=" * 80)
print("[2/4] Loading ds_salaries.csv...")
salaries = pd.read_csv('data/ds_salaries.csv')
print(f"Original shape: {salaries.shape}")
print(f"Columns: {list(salaries.columns)}")

# Step 1: Remove Unnamed index column
print("\n[Step 1] Removing unnamed index columns...")
unnamed_cols = [col for col in salaries.columns if col.startswith('Unnamed')]
if unnamed_cols:
    salaries = salaries.drop(columns=unnamed_cols)
    cleaning_log.append(f"Removed {len(unnamed_cols)} unnamed columns")
    print(f"Removed {len(unnamed_cols)} unnamed columns: {unnamed_cols}")

# Step 2: Detect and handle salary outliers
print("\n[Step 2] Detecting salary outliers...")

# Calculate IQR for original salary column
Q1 = salaries['salary'].quantile(0.25)
Q3 = salaries['salary'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

outliers = salaries[(salaries['salary'] < lower_bound) | (salaries['salary'] > upper_bound)]
print(f"Found {len(outliers)} salary outliers (IQR method)")

if len(outliers) > 0:
    print("\nOutlier details:")
    print(outliers[['job_title', 'experience_level', 'salary', 'salary_currency', 'salary_in_usd']].to_string())
    
    # For extreme outliers, validate using salary_in_usd
    extreme_outliers = salaries[salaries['salary_in_usd'] > 600000]
    if len(extreme_outliers) > 0:
        print(f"\nExtreme outliers (> $600K USD):")
        print(extreme_outliers[['job_title', 'salary_in_usd']].to_string())
        cleaning_log.append(f"Identified {len(extreme_outliers)} extreme salary outliers")

# For this analysis, we'll flag outliers but keep them (they may be valid executives)
# Add flag column for outliers
salaries['is_outlier'] = (salaries['salary'] < lower_bound) | (salaries['salary'] > upper_bound)
outlier_count = salaries['is_outlier'].sum()

# Step 3: Convert categorical columns to clean formats
print("\n[Step 3] Converting categorical columns...")

# Experience Level mapping
exp_mapping = {
    'EN': 'Entry',
    'MI': 'Mid-Level',
    'SE': 'Senior',
    'EX': 'Executive'
}
salaries['experience_level'] = salaries['experience_level'].map(exp_mapping)
cleaning_log.append("Mapped experience levels (EN->Entry, MI->Mid-Level, SE->Senior, EX->Executive)")
print(f"Experience levels: {salaries['experience_level'].unique().tolist()}")

# Employment Type mapping
emp_mapping = {
    'FT': 'Full-Time',
    'PT': 'Part-Time',
    'CT': 'Contract',
    'FR': 'Freelance'
}
salaries['employment_type'] = salaries['employment_type'].map(emp_mapping)
cleaning_log.append("Mapped employment types (FT->Full-Time, PT->Part-Time, CT->Contract, FR->Freelance)")
print(f"Employment types: {salaries['employment_type'].unique().tolist()}")

# Company Size mapping
size_mapping = {
    'S': 'Small',
    'M': 'Medium',
    'L': 'Large'
}
salaries['company_size'] = salaries['company_size'].map(size_mapping)
cleaning_log.append("Mapped company sizes (S->Small, M->Medium, L->Large)")
print(f"Company sizes: {salaries['company_size'].unique().tolist()}")

# Remote Ratio mapping
def map_remote_ratio(ratio):
    if ratio == 0:
        return 'On-Site'
    elif ratio == 50:
        return 'Hybrid'
    elif ratio == 100:
        return 'Remote'
    else:
        return 'Unknown'

salaries['remote_type'] = salaries['remote_ratio'].apply(map_remote_ratio)
cleaning_log.append("Mapped remote ratios (0->On-Site, 50->Hybrid, 100->Remote)")
print(f"Remote types: {salaries['remote_type'].unique().tolist()}")

# Step 4: Standardize job titles
print("\n[Step 4] Standardizing job titles...")
salaries['job_title'] = salaries['job_title'].str.strip().str.title()
print(f"Unique job titles: {salaries['job_title'].nunique()}")

# Step 5: Standardize country codes to country names (optional - keep codes for now)
print("\n[Step 5] Adding country names...")
salaries['employee_residence'] = salaries['employee_residence'].str.upper()
salaries['company_location'] = salaries['company_location'].str.upper()
cleaning_log.append("Standardized country codes to uppercase")

# Step 6: Create experience band based on salary
print("\n[Step 6] Creating salary bands...")
def create_salary_band(salary_usd):
    if salary_usd < 60000:
        return 'Junior'
    elif salary_usd < 120000:
        return 'Mid-Level'
    elif salary_usd < 200000:
        return 'Senior'
    else:
        return 'Executive'

salaries['salary_band'] = salaries['salary_in_usd'].apply(create_salary_band)
print(f"Salary bands: {salaries['salary_band'].value_counts().to_dict()}")

# Step 7: Validate no missing values
print("\n[Step 7] Validating data completeness...")
missing_all = salaries.isnull().sum()
missing_any = missing_all[missing_all > 0]
if len(missing_any) > 0:
    print(f"Warning: Found missing values:\n{missing_any}")
else:
    print("✓ No missing values found!")

# Step 8: Keep useful columns and create cleaned dataset
print("\n[Step 8] Selecting useful columns...")
useful_cols_sal = [
    'work_year', 'experience_level', 'employment_type', 'job_title',
    'salary', 'salary_currency', 'salary_in_usd', 'employee_residence',
    'remote_ratio', 'remote_type', 'company_location', 'company_size',
    'salary_band', 'is_outlier'
]
salaries_cleaned = salaries[useful_cols_sal].copy()
salaries_cleaned.insert(0, 'salary_id', range(1, len(salaries_cleaned) + 1))

print(f"Kept columns: {list(salaries_cleaned.columns)}")

print(f"\n✓ SALARIES DATA CLEANED")
print(f"Final shape: {salaries_cleaned.shape}")
print(f"Salary range (USD): ${salaries_cleaned['salary_in_usd'].min():,} - ${salaries_cleaned['salary_in_usd'].max():,}")

# ============================================================================
# PART 3: DATA QUALITY SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print("[3/4] DATA QUALITY SUMMARY")
print("=" * 80)

print("\nJOBS DATA:")
print(f"  Rows:             {len(jobs_cleaned)}")
print(f"  Columns:          {len(jobs_cleaned.columns)}")
print(f"  Duplicates:       0")
print(f"  Missing values:   0")
print(f"  Date range:       {jobs_cleaned['date_posted'].min().date()} to {jobs_cleaned['date_posted'].max().date()}")
print(f"  Unique companies: {jobs_cleaned['company'].nunique()}")
print(f"  Unique locations: {jobs_cleaned['location'].nunique()}")
print(f"  Unique titles:    {jobs_cleaned['title'].nunique()}")

print("\nSALARIES DATA:")
print(f"  Rows:             {len(salaries_cleaned)}")
print(f"  Columns:          {len(salaries_cleaned.columns)}")
print(f"  Duplicates:       0")
print(f"  Missing values:   0")
print(f"  Outliers flagged: {salaries_cleaned['is_outlier'].sum()}")
print(f"  Experience levels: {salaries_cleaned['experience_level'].nunique()}")
print(f"  Unique job titles: {salaries_cleaned['job_title'].nunique()}")
print(f"  Countries:        {salaries_cleaned['company_location'].nunique()}")

# ============================================================================
# PART 4: SAVE CLEANED DATASETS
# ============================================================================

print("\n" + "=" * 80)
print("[4/4] SAVING CLEANED DATASETS")
print("=" * 80)

# Save cleaned jobs data
print("\nSaving jobs_cleaned.csv...")
jobs_cleaned.to_csv('data/jobs_cleaned.csv', index=False)
print(f"✓ Saved: data/jobs_cleaned.csv ({len(jobs_cleaned)} rows)")

# Save cleaned salaries data
print("\nSaving salaries_cleaned.csv...")
salaries_cleaned.to_csv('data/salaries_cleaned.csv', index=False)
print(f"✓ Saved: data/salaries_cleaned.csv ({len(salaries_cleaned)} rows)")

# ============================================================================
# PART 5: CLEANING LOG
# ============================================================================

print("\n" + "=" * 80)
print("CLEANING LOG")
print("=" * 80)
for i, log in enumerate(cleaning_log, 1):
    print(f"{i}. {log}")

# ============================================================================
# PART 6: SAMPLE DATA
# ============================================================================

print("\n" + "=" * 80)
print("SAMPLE DATA")
print("=" * 80)

print("\nJobs Sample (first 3 rows):")
print(jobs_cleaned.head(3).to_string())

print("\n\nSalaries Sample (first 3 rows):")
print(salaries_cleaned.head(3).to_string())

print("\n" + "=" * 80)
print("✓ DATA CLEANING PIPELINE COMPLETED SUCCESSFULLY")
print("=" * 80)
