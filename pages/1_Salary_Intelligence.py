"""
Salary Intelligence Page

Analysis of salary trends by:
- Experience level
- Company size
- Remote work type
- Top paying roles
"""

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Salary Intelligence",
    page_icon="💰",
    layout="wide",
)


@st.cache_data
def load_data():
    """Load salary and job datasets."""
    jobs_df = pd.read_csv("data/jobs_cleaned.csv")
    salaries_df = pd.read_csv("data/salaries_cleaned.csv")
    return jobs_df, salaries_df


def main():
    """Salary intelligence dashboard."""
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
                background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
                border: 1px solid #fcd34d;
                border-radius: 12px;
                padding: 18px 16px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="page-title">💰 Salary Intelligence</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Deep dive into salary trends and compensation patterns</div>',
        unsafe_allow_html=True,
    )

    try:
        jobs_df, salaries_df = load_data()
    except FileNotFoundError as e:
        st.error(f"❌ Missing data file: {e}")
        st.stop()

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📊 Total Salaries", len(salaries_df))
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("💵 Avg Salary", f"${salaries_df['salary_in_usd'].mean():,.0f}")
        st.markdown("</div>", unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📈 Median Salary", f"${salaries_df['salary_in_usd'].median():,.0f}")
        st.markdown("</div>", unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        salary_range = salaries_df['salary_in_usd'].max() - salaries_df['salary_in_usd'].min()
        st.metric("💹 Range (USD)", f"${salary_range:,.0f}")
        st.markdown("</div>", unsafe_allow_html=True)

    # Salary by Experience Level
    st.markdown("### 🎯 Salary by Experience Level")
    if "experience_level" in salaries_df.columns:
        salary_by_exp = salaries_df.groupby("experience_level")["salary_in_usd"].agg(["mean", "median", "count"]).reset_index()
        salary_by_exp.columns = ["Experience Level", "Average Salary", "Median Salary", "Count"]

        fig_exp = px.bar(
            salary_by_exp,
            x="Experience Level",
            y="Average Salary",
            color="Average Salary",
            text="Average Salary",
            color_continuous_scale="YlOrRd",
            title="Average Salary by Experience Level",
        )
        fig_exp.update_layout(
            yaxis_title="Salary (USD)",
            coloraxis_showscale=False,
            height=400,
            hovermode="x unified",
        )
        fig_exp.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
        st.plotly_chart(fig_exp, use_container_width=True)

        # Table view
        st.dataframe(salary_by_exp, use_container_width=True, hide_index=True)
    else:
        st.info("Experience level data not available.")

    # Salary by Company Size
    st.markdown("### 🏢 Salary by Company Size")
    if "company_size" in salaries_df.columns:
        salary_by_size = salaries_df.groupby("company_size")["salary_in_usd"].agg(["mean", "median", "count"]).reset_index()
        salary_by_size.columns = ["Company Size", "Average Salary", "Median Salary", "Count"]

        fig_size = px.box(
            salaries_df[salaries_df["company_size"].notna()],
            x="company_size",
            y="salary_in_usd",
            color="company_size",
            title="Salary Distribution by Company Size",
        )
        fig_size.update_layout(
            xaxis_title="Company Size",
            yaxis_title="Salary (USD)",
            height=400,
            showlegend=False,
            hovermode="x unified",
        )
        st.plotly_chart(fig_size, use_container_width=True)

        st.dataframe(salary_by_size, use_container_width=True, hide_index=True)
    else:
        st.info("Company size data not available.")

    # Salary by Remote Type
    st.markdown("### 🌐 Salary by Remote Work Type")
    if "remote_ratio" in salaries_df.columns:
        salary_by_remote = salaries_df.groupby("remote_ratio")["salary_in_usd"].agg(["mean", "median", "count"]).reset_index()
        salary_by_remote.columns = ["Remote Type", "Average Salary", "Median Salary", "Count"]

        fig_remote = px.bar(
            salary_by_remote,
            x="Remote Type",
            y="Average Salary",
            color="Average Salary",
            text="Average Salary",
            color_continuous_scale="Viridis",
            title="Average Salary by Remote Work Type",
        )
        fig_remote.update_layout(
            yaxis_title="Salary (USD)",
            coloraxis_showscale=False,
            height=400,
            hovermode="x unified",
        )
        fig_remote.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
        st.plotly_chart(fig_remote, use_container_width=True)

        st.dataframe(salary_by_remote, use_container_width=True, hide_index=True)
    else:
        st.info("Remote work type data not available.")

    # Top Paying Roles
    st.markdown("### 💎 Top 20 Highest Paying Job Titles")
    if "job_title" in salaries_df.columns:
        top_paying = salaries_df.groupby("job_title")["salary_in_usd"].agg(["mean", "count"]).reset_index()
        top_paying = top_paying[top_paying["count"] >= 2].sort_values("mean", ascending=False).head(20)
        top_paying.columns = ["Job Title", "Average Salary", "Count"]

        fig_top = px.bar(
            top_paying,
            x="Average Salary",
            y="Job Title",
            color="Average Salary",
            text="Average Salary",
            color_continuous_scale="RdYlGn",
            title="Top 20 Highest Paying Job Titles (min. 2 occurrences)",
            orientation="h",
        )
        fig_top.update_layout(
            xaxis_title="Average Salary (USD)",
            yaxis_title="",
            coloraxis_showscale=False,
            height=600,
            hovermode="y unified",
        )
        fig_top.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
        fig_top.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig_top, use_container_width=True)

        st.dataframe(top_paying, use_container_width=True, hide_index=True)
    else:
        st.info("Job title data not available.")

    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #9ca3af; font-size: 0.85rem;'>"
        "💡 Tip: Use the sidebar filters on the main page to narrow down results by location or company."
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
