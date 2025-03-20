# Step 1: Import Libraries
import pandas as pd
from sklearn.neighbors import NearestNeighbors

# Step 2: Load the Dataset
data = pd.read_csv('job_data.csv')

# Step 3: Separate Features and Target
X = data[['Python', 'SQL', 'Data Analysis', 'Machine Learning', 'Cloud Computing']]  # Features
y = data['Job Title']  # Target

# Step 4: Train the Nearest Neighbors Model
model = NearestNeighbors(n_neighbors=5, metric='hamming')  # Use Hamming distance for binary data
model.fit(X)

# Step 5: Create a Recommendation Function
def recommend_jobs(python, sql, data_analysis, machine_learning, cloud_computing):
    user_input = [[python, sql, data_analysis, machine_learning, cloud_computing]]  # Create a feature vector
    distances, indices = model.kneighbors(user_input)  # Find nearest neighbors
    recommended_jobs = y.iloc[indices[0]].tolist()  # Get job titles of nearest neighbors
    return recommended_jobs

# Step 6: Take User Input
print("Welcome to the Job Recommendation System!")
print("Please answer the following questions with 1 (Yes) or 0 (No).")

python_skill = int(input("Do you know Python? (1 for Yes, 0 for No): "))
sql_skill = int(input("Do you know SQL? (1 for Yes, 0 for No): "))
data_analysis_skill = int(input("Do you know Data Analysis? (1 for Yes, 0 for No): "))
machine_learning_skill = int(input("Do you know Machine Learning? (1 for Yes, 0 for No): "))
cloud_computing_skill = int(input("Do you know Cloud Computing? (1 for Yes, 0 for No): "))

# Step 7: Validate Input
if not all(skill in [0, 1] for skill in [python_skill, sql_skill, data_analysis_skill, machine_learning_skill, cloud_computing_skill]):
    print("Invalid input! Please enter 1 (Yes) or 0 (No).")
else:
    # Step 8: Recommend Jobs
    recommended_jobs = recommend_jobs(python_skill, sql_skill, data_analysis_skill, machine_learning_skill, cloud_computing_skill)
    print("Recommended Jobs:")
    for job in recommended_jobs:
        print(f"- {job}")