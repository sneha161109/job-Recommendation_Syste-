import streamlit as st
import pandas as pd
import plotly.express as px
from jobrecommendation import (
    AdvancedJobRecommender,
    ALL_SKILLS,
    TECH_SKILLS,
    DATA_SKILLS,
    CLOUD_SKILLS,
    BIG_DATA_SKILLS
)

# Initialize recommender
recommender = AdvancedJobRecommender()

# Skill categories for UI organization
SKILL_CATEGORIES = {
    "Programming": TECH_SKILLS,
    "Data Science": DATA_SKILLS,
    "Cloud Platforms": CLOUD_SKILLS,
    "Big Data Tools": BIG_DATA_SKILLS
}

def setup_page():
    """Configure page settings and styles"""
    st.set_page_config(
        page_title="Job Recommendation Engine",
        page_icon="💼",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.markdown("""
    <style>
    .match-card {
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s;
        border-left: 5px solid #4f46e5;
    }
    .skill-pill {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        margin: 0.25rem;
        border-radius: 1rem;
        background-color: #e0e7ff;
        color: #4f46e5;
        font-size: 0.85rem;
    }
    </style>
    """, unsafe_allow_html=True)

def get_skill_proficiency():
    """Interactive skill proficiency input"""
    st.sidebar.header("🛠 Skill Mastery Assessment")
    st.sidebar.markdown("Rate your proficiency (0-4):")
    
    with st.sidebar.expander("Skill Level Guide", expanded=False):
        st.markdown("""
        - **0**: No experience
        - **1**: Basic (simple tasks)
        - **2**: Intermediate (work independently)
        - **3**: Advanced (can mentor others)
        - **4**: Expert (industry-leading)
        """)
    
    skills = {}
    for category, category_skills in SKILL_CATEGORIES.items():
        with st.sidebar.expander(f"**{category}**", expanded=True):
            for skill in category_skills:
                skills[skill] = st.select_slider(
                    skill,
                    options=[0, 1, 2, 3, 4],
                    value=0,
                    help=f"Your {skill} proficiency level"
                )
    return skills

def get_user_preferences():
    """Collect user job preferences"""
    st.sidebar.header("🎯 Job Preferences")
    
    preferences = {
        'experience': st.selectbox(
            "Experience Level",
            ['All', 'Entry', 'Mid', 'Senior'],
            index=0
        ),
        'remote_only': st.toggle(
            "Remote Only", 
            True,
            help="Show only remote positions"
        ),
        'industry': st.selectbox(
            "Industry Preference",
            ['Any'] + list(recommender.df['Industry'].unique()),
            help="Filter by specific industry"
        ),
        'n_recommendations': st.slider(
            "Number of Recommendations",
            3, 15, 5,
            help="How many jobs to show"
        )
    }
    
    if preferences['industry'] == 'Any':
        preferences.pop('industry')
    
    return preferences

def display_recommendations(recommendations):
    """Interactive visualization of job matches"""
    if recommendations.empty:
        st.warning("No jobs match your criteria. Try adjusting your filters.")
        return
    
    st.header("✨ Your Top Matches")
    
    # Main recommendations view
    for _, job in recommendations.iterrows():
        with st.container():
            st.markdown(f"""
            <div class="match-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin: 0;">{job['Job Title']}</h3>
                    <span style="font-size: 1.2rem; font-weight: bold; color: #4f46e5;">
                        {job['Match_Score']:.0f}% Match
                    </span>
                </div>
                <div style="margin: 0.5rem 0; color: #64748b;">
                    {job['Experience']} Level • {job['Industry']} • {'🌍 Remote' if job['Remote'] else '🏢 On-site'}
                </div>
                <div style="margin: 0.5rem 0;">
                    {" ".join([f'<span class="skill-pill">{skill}</span>' for skill in ALL_SKILLS if job[skill] > 0])}
                </div>
                <div style="margin-top: 1rem;">
                    <strong>Tech Stack:</strong> {job['TechStack']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Skill gap analysis
            with st.expander("🔍 See skill requirements and gaps"):
                gap_cols = st.columns([1, 3])
                with gap_cols[0]:
                    st.metric("Skill Coverage", f"{job['Skill_Coverage']:.0f}%")
                    st.progress(job['Skill_Coverage']/100)
                with gap_cols[1]:
                    if job['Missing_Skills']:
                        st.warning(f"**Skills to improve:** {', '.join(job['Missing_Skills'])}")
                    else:
                        st.success("You meet all required skills!")

def main():
    setup_page()
    st.title("💼 Advanced Job Recommender")
    st.markdown("Find your ideal role based on your skills and preferences")
    
    # Get user input
    skills = get_skill_proficiency()
    preferences = get_user_preferences()
    
    # Generate recommendations
    if st.button("Find My Matches", type="primary", use_container_width=True):
        with st.spinner("Analyzing your profile against job market..."):
            recommendations = recommender.recommend_jobs(skills, preferences)
            display_recommendations(recommendations)

if __name__ == "__main__":
    main()
