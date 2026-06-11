"""
Skills Analysis Page

Deep dive into:
- Top 20 in-demand skills
- Skill frequency distribution
- Skill combinations
- Skills demand by experience level
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from collections import Counter


st.set_page_config(
    page_title="Skills Analysis",
    page_icon="📚",
    layout="wide",
)


@st.cache_data
def load_data():
    """Load skill and job datasets."""
    skills_df = pd.read_csv("data/skill_frequency.csv")
    jobs_with_skills_df = pd.read_csv("data/jobs_with_skills.csv")
    return skills_df, jobs_with_skills_df


def main():
    """Skills analysis dashboard."""
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
                background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
                border: 1px solid #7dd3fc;
                border-radius: 12px;
                padding: 18px 16px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="page-title">📚 Skills Analysis</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Understand the most in-demand skills and skill combinations</div>',
        unsafe_allow_html=True,
    )

    try:
        skills_df, jobs_with_skills_df = load_data()
    except FileNotFoundError as e:
        st.error(f"❌ Missing data file: {e}")
        st.stop()

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📊 Unique Skills", len(skills_df))
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("💼 Jobs Analyzed", len(jobs_with_skills_df))
        st.markdown("</div>", unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        avg_skills = jobs_with_skills_df['skill_count'].mean()
        st.metric("⚙️ Avg Skills/Job", f"{avg_skills:.1f}")
        st.markdown("</div>", unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        top_skill = skills_df.iloc[0]
        st.metric("🏆 Top Skill", top_skill["skill"] + f" ({int(top_skill['frequency'])})")
        st.markdown("</div>", unsafe_allow_html=True)

    # Top 20 Skills
    st.markdown("### 🏆 Top 20 In-Demand Skills")
    top_20_skills = skills_df.head(20)

    fig_top = px.bar(
        top_20_skills,
        x="frequency",
        y="skill",
        orientation="h",
        text="frequency",
        color="frequency",
        color_continuous_scale="Blues",
        title="Top 20 Skills Ranked by Frequency",
    )
    fig_top.update_layout(
        yaxis_title="",
        xaxis_title="Frequency",
        coloraxis_showscale=False,
        height=550,
        hovermode="y unified",
    )
    fig_top.update_traces(textposition="outside")
    fig_top.update_yaxes(categoryorder="total ascending")
    st.plotly_chart(fig_top, use_container_width=True)

    # Skill Frequency Distribution
    st.markdown("### 📊 Skill Frequency Distribution")
    fig_dist = px.histogram(
        skills_df,
        x="frequency",
        nbins=30,
        title="Distribution of Skill Mentions",
        opacity=0.8,
    )
    fig_dist.update_layout(
        xaxis_title="Frequency (Number of Job Postings)",
        yaxis_title="Number of Skills",
        height=400,
        hovermode="x unified",
    )
    st.plotly_chart(fig_dist, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Most Common Skill Frequency", int(skills_df["frequency"].max()))
    with col2:
        st.metric("Least Common Skill Frequency", int(skills_df["frequency"].min()))

    # Skill Combinations
    st.markdown("### 🔗 Top Skill Combinations")
    st.info(
        "This shows the most common pairs of skills that appear together in the same job posting."
    )

    # Parse skills from detected_skills field (pipe-separated)
    skill_combinations = Counter()
    for idx, row in jobs_with_skills_df.iterrows():
        detected = row['detected_skills']
        if pd.notna(detected):
            job_skills = [s.strip() for s in str(detected).split('|')]
            if len(job_skills) >= 2:
                for i in range(len(job_skills)):
                    for j in range(i + 1, len(job_skills)):
                        pair = tuple(sorted([job_skills[i], job_skills[j]]))
                        skill_combinations[pair] += 1

    if skill_combinations:
        top_combinations = skill_combinations.most_common(15)
        combo_df = pd.DataFrame(
            [
                {
                    "Skill 1": pair[0],
                    "Skill 2": pair[1],
                    "Frequency": count,
                    "Pair": f"{pair[0]} + {pair[1]}",
                }
                for pair, count in top_combinations
            ]
        )

        fig_combo = px.bar(
            combo_df,
            x="Frequency",
            y="Pair",
            color="Frequency",
            text="Frequency",
            color_continuous_scale="Tealgrn",
            title="Top 15 Skill Combinations",
            orientation="h",
        )
        fig_combo.update_layout(
            yaxis_title="",
            xaxis_title="Frequency",
            coloraxis_showscale=False,
            height=450,
            hovermode="y unified",
        )
        fig_combo.update_traces(textposition="outside")
        fig_combo.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig_combo, use_container_width=True)

        st.dataframe(combo_df[["Skill 1", "Skill 2", "Frequency"]], use_container_width=True, hide_index=True)
    else:
        st.info("No skill combinations found.")

    # Skills Demand Ranking
    st.markdown("### 📈 Skills Demand Ranking")
    st.subheader("Skills ranked by workplace demand (frequency)")

    display_df = skills_df[["skill", "frequency"]].copy()
    display_df["rank"] = range(1, len(display_df) + 1)
    display_df = display_df[["rank", "skill", "frequency"]].head(30)

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #9ca3af; font-size: 0.85rem;'>"
        "💡 Pro tip: Skills that appear together frequently in job postings are often complementary and valuable to combine."
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
