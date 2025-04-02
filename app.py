import streamlit as st
from jobrecommendation import AdvancedJobRecommender, ALL_SKILLS, TECH_SKILLS, DATA_SKILLS, CLOUD_SKILLS, BIG_DATA_SKILLS
import pandas as pd
import plotly.express as px

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
        page_title="Career Compass",
        page_icon="🧭",
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
    .match-card:hover {
        transform: translateY(-3px);
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

def get_user_skills():
    """Interactive skill proficiency input with guided assessment"""
    st.sidebar.header("🧠 Skill Assessment")
    
    with st.sidebar.expander("ℹ️ How to rate your skills", expanded=False):
        st.markdown("""
        - **0**: No experience
        - **1**: Basic (can complete simple tasks)
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
                    help=f"Rate your {skill} proficiency"
                )
    return skills

def get_user_preferences():
    """Collect user job preferences"""
    st.sidebar.header("🎯 Job Preferences")
    
    preferences = {
        'experience': st.selectbox(
            "Experience Level",
            ['All', 'Entry', 'Mid', 'Senior'],
            help="Target job seniority level"
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
            3, 15, 8,
            help="How many jobs to recommend"
        )
    }
    
    # Only apply industry filter if not 'Any'
    if preferences['industry'] == 'Any':
        preferences.pop('industry')
    
    return preferences

def display_recommendations(recommendations):
    """Interactive visualization of job matches"""
    if recommendations.empty:
        st.warning("No jobs match your criteria. Try adjusting your filters or skills.")
        return
    
    st.header("✨ Your Top Matches")
    st.caption(f"Showing {len(recommendations)} positions sorted by best fit")
    
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
                    if isinstance(job['Missing_Skills'], list) and len(job['Missing_Skills']) > 0:
                        st.warning(f"**To improve:** {', '.join(job['Missing_Skills'])}")
                    else:
                        st.success("You meet all required skills!")
    
    # Analytics tabs
    tab1, tab2 = st.tabs(["📊 Match Analysis", "📈 Skill Insights"])
    
    with tab1:
        fig = px.scatter(
            recommendations,
            x='Match_Score',
            y='Skill_Coverage',
            color='Experience',
            hover_name='Job Title',
            size='Match_Score',
            labels={
                'Match_Score': 'Overall Match (%)',
                'Skill_Coverage': 'Skill Coverage (%)'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Most Required Skills in Matches")
        skill_dist = recommender.get_skill_distribution(recommendations)
        st.bar_chart(skill_dist)

def main():
    setup_page()
    
    st.title("🧭 Career Compass")
    st.markdown("Discover your ideal tech role based on your skills and preferences")
    
    # Get user input
    skills = get_user_skills()
    preferences = get_user_preferences()
    
    # Generate recommendations
    if st.button("Find My Matches", type="primary", use_container_width=True):
        with st.spinner("Analyzing your profile against job market..."):
            recommendations = recommender.recommend_jobs(skills, preferences)
            display_recommendations(recommendations)

if __name__ == "__main__":
    main()
