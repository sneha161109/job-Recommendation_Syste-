import streamlit as st
import pandas as pd
from sklearn.neighbors import NearestNeighbors

# Load the dataset
data = pd.read_csv('job_data.csv')

# Separate features and target
X = data[['Python', 'SQL', 'Data Analysis', 'Machine Learning', 'Cloud Computing']]
y = data['Job Title']

# Train the Nearest Neighbors model
model = NearestNeighbors(n_neighbors=5, metric='hamming')
model.fit(X)

# Streamlit app
st.title("Job Recommendation System")
st.write("Please answer the following questions with 1 (Yes) or 0 (No).")

python_skill = st.radio("Do you know Python?", (1, 0))
sql_skill = st.radio("Do you know SQL?", (1, 0))
data_analysis_skill = st.radio("Do you know Data Analysis?", (1, 0))
machine_learning_skill = st.radio("Do you know Machine Learning?", (1, 0))
cloud_computing_skill = st.radio("Do you know Cloud Computing?", (1, 0))

if st.button("Recommend Jobs"):
    user_input = [[python_skill, sql_skill, data_analysis_skill, machine_learning_skill, cloud_computing_skill]]
    distances, indices = model.kneighbors(user_input)
    recommended_jobs = y.iloc[indices[0]].tolist()
    
    st.success("Recommended Jobs:")
    for job in recommended_jobs:
        st.write(f"- {job}")