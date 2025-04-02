import streamlit as st
from jobrecommendation import JobRecommender
import plotly.express as px

# Initialize recommender
recommender = JobRecommender()

def get_user_skills():
    """Get user skill inputs with expandable categories"""
    st.sidebar.header("Your Skill Profile")
    skills = {}
    
    categories = {
        "Programming": ['Python','SQL','R','Java','JavaScript'],
        "Data Science": ['DataViz','Stats','ML','DL'],
        "Cloud": ['Cloud','AWS','Azure','GCP'],
        "Big Data": ['Spark','Kafka']
    }
    
    for category, skill_list in categories.items():
        with st.sidebar.expander(category, expanded=True):
            for skill in skill_list:
                skills[skill] = st.slider(
                    skill, 0, 4, 0,
                    help="0=None, 1=Basic, 2=Intermediate, 3=Advanced, 4=Expert"
                )
    return skills

def show_recommendations(recommendations):
    """Display recommendations with visualizations"""
    if recommendations.empty:
        st.warning("No jobs match your criteria. Try adjusting filters.")
        return
    
    st.header("Top Job Matches")
    
    # Show match metrics
    cols = st.columns(3)
    cols[0].metric("Total Matches", len(recommendations))
    cols[1].metric("Best Match", f"{recommendations.iloc[0]['Match_Score']:.1f}%")
    cols[2].metric("Avg Match", f"{recommendations['Match_Score'].mean():.1f}%")
    
    # Job cards
    for _, job in recommendations.iterrows():
        with st.expander(f"{job['Job Title']} ({job['Experience']}) - {job['Match_Score']:.1f}%", expanded=True):
            c1, c2 = st.columns([1, 3])
            with c1:
                st.metric("Match", f"{job['Match_Score']:.1f}%")
                st.caption(f"Industry: {job['Industry']}")
                st.caption(f"Remote: {'✅' if job['Remote'] else '❌'}")
            
            with c2:
                # Show required skills
                required_skills = [s for s in recommender.skills if job[s] > 0]
                st.write("**Required Skills:** " + ", ".join(required_skills))
                
                # Skill gap analysis
                missing = [s for s in required_skills if user_skills.get(s, 0) < job[s]]
                if missing:
                    st.warning(f"Skill gap: {', '.join(missing)}")

    # Visualization
    st.header("Match Analysis")
    fig = px.scatter(
        recommendations,
        x='Match_Score',
        y='Experience',
        color='Industry',
        size='Match_Score',
        hover_name='Job Title'
    )
    st.plotly_chart(fig, use_container_width=True)

def main():
    st.set_page_config(page_title="Job Recommender", layout="wide")
    st.title("📊 Advanced Job Recommender")
    
    # Get user inputs
    user_skills = get_user_skills()
    
    # Filters
    st.sidebar.header("Filters")
    filters = {
        'experience': st.sidebar.selectbox("Experience Level", ['All','Entry','Mid','Senior']),
        'remote': st.sidebar.checkbox("Remote Only", True),
        'industry': st.sidebar.selectbox(
            "Industry", 
            ['All'] + sorted(recommender.df['Industry'].unique())
        )
    }
    
    # Get recommendations
    if st.button("Find Matching Jobs"):
        with st.spinner("Finding best matches..."):
            recommendations = recommender.recommend(user_skills, filters)
            show_recommendations(recommendations)

if __name__ == "__main__":
    main()
