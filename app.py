import streamlit as st
from jobrecommendation import AdvancedJobRecommender, ALL_SKILLS

# Initialize
recommender = AdvancedJobRecommender()

def get_skill_proficiency():
    """Interactive skill proficiency input"""
    st.sidebar.header("🛠 Skill Mastery Assessment")
    st.sidebar.markdown("Rate your proficiency for each skill (0 = None, 4 = Expert)")
    
    skills = {}
    for category, category_skills in SKILL_CATEGORIES.items():
        with st.sidebar.expander(f"**{category}**", expanded=True):
            for skill in category_skills:
                skills[skill] = st.slider(
                    skill,
                    min_value=0,
                    max_value=4,
                    value=0,
                    step=1,
                    help=f"0: None | 1: Basic | 2: Intermediate | 3: Advanced | 4: Expert"
                )
    return skills

def display_recommendations(recommendations):
    """Interactive results visualization"""
    tab1, tab2, tab3 = st.tabs(["Best Matches", "Skill Analysis", "Career Pathways"])
    
    with tab1:
        for _, job in recommendations.iterrows():
            with st.container():
                cols = st.columns([1, 4])
                cols[0].metric("Match", f"{job['Match_Score']:.1f}%")
                
                with cols[1]:
                    st.subheader(job['Job Title'])
                    prog_cols = st.columns(3)
                    prog_cols[0].progress(job['Match_Score']/100, text="Fit")
                    prog_cols[1].progress(job['Skill_Coverage'], text="Coverage")
                    prog_cols[2].markdown(f"**Level:** {job['Experience']}")
                    
                    if job['Remote']:
                        st.success("🌍 Remote position available")
    
    with tab2:
        st.vega_lite_chart({
            "mark": {"type": "circle", "size": 100},
            "encoding": {
                "x": {"field": "Match_Score", "type": "quantitative"},
                "y": {"field": "Skill_Coverage", "type": "quantitative"},
                "color": {"field": "Experience", "type": "nominal"}
            },
            "data": recommendations.to_dict(orient='records')
        }, use_container_width=True)
    
    with tab3:
        st.write("Skill development pathways...")  # Implement pathway logic

def main():
    # UI Config
    st.set_page_config(layout="wide")
    
    # Get user input
    skills = get_skill_proficiency()
    
    # Filters
    filters = {
        'experience': st.selectbox("Target Level", ['All', 'Entry', 'Mid', 'Senior']),
        'remote_only': st.toggle("Remote Only", True),
        'n_recommendations': st.slider("Number of Recommendations", 3, 20, 10)
    }
    
    # Generate recommendations
    if st.button("🔍 Find Ideal Jobs", type="primary"):
        with st.spinner("Finding your perfect matches..."):
            recommendations = recommender.recommend_jobs(skills, filters)
            display_recommendations(recommendations)

if __name__ == "__main__":
    main()
