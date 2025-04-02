import streamlit as st
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from streamlit_tags import st_tags

# Load data
@st.cache_data
def load_data():
    return pd.read_csv('job_data.csv')

# Skill categories
TECH_SKILLS = ['Python', 'SQL', 'R', 'Java', 'JavaScript']
DATA_SKILLS = ['DataViz', 'Stats', 'ML', 'DL']
CLOUD_SKILLS = ['Cloud', 'AWS', 'Azure', 'GCP']
BIG_DATA_SKILLS = ['Spark', 'Kafka']
ALL_SKILLS = TECH_SKILLS + DATA_SKILLS + CLOUD_SKILLS + BIG_DATA_SKILLS

def main():
    st.set_page_config(layout="wide", page_title="🚀 Interactive Job Finder")
    
    # Custom CSS for better visuals
    st.markdown("""
    <style>
    .match-card {
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transition: transform 0.3s;
    }
    .match-card:hover {
        transform: translateY(-5px);
    }
    .skill-pill {
        display: inline-block;
        padding: 5px 10px;
        margin: 2px;
        border-radius: 20px;
        background-color: #f0f2f6;
        font-size: 0.8em;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("🚀 Interactive Job Finder")
    st.markdown("### Discover your perfect tech role based on your skills")
    
    df = load_data()
    
    # Interactive skill input
    with st.expander("✨ Build Your Skill Profile", expanded=True):
        tab1, tab2 = st.tabs(["🏷️ Checkbox Selector", "🔍 Free Input"])
        
        with tab1:
            cols = st.columns(2)
            with cols[0]:
                st.subheader("Programming")
                tech_skills = {skill: st.checkbox(skill, key=f"tech_{skill}") for skill in TECH_SKILLS}
                
                st.subheader("Cloud Platforms")
                cloud_skills = {skill: st.checkbox(skill, key=f"cloud_{skill}") for skill in CLOUD_SKILLS}
            
            with cols[1]:
                st.subheader("Data Science")
                data_skills = {skill: st.checkbox(skill, key=f"data_{skill}") for skill in DATA_SKILLS}
                
                st.subheader("Big Data Tools")
                big_data_skills = {skill: st.checkbox(skill, key=f"bigdata_{skill}") for skill in BIG_DATA_SKILLS}
        
        with tab2:
            user_skill_input = st_tags(
                label="Type or paste your skills (comma separated):",
                text='e.g., Python, SQL, Machine Learning',
                value=[],
                suggestions=ALL_SKILLS,
                maxtags=15
            )
            st.caption("We'll automatically match these to our skill categories")
    
    # Process skill input
    user_skills = {**tech_skills, **data_skills, **cloud_skills, **big_data_skills}
    
    # Map free input to our skill categories
    for skill in user_skill_input:
        normalized_skill = skill.strip().lower()
        for defined_skill in ALL_SKILLS:
            if defined_skill.lower() in normalized_skill:
                user_skills[defined_skill] = True
    
    # Interactive filters
    with st.sidebar:
        st.header("🔦 Refine Your Search")
        
        experience = st.select_slider(
            "Experience Level",
            options=['Entry', 'Mid', 'Senior', 'All Levels'],
            value='All Levels'
        )
        
        remote_only = st.toggle("Remote Only", True)
        
        min_match = st.slider(
            "Minimum Match %",
            min_value=50, max_value=100, value=70
        )
        
        num_recommendations = st.slider(
            "Number of Recommendations",
            min_value=3, max_value=15, value=5
        )
    
    # Prepare input vector
    user_input = [1 if user_skills.get(skill, False) else 0 for skill in ALL_SKILLS]
    
    # Filter jobs
    filtered_df = df.copy()
    if experience != 'All Levels':
        filtered_df = filtered_df[filtered_df['Experience'] == experience]
    if remote_only:
        filtered_df = filtered_df[filtered_df['Remote'] == 1]
    
    # Train model and get recommendations
    if not filtered_df.empty:
        model = NearestNeighbors(n_neighbors=num_recommendations, metric='jaccard')
        model.fit(filtered_df[ALL_SKILLS])
        
        distances, indices = model.kneighbors([user_input])
        recommendations = filtered_df.iloc[indices[0]]
        match_percentages = 100 - (distances[0] * 100)
        
        # Display results
        st.subheader("🎯 Your Personalized Recommendations")
        st.caption(f"Showing {len(recommendations)} roles matching at least {min_match}% of your skills")
        
        for i, (_, row) in enumerate(recommendations.iterrows()):
            if match_percentages[i] >= min_match:
                with st.container():
                    match_html = f"""
                    <div class="match-card" style="border-left: 5px solid {'#4CAF50' if match_percentages[i] > 80 else '#FFC107' if match_percentages[i] > 65 else '#F44336'}">
                        <h3>{row['Job Title']}</h3>
                        <div style="display: flex; justify-content: space-between;">
                            <div>
                                <span style="color: {'#4CAF50' if row['Remote'] else '#F44336'}">
                                    {'🌍 Remote' if row['Remote'] else '🏢 On-site'}
                                </span> | 
                                <span>📊 {row['Experience']} Level</span>
                            </div>
                            <span style="font-weight: bold; color: {'#4CAF50' if match_percentages[i] > 80 else '#FFC107' if match_percentages[i] > 65 else '#F44336'}">
                                {match_percentages[i]:.0f}% Match
                            </span>
                        </div>
                        <div style="margin: 10px 0;">
                            {" ".join([f'<span class="skill-pill">{skill}</span>' for skill in ALL_SKILLS if row[skill]])}
                        </div>
                    </div>
                    """
                    st.markdown(match_html, unsafe_allow_html=True)
                    
                    # Skill gap analysis
                    required_skills = [skill for skill in ALL_SKILLS if row[skill]]
                    missing_skills = [skill for skill in required_skills if not user_skills.get(skill, False)]
                    
                    if missing_skills:
                        with st.expander("🔍 Skill Gap Analysis"):
                            st.warning(f"To fully qualify for this role, consider developing these skills:")
                            for skill in missing_skills:
                                st.markdown(f"- {skill}")
                                # Could add links to learning resources here
                    
                    st.markdown("---")
    
        # Visual summary
        with st.expander("📊 Recommendation Summary"):
            st.subheader("Your Skill Profile vs Recommended Jobs")
            
            # Create a skill matrix visualization
            skill_matrix = pd.DataFrame({
                'Your Skills': [1 if user_skills.get(skill, False) else 0 for skill in ALL_SKILLS],
                **{row['Job Title']: [row[skill] for skill in ALL_SKILLS] 
                   for _, row in recommendations.iterrows()}
            }, index=ALL_SKILLS)
            
            st.dataframe(
                skill_matrix.style.applymap(
                    lambda x: 'background-color: #4CAF50' if x == 1 else 'background-color: #F44336'
                ),
                use_container_width=True
            )
    else:
        st.warning("No jobs match your current filters. Try adjusting your criteria.")

if __name__ == "__main__":
    main()
