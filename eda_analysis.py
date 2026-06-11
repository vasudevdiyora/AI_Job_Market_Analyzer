import pandas as pd
import numpy as np

# Load datasets
jobs = pd.read_csv('clean_jobs.csv')
salaries = pd.read_csv('ds_salaries.csv')

print("=" * 80)
print("CLEAN_JOBS.CSV - STRUCTURE")
print("=" * 80)
print(f"\nShape: {jobs.shape}")
print(f"\nColumns ({len(jobs.columns)}):")
for i, col in enumerate(jobs.columns, 1):
    print(f"  {i}. {col}")

print("\n" + "=" * 80)
print("DATA TYPES")
print("=" * 80)
print(jobs.dtypes)

print("\n" + "=" * 80)
print("FIRST 3 ROWS (clean_jobs.csv)")
print("=" * 80)
print(jobs.head(3).to_string())

print("\n" + "=" * 80)
print("MISSING VALUES (clean_jobs.csv)")
print("=" * 80)
missing_jobs = jobs.isnull().sum()
missing_pct = (missing_jobs / len(jobs)) * 100
missing_df = pd.DataFrame({
    'Column': missing_jobs.index,
    'Missing_Count': missing_jobs.values,
    'Missing_Percent': missing_pct.values
})
missing_df = missing_df[missing_df['Missing_Count'] > 0].sort_values('Missing_Count', ascending=False)
if len(missing_df) > 0:
    print(missing_df.to_string(index=False))
else:
    print("No missing values found!")

print("\n" + "=" * 80)
print("DUPLICATE ROWS (clean_jobs.csv)")
print("=" * 80)
duplicates = jobs.duplicated().sum()
print(f"Total duplicate rows: {duplicates}")
if duplicates > 0:
    print(f"Duplicate percentage: {(duplicates/len(jobs))*100:.2f}%")

print("\n" + "=" * 80)
print("UNIQUE VALUES COUNT")
print("=" * 80)
for col in jobs.columns:
    unique_count = jobs[col].nunique()
    print(f"{col}: {unique_count} unique values")

print("\n" + "=" * 80)
print("SAMPLE VALUES BY COLUMN")
print("=" * 80)
for col in jobs.columns:
    print(f"\n{col}:")
    print(f"  Sample values: {jobs[col].dropna().head(3).tolist()}")

print("\n\n" + "=" * 80)
print("DS_SALARIES.CSV - STRUCTURE")
print("=" * 80)
print(f"\nShape: {salaries.shape}")
print(f"\nColumns ({len(salaries.columns)}):")
for i, col in enumerate(salaries.columns, 1):
    print(f"  {i}. {col}")

print("\n" + "=" * 80)
print("DATA TYPES")
print("=" * 80)
print(salaries.dtypes)

print("\n" + "=" * 80)
print("FIRST 3 ROWS (ds_salaries.csv)")
print("=" * 80)
print(salaries.head(3).to_string())

print("\n" + "=" * 80)
print("MISSING VALUES (ds_salaries.csv)")
print("=" * 80)
missing_sal = salaries.isnull().sum()
missing_pct_sal = (missing_sal / len(salaries)) * 100
missing_df_sal = pd.DataFrame({
    'Column': missing_sal.index,
    'Missing_Count': missing_sal.values,
    'Missing_Percent': missing_pct_sal.values
})
missing_df_sal = missing_df_sal[missing_df_sal['Missing_Count'] > 0].sort_values('Missing_Count', ascending=False)
if len(missing_df_sal) > 0:
    print(missing_df_sal.to_string(index=False))
else:
    print("No missing values found!")

print("\n" + "=" * 80)
print("DUPLICATE ROWS (ds_salaries.csv)")
print("=" * 80)
duplicates_sal = salaries.duplicated().sum()
print(f"Total duplicate rows: {duplicates_sal}")
if duplicates_sal > 0:
    print(f"Duplicate percentage: {(duplicates_sal/len(salaries))*100:.2f}%")

print("\n" + "=" * 80)
print("UNIQUE VALUES COUNT")
print("=" * 80)
for col in salaries.columns:
    unique_count = salaries[col].nunique()
    print(f"{col}: {unique_count} unique values")

print("\n" + "=" * 80)
print("SAMPLE VALUES BY COLUMN")
print("=" * 80)
for col in salaries.columns:
    print(f"\n{col}:")
    if salaries[col].dtype in ['int64', 'float64']:
        print(f"  Min: {salaries[col].min()}, Max: {salaries[col].max()}, Mean: {salaries[col].mean():.2f}")
    else:
        print(f"  Sample values: {salaries[col].dropna().head(3).tolist()}")

print("\n" + "=" * 80)
print("STATISTICAL SUMMARY")
print("=" * 80)
print("\nds_salaries.csv numeric columns:")
print(salaries.describe().to_string())

EOF
