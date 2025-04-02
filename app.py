import streamlit as st
import pandas as pd
from sklearn.neighbors import NearestNeighbors
import os

# Set page config
st.set_page_config(page_title="Job Recommendation System", page_icon="💼", layout="wide")

@st.cache_data
def load_data():
    """Load and cache the job data"""
    if not os.path.exists('job_data.csv'):
        st.error("Job data file not found! Please ensure 'job_data.csv' exists.")
        return None
    try:
        data = pd.read_csv('job_data.csv')
        required_columns = ['Python', 'SQL', 'Data Analysis', 'Machine Learning', 'Cloud Computing', 'Job Title']
        if not all(col in data.columns for col in required_columns):
            st.error("Required columns missing in the dataset!")
            return None
        return data
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def train_model(X):
    """Train and cache the recommendation model"""
    model = NearestNeighbors(n_neighbors=5, metric='hamming')
    model.fit(X)
    return model

def main():
    st.title("💼 Job Recommendation System")
    st.markdown("### Discover your ideal job based on your skills")
    
    # Load data
    data = load_data()
    if data is None:
        return
    
    # Prepare features and target
    X = data[['Python', 'SQL', 'Data Analysis', 'Machine Learning', 'Cloud Computing']]
    y = data['Job Title']
    
    # Train model
    model = train_model(X)
    
    # User input section
    st.sidebar.header("Your Skills Profile")
    st.sidebar.markdown("Please indicate which skills you have (1 = Yes, 0 = No)")
    
    with st.sidebar.form("skills_form"):
        python_skill = st.radio("Python", [1, 0], horizontal=True)
        sql_skill = st.radio("SQL", [1, 0], horizontal=True)
        data_analysis_skill = st.radio("Data Analysis", [1, 0], horizontal=True)
        machine_learning_skill = st.radio("Machine Learning", [1, 0], horizontal=True)
        cloud_computing_skill = st.radio("Cloud Computing", [1, 0], horizontal=True)
        submitted = st.form_submit_button("Get Recommendations")
    
    # Recommendation logic
    if submitted:
        user_input = [[python_skill, sql_skill, data_analysis_skill, 
                      machine_learning_skill, cloud_computing_skill]]
        
        try:
            distances, indices = model.kneighbors(user_input)
            recommended_jobs = y.iloc[indices[0]].tolist()
            
            st.success("🎯 Recommended Jobs For You:")
            cols = st.columns(2)
            for i, job in enumerate(recommended_jobs):
                cols[i%2].markdown(f"✅ **{job}**")
            
            # Show matching skills
            st.markdown("---")
            st.markdown("### Your Skills Match With:")
            matched_data = data.iloc[indices[0]]
            st.dataframe(matched_data, hide_index=True)
            
        except Exception as e:
            st.error(f"Error generating recommendations: {str(e)}")

if __name__ == "__main__":
    main()
