import streamlit as st
from JobRecommendation import JobRecommender

# Initialize recommender
recommender = JobRecommender()

# Job type selection
JOB_TYPES = {
    'Data': ['Data Scientist', 'Data Analyst', 'ML Engineer'],
    'Engineering': ['Backend Developer', 'Frontend Developer', 'DevOps Engineer'],
    'Security': ['Cybersecurity Specialist'],
    'Mobile': ['iOS Developer', 'Android Developer']
}

def main():
    st.title("🧠 Smart Job Recommender Pro")
    
    # Job type selection
    selected_type = st.selectbox(
        "Select your desired job category:",
        list(JOB_TYPES.keys())
    
    # Dynamic skill selection
    st.sidebar.header("Skill Assessment")
    user_skills = {}
    
    skill_groups = {
        'Programming': ['Python', 'Java', 'JavaScript'],
        'Data': ['SQL', 'Data_Analysis', 'Machine_Learning', 'AI'],
        'Infrastructure': ['Cloud', 'DevOps'],
        'Specialized': ['Web_Dev', 'Mobile_Dev', 'Cybersecurity']
    }
    
    for group, skills in skill_groups.items():
        with st.sidebar.expander(group):
            for skill in skills:
                user_skills[skill] = st.select_slider(
                    skill,
                    options=[0, 1, 2, 3, 4],
                    value=0,
                    help="0=None, 1=Basic, 2=Intermediate, 3=Advanced, 4=Expert"
                )
    
    if st.button("Get Recommendations"):
        results = recommender.recommend(
            job_type=selected_type,
            user_skills=user_skills
        )
        
        if not results.empty:
            st.success(f"Top {selected_type} Roles For You:")
            for _, row in results.iterrows():
                with st.expander(f"{row['Job_Title']} - {row['Match_Score']:.0f}% Match"):
                    st.write("**Required Skills:**")
                    for skill in recommender.skill_columns:
                        if row[skill] > 0:
                            st.write(f"- {skill.replace('_', ' ')} (Level {row[skill]})")
        else:
            st.warning("No matches found. Try adjusting your filters.")

if __name__ == "__main__":
    main()
