import streamlit as st
from jobrecommendation import JobRecommender

# Initialize recommender
recommender = JobRecommender()

def get_user_skills():
    st.sidebar.header("Your Skill Profile (0-4)")
    skills = {}
    
    categories = {
        "Programming": ['Python','SQL','R','Java','JavaScript'],
        "Data Science": ['DataViz','Stats','ML','DL'],
        "Cloud": ['Cloud','AWS','Azure','GCP'],
        "Big Data": ['Spark','Kafka']
    }
    
    for category, skill_list in categories.items():
        with st.sidebar.expander(category):
            for skill in skill_list:
                skills[skill] = st.slider(skill, 0, 4, 0)
    return skills

def show_recommendations(recommendations):
    if recommendations.empty:
        st.warning("No jobs match your criteria")
        return
    
    st.header(f"Top {len(recommendations)} Matches")
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Highest Match", f"{recommendations.iloc[0]['Match_Score']:.1f}%")
    col2.metric("Average Match", f"{recommendations['Match_Score'].mean():.1f}%")
    col3.metric("Lowest Match", f"{recommendations.iloc[-1]['Match_Score']:.1f}%")
    
    # Job cards
    for _, job in recommendations.iterrows():
        with st.expander(f"{job['Job Title']} ({job['Experience']}) - {job['Match_Score']:.1f}%"):
            st.write(f"**Industry:** {job['Industry']} | **Remote:** {'✅' if job['Remote'] else '❌'}")
            
            # Required skills
            req_skills = [s for s in recommender.skills if job[s] > 0]
            st.write("**Required Skills:**", ", ".join(req_skills))
            
            # Simple bar chart of skill requirements
            skill_data = pd.DataFrame({
                'Skill': req_skills,
                'Level': [job[s] for s in req_skills]
            })
            st.bar_chart(skill_data.set_index('Skill'))

def main():
    st.set_page_config(page_title="Job Recommender", layout="wide")
    st.title("Job Recommendation Engine")
    
    # User inputs
    user_skills = get_user_skills()
    
    # Filters
    st.sidebar.header("Filters")
    filters = {
        'experience': st.sidebar.selectbox("Experience", ['All','Entry','Mid','Senior']),
        'remote': st.sidebar.checkbox("Remote Only", True),
        'industry': st.sidebar.selectbox("Industry", ['All'] + sorted(recommender.df['Industry'].unique()))
    }
    
    if st.button("Find Jobs"):
        recommendations = recommender.recommend(user_skills, filters)
        show_recommendations(recommendations)

if __name__ == "__main__":
    main()
