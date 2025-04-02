import streamlit as st
from recommender import SkillRecommender

def main():
    st.title("🔍 Skill-Based Job Recommender")
    
    # Initialize recommender
    try:
        recommender = SkillRecommender()
    except Exception as e:
        st.error(f"Failed to load: {e}")
        return
    
    # Skill input
    st.sidebar.header("Your Skills")
    user_skills = {
        'Python': st.sidebar.checkbox("Python"),
        'SQL': st.sidebar.checkbox("SQL"),
        'Data_Analysis': st.sidebar.checkbox("Data Analysis"),
        'Machine_Learning': st.sidebar.checkbox("Machine Learning"),
        'Cloud': st.sidebar.checkbox("Cloud Computing")
    }
    
    # Get recommendations
    if st.button("Find Matching Jobs"):
        results = recommender.recommend({k: int(v) for k, v in user_skills.items()})
        
        if not results.empty:
            st.success("Top Job Matches:")
            for _, row in results.iterrows():
                st.write(f"### {row['Job Title']}")
                st.progress(int(row['Match_Score']))
                st.write(f"**Match:** {row['Match_Score']:.0f}%")
                st.write("---")
        else:
            st.warning("No matches found. Try different skills.")

if __name__ == "__main__":
    main()
