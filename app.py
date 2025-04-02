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
    
    # Skill input
    st.sidebar.header("Your Skills (0-4)")
    user_skills = {}
    for skill in recommender.skill_columns:
        user_skills[skill] = st.sidebar.slider(
            skill.replace('_', ' '),
            min_value=0,
            max_value=4,
            value=0
        )
    
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
