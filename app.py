"""
AI Job Market Analyzer - Main Dashboard (Overview)

Shows:
- KPIs: Total Jobs, Companies, Locations, Average Salary
- Top 10 Skills
- Top 10 Job Titles
- Top 10 Companies
- Top 10 Hiring Locations
- Job Posting Trends
- Salary Distribution
- Interactive filters (Location, Company, Job Title)
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.data_cleaners import (
    clean_company_names,
    get_unique_sorted_values,
    filter_data,
)


st.set_page_config(
    page_title="AI Job Market Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def load_data():
    """Load all datasets and apply data quality improvements."""
    jobs_df = pd.read_csv("data/jobs_cleaned.csv")
    salaries_df = pd.read_csv("data/salaries_cleaned.csv")
    skills_df = pd.read_csv("data/skill_frequency.csv")
    
    # Clean company names
    jobs_df = clean_company_names(jobs_df, "company")
    
    # Convert date_posted to datetime
    jobs_df["date_posted"] = pd.to_datetime(jobs_df["date_posted"])
    
    return jobs_df, salaries_df, skills_df


def format_currency(value: float) -> str:
    """Format value as USD currency."""
    return f"${value:,.0f}"


def build_top_skills_chart(skills_df: pd.DataFrame):
    """Top 10 Skills bar chart."""
    top_skills = skills_df.sort_values("frequency", ascending=False).head(10)
    fig = px.bar(
        top_skills,
        x="frequency",
        y="skill",
        orientation="h",
        text="frequency",
        color="frequency",
        color_continuous_scale="Blues",
        title="📚 Top 10 Skills in Demand",
    )
    fig.update_layout(
        yaxis_title="",
        xaxis_title="Frequency",
        coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=50, b=10),
        height=380,
        hovermode="y unified",
    )
    fig.update_traces(textposition="outside")
    fig.update_yaxes(categoryorder="total ascending")
    return fig


def build_top_job_titles_chart(jobs_df: pd.DataFrame):
    """Top 10 Job Titles bar chart."""
    titles = (
        jobs_df["title"]
        .dropna()
        .value_counts()
        .head(10)
        .reset_index()
    )
    titles.columns = ["title", "count"]

    fig = px.bar(
        titles,
        x="count",
        y="title",
        orientation="h",
        text="count",
        color="count",
        color_continuous_scale="Greens",
        title="💼 Top 10 Job Titles",
    )
    fig.update_layout(
        yaxis_title="",
        xaxis_title="Count",
        coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=50, b=10),
        height=380,
        hovermode="y unified",
    )
    fig.update_traces(textposition="outside")
    fig.update_yaxes(categoryorder="total ascending")
    return fig


def build_top_companies_chart(jobs_df: pd.DataFrame):
    """Top 10 Companies bar chart."""
    companies = (
        jobs_df["company"]
        .dropna()
        .value_counts()
        .head(10)
        .reset_index()
    )
    companies.columns = ["company", "count"]

    fig = px.bar(
        companies,
        x="count",
        y="company",
        orientation="h",
        text="count",
        color="count",
        color_continuous_scale="Tealgrn",
        title="🏢 Top 10 Hiring Companies",
    )
    fig.update_layout(
        yaxis_title="",
        xaxis_title="Count",
        coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=50, b=10),
        height=380,
        hovermode="y unified",
    )
    fig.update_traces(textposition="outside")
    fig.update_yaxes(categoryorder="total ascending")
    return fig


def build_top_locations_chart(jobs_df: pd.DataFrame):
    """Top 10 Hiring Locations bar chart."""
    locations = (
        jobs_df["location"]
        .dropna()
        .value_counts()
        .head(10)
        .reset_index()
    )
    locations.columns = ["location", "count"]

    fig = px.bar(
        locations,
        x="count",
        y="location",
        orientation="h",
        text="count",
        color="count",
        color_continuous_scale="Reds",
        title="📍 Top 10 Hiring Locations",
    )
    fig.update_layout(
        yaxis_title="",
        xaxis_title="Count",
        coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=50, b=10),
        height=380,
        hovermode="y unified",
    )
    fig.update_traces(textposition="outside")
    fig.update_yaxes(categoryorder="total ascending")
    return fig


def build_job_trend_chart(jobs_df: pd.DataFrame):
    """Job posting trend over time."""
    trend = (
        jobs_df.groupby(jobs_df["date_posted"].dt.date)
        .size()
        .reset_index(name="count")
    )
    trend.columns = ["date", "count"]

    fig = px.line(
        trend,
        x="date",
        y="count",
        title="📈 Job Posting Trend",
        markers=True,
        line_shape="linear",
    )
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Number of Jobs Posted",
        margin=dict(l=10, r=10, t=50, b=10),
        height=380,
        hovermode="x unified",
    )
    return fig


def build_salary_distribution_chart(salaries_df: pd.DataFrame):
    """Salary distribution histogram."""
    salary_col = "salary_in_usd"
    salary_data = salaries_df[salary_col].dropna()

    fig = px.histogram(
        salary_data,
        x=salary_col,
        nbins=35,
        title="💰 Salary Distribution (USD)",
        opacity=0.9,
    )
    fig.update_layout(
        xaxis_title="Salary in USD",
        yaxis_title="Count",
        bargap=0.05,
        margin=dict(l=10, r=10, t=50, b=10),
        height=380,
        hovermode="x unified",
    )
    return fig


def render_sidebar_filters(jobs_df: pd.DataFrame) -> tuple:
    """Render sidebar with interactive filters."""
    with st.sidebar:
        st.markdown("### 🎯 Filters")
        
        # Location filter
        locations = ["All Locations"] + get_unique_sorted_values(jobs_df["location"])
        selected_location = st.selectbox(
            "Location",
            locations,
            key="location_filter",
        )
        
        # Company filter
        companies = ["All Companies"] + get_unique_sorted_values(jobs_df["company"])
        selected_company = st.selectbox(
            "Company",
            companies,
            key="company_filter",
        )
        
        # Job Title filter
        titles = ["All Job Titles"] + get_unique_sorted_values(jobs_df["title"])
        selected_title = st.selectbox(
            "Job Title",
            titles,
            key="title_filter",
        )
        
        # Apply filters
        filtered_df = filter_data(
            jobs_df,
            location=selected_location,
            company=selected_company,
            job_title=selected_title,
        )
        
        st.markdown(f"### 📊 Filtered Results")
        st.metric("Jobs Found", len(filtered_df))
        
        return filtered_df, selected_location, selected_company, selected_title


def main():
    """Main dashboard layout and logic."""
    # Header styling
    st.markdown(
        """
        <style>
            .main-title {
                font-size: 2.5rem;
                font-weight: 800;
                margin-bottom: 0.1rem;
                color: #1f2937;
            }
            .sub-title {
                color: #6b7280;
                margin-bottom: 1.5rem;
                font-size: 1.05rem;
            }
            .kpi-card {
                background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
                border: 1px solid #bae6fd;
                border-radius: 12px;
                padding: 18px 16px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            }
            .section-header {
                font-size: 1.3rem;
                font-weight: 700;
                margin-top: 2rem;
                margin-bottom: 1rem;
                color: #1f2937;
                padding-bottom: 0.5rem;
                border-bottom: 2px solid #e5e7eb;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Load data
    try:
        jobs_df, salaries_df, skills_df = load_data()
    except FileNotFoundError as e:
        st.error(f"❌ Missing data file: {e}")
        st.stop()

    # Header
    st.markdown('<div class="main-title">📊 AI Job Market Analyzer</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Live market intelligence on jobs, companies, skills, and salaries</div>',
        unsafe_allow_html=True,
    )

    # Sidebar filters
    filtered_jobs_df, sel_location, sel_company, sel_title = render_sidebar_filters(jobs_df)

    # KPIs (updated with filtered data)
    total_jobs = len(filtered_jobs_df)
    total_companies = filtered_jobs_df["company"].nunique(dropna=True)
    total_locations = filtered_jobs_df["location"].nunique(dropna=True)
    avg_salary = salaries_df["salary_in_usd"].mean()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.metric("💼 Total Jobs", f"{total_jobs:,}")
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.metric("🏢 Companies", f"{total_companies:,}")
        st.markdown("</div>", unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.metric("📍 Locations", f"{total_locations:,}")
        st.markdown("</div>", unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.metric("💰 Avg Salary", format_currency(avg_salary))
        st.markdown("</div>", unsafe_allow_html=True)

    # Market Analysis Section
    st.markdown('<div class="section-header">📈 Market Analysis</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(build_top_skills_chart(skills_df), use_container_width=True)
    with col2:
        st.plotly_chart(build_top_job_titles_chart(filtered_jobs_df), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(build_top_companies_chart(filtered_jobs_df), use_container_width=True)
    with col4:
        st.plotly_chart(build_top_locations_chart(filtered_jobs_df), use_container_width=True)

    # Trends Section
    st.markdown('<div class="section-header">📊 Trends & Distribution</div>', unsafe_allow_html=True)

    col5, col6 = st.columns(2)
    with col5:
        st.plotly_chart(build_job_trend_chart(filtered_jobs_df), use_container_width=True)
    with col6:
        st.plotly_chart(build_salary_distribution_chart(salaries_df), use_container_width=True)

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #9ca3af; font-size: 0.85rem;'>"
        "Data sources: LinkedIn job postings | Last updated: June 2025"
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
