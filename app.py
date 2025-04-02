import streamlit as st
from JobRecommendation import JobRecommender
from pathlib import Path

# App configuration
st.set_page_config(
    page_title="Professional Job Recommender",
    layout="wide"
)

def initialize_recommender():
    """Initialize with error handling"""
    try:
        return JobRecommender()
    except Exception as e:
        st.error(f"System initialization failed: {str(e)}")
        st.stop()

def get_user_skills(skill_columns):
    """Create interactive skill input form"""
    st.sidebar.header("Your Skills (0-4)")
    user_skills = {}
    
    skill_groups = {
        'Programming': ['Python', 'Java', 'JavaScript'],
        'Data': ['SQL', 'Data_Analysis', 'Machine_Learning'],
        'Infrastructure': ['Cloud', 'DevOps'],
        'Specialized': ['Web_Dev', 'Mobile_Dev']
    }
    
    for group, skills in skill_groups.items():
        with st.sidebar.expander(group):
            for skill in skills:
                if skill in skill_columns:
                    user_skills[skill] = st.slider(
                        skill.replace('_', ' '),
                        min_value=0,
                        max_value=4,
                        value=0,
                        step=1
                    )
    return user_skills

def main():
    st.title("Professional Job Recommender")
    
    # Initialize system
    recommender = initialize_recommender()
    
    # Job type selection
    job_type = st.selectbox(
        "Select job category:",
        options=recommender.df['Job_Type'].unique()
    )
    
    # Skill input
    user_skills = get_user_skills(recommender.skill_columns)
    
    # Get recommendations
    if st.button("Get Recommendations"):
        with st.spinner("Finding best matches..."):
            results = recommender.recommend(job_type, user_skills)
            
            if not results.empty:
                st.success(f"Top {job_type} Jobs for You:")
                for _, row in results.iterrows():
                    with st.expander(f"{row['Job_Title']} ({row['Match_Score']:.0f}% match)"):
                        st.write("**Required Skills:**")
                        for skill in recommender.skill_columns:
                            if row[skill] > 0:
                                st.write(f"- {skill.replace('_', ' ')} (Level {int(row[skill])})")
            else:
                st.warning("No matching jobs found. Try adjusting your skills.")

if __name__ == "__main__":
    main()
