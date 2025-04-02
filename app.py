import streamlit as st
from JobRecommendation import JobRecommender  # Matches your filename
from pathlib import Path

# App configuration
st.set_page_config(
    page_title="Job Recommendation System",
    layout="wide"
)

def main():
    st.title("Job Recommendation System")
    
    # Initialize with error handling
    try:
        recommender = JobRecommender()
        st.session_state.ready = True
    except Exception as e:
        st.error(f"System initialization failed: {str(e)}")
        st.session_state.ready = False
        return
    
    # Job type selection
    job_type = st.selectbox(
        "Select job category:",
        options=recommender.df['Job_Type'].unique()
    )
    
    # Skill input
    st.sidebar.header("Your Skill Levels (0-4)")
    user_skills = {}
    for skill in recommender.skill_columns:
        user_skills[skill] = st.sidebar.slider(
            skill.replace('_', ' '),
            min_value=0,
            max_value=4,
            value=0,
            step=1
        )
    
    # Get recommendations
    if st.button("Get Recommendations") and st.session_state.ready:
        with st.spinner("Finding best matches..."):
            results = recommender.recommend(job_type, user_skills)
            
            if not results.empty:
                st.success(f"Top {job_type} Jobs:")
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
