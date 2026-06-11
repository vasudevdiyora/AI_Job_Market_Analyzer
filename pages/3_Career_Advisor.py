"""
Career Advisor Page

Interactive career exploration:
- Select a role
- View required skills
- See salary expectations
- Understand market demand
- Get learning path recommendations
"""

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Career Advisor",
    page_icon="🚀",
    layout="wide",
)


@st.cache_data
def load_data():
    """Load all datasets."""
    jobs_df = pd.read_csv("data/jobs_cleaned.csv")
    salaries_df = pd.read_csv("data/salaries_cleaned.csv")
    skills_df = pd.read_csv("data/skill_frequency.csv")
    jobs_with_skills_df = pd.read_csv("data/jobs_with_skills.csv")
    return jobs_df, salaries_df, skills_df, jobs_with_skills_df


def main():
    """Career advisor interactive dashboard."""
    st.markdown(
        """
        <style>
            .page-title {
                font-size: 2.2rem;
                font-weight: 800;
                margin-bottom: 0.1rem;
                color: #1f2937;
            }
            .page-subtitle {
                color: #6b7280;
                margin-bottom: 1.5rem;
                font-size: 1.05rem;
            }
            .metric-card {
                background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
                border: 1px solid #86efac;
                border-radius: 12px;
                padding: 18px 16px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            }
            .role-description {
                background-color: #f3f4f6;
                padding: 16px;
                border-radius: 8px;
                margin: 12px 0;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="page-title">🚀 Career Advisor</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Explore career paths and market demand for different roles</div>',
        unsafe_allow_html=True,
    )

    try:
        jobs_df, salaries_df, skills_df, jobs_with_skills_df = load_data()
    except FileNotFoundError as e:
        st.error(f"❌ Missing data file: {e}")
        st.stop()

    # Career paths dictionary with descriptions and skills from actual data
    # Only using skills that exist in skill_frequency.csv
    career_paths = {
        "Data Analyst": {
            "description": "Analyze data to help businesses make decisions. Focus on SQL, visualization, and statistical analysis.",
            "skills": ["SQL", "Data Analysis", "Tableau", "Power BI", "Excel"],
            "experience": "Entry to Mid-level",
            "keywords": ["analyst", "data analyst"],
        },
        "Data Scientist": {
            "description": "Build predictive models and machine learning solutions. Combines statistics, programming, and domain expertise.",
            "skills": ["Python", "Machine Learning", "SQL", "Data Analysis", "AWS"],
            "experience": "Mid to Senior level",
            "keywords": ["data scientist", "scientist"],
        },
        "Backend Developer": {
            "description": "Build server-side applications and APIs. Focus on databases, frameworks, and scalability.",
            "skills": ["Python", "SQL", "Java", "Docker", "Git"],
            "experience": "Entry to Senior level",
            "keywords": ["backend", "developer", "python", "java"],
        },
        "Frontend Developer": {
            "description": "Build user interfaces and web applications. Focus on JavaScript and modern frameworks.",
            "skills": ["JavaScript", "Python", "Git", "Docker", "Azure"],
            "experience": "Entry to Mid-level",
            "keywords": ["frontend", "developer"],
        },
        "Full Stack Developer": {
            "description": "Work on both frontend and backend. Combines web development with server-side skills.",
            "skills": ["Python", "JavaScript", "SQL", "Docker", "Git"],
            "experience": "Mid to Senior level",
            "keywords": ["full stack", "fullstack", "developer"],
        },
    }

    # Role selector
    st.markdown("### 🎯 Explore a Career Path")
    selected_role = st.selectbox(
        "Select a role to explore:",
        list(career_paths.keys()),
        index=0,
    )

    role_info = career_paths[selected_role]

    # Role description
    st.markdown('<div class="role-description">', unsafe_allow_html=True)
    st.markdown(f"**{selected_role}** — {role_info['description']}")
    st.markdown(f"**Experience Level:** {role_info['experience']}")
    st.markdown("</div>", unsafe_allow_html=True)

    # Key metrics for role - use multiple keyword patterns for matching
    keywords = role_info.get("keywords", [selected_role.lower()])
    role_jobs = jobs_df.copy()
    
    # Match jobs by any of the role keywords
    mask = role_jobs["title"].str.lower().str.contains("|".join(keywords), na=False, regex=True)
    role_jobs = role_jobs[mask]
    
    role_salaries = salaries_df.copy()
    mask_sal = role_salaries["job_title"].str.lower().str.contains("|".join(keywords), na=False, regex=True)
    role_salaries = role_salaries[mask_sal]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("💼 Job Postings", len(role_jobs))
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        avg_salary = role_salaries["salary_in_usd"].mean() if len(role_salaries) > 0 else 0
        st.metric("💰 Avg Salary", f"${avg_salary:,.0f}" if avg_salary > 0 else "N/A")
        st.markdown("</div>", unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        companies = role_jobs["company"].nunique() if len(role_jobs) > 0 else 0
        st.metric("🏢 Companies Hiring", companies)
        st.markdown("</div>", unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        demand = len(role_jobs)
        if demand > 100:
            demand_level = "🔥 High"
        elif demand > 50:
            demand_level = "📈 Medium"
        else:
            demand_level = "📊 Low"
        st.metric("📊 Market Demand", demand_level)
        st.markdown("</div>", unsafe_allow_html=True)

    # Required Skills
    st.markdown("### 📚 Required Skills to Master")
    skill_cols = st.columns(len(role_info["skills"]))
    for i, skill in enumerate(role_info["skills"]):
        with skill_cols[i]:
            st.info(f"✓ {skill}")

    # Learning Path
    st.markdown("### 🛤️ Suggested Learning Path")
    learning_phases = {
        "Phase 1: Foundations": [
            "Learn core fundamentals (6-8 weeks)",
            "Understand basic concepts and best practices",
            "Complete beginner-friendly courses",
        ],
        "Phase 2: Core Skills": [
            "Focus on primary tools/languages (3-4 months)",
            "Build practice projects",
            "Develop proficiency in main technologies",
        ],
        "Phase 3: Specialization": [
            "Learn complementary skills (2-3 months)",
            "Study real-world applications",
            "Explore advanced topics",
        ],
        "Phase 4: Practice & Portfolio": [
            "Build portfolio projects (ongoing)",
            "Contribute to open source",
            "Create case studies showcasing your work",
        ],
    }

    for phase, steps in learning_phases.items():
        with st.expander(f"📌 {phase}"):
            for step in steps:
                st.markdown(f"• {step}")

    # Salary Distribution for Role
    if len(role_salaries) > 0:
        st.markdown("### 💰 Salary Distribution for This Role")

        fig_salary = px.histogram(
            role_salaries,
            x="salary_in_usd",
            nbins=20,
            title=f"Salary Distribution for {selected_role}",
            opacity=0.8,
        )
        fig_salary.update_layout(
            xaxis_title="Salary (USD)",
            yaxis_title="Count",
            height=400,
            hovermode="x unified",
        )
        st.plotly_chart(fig_salary, use_container_width=True)

        # Statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Min Salary", f"${role_salaries['salary_in_usd'].min():,.0f}")
        with col2:
            st.metric("Median Salary", f"${role_salaries['salary_in_usd'].median():,.0f}")
        with col3:
            st.metric("Mean Salary", f"${role_salaries['salary_in_usd'].mean():,.0f}")
        with col4:
            st.metric("Max Salary", f"${role_salaries['salary_in_usd'].max():,.0f}")

    # Top Hiring Locations
    if len(role_jobs) > 0:
        st.markdown("### 📍 Top Hiring Locations for This Role")

        top_locations = (
            role_jobs["location"]
            .dropna()
            .value_counts()
            .head(10)
            .reset_index()
        )
        top_locations.columns = ["location", "count"]

        fig_locations = px.bar(
            top_locations,
            x="count",
            y="location",
            color="count",
            text="count",
            color_continuous_scale="Reds",
            title=f"Top 10 Locations Hiring {selected_role}s",
            orientation="h",
        )
        fig_locations.update_layout(
            xaxis_title="Number of Jobs",
            yaxis_title="",
            coloraxis_showscale=False,
            height=400,
            hovermode="y unified",
        )
        fig_locations.update_traces(textposition="outside")
        fig_locations.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig_locations, use_container_width=True)

    # Insights
    st.markdown("### 💡 Market Insights")
    insights = [
        f"There are currently **{len(role_jobs)}** open positions for {selected_role}.",
        f"The average salary for this role is **${role_salaries['salary_in_usd'].mean():,.0f}**." if len(role_salaries) > 0 else "Salary data not available.",
        f"**{role_jobs['company'].nunique()}** companies are actively hiring for this role." if len(role_jobs) > 0 else "No hiring data available.",
        "The most in-demand version of this role requires a combination of technical and soft skills.",
        "Building a portfolio of projects is crucial for landing interviews in this field.",
    ]

    for insight in insights:
        st.markdown(f"✨ {insight}")

    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #9ca3af; font-size: 0.85rem;'>"
        "🎓 Remember: Learning these skills takes time and practice. Focus on building real-world projects!"
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
