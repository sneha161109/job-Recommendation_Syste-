import streamlit as st
from JobRecommendation import JobRecommender  # Exact filename match

def main():
    st.title("Job Recommendation System")
    
    # Initialize with error handling
    try:
        recommender = JobRecommender()
    except Exception as e:
        st.error(f"Failed to initialize: {str(e)}")
        st.stop()
    
    # Job type selection
    job_type = st.selectbox(
        "Select job category:",
        options=recommender.df['Job_Type'].unique()
    )
    
    # Skill input with checkboxes
    st.sidebar.header("Your Skills")
    user_skills = {}
    for skill in recommender.skill_columns:
        # Using checkboxes (1 if checked, 0 if not)
        user_skills[skill] = 1 if st.sidebar.checkbox(
            skill.replace('_', ' '),
            value=False,
            key=skill
        ) else 0
    
    # Get recommendations
    if st.button("Find Jobs"):
        results = recommender.recommend(job_type, user_skills)
        
        if not results.empty:
            st.success("Top Recommendations:")
            for _, row in results.iterrows():
                with st.expander(f"{row['Job_Title']} ({row['Match_Score']:.0f}% match)"):
                    st.write("**Required Skills:**")
                    for skill in recommender.skill_columns:
                        if row[skill] > 0:
                            st.write(f"- {skill.replace('_', ' ')}")
        else:
            st.warning("No matches found")

if __name__ == "__main__":
    main()
