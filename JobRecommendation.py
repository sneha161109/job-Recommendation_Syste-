import pandas as pd
from sklearn.neighbors import NearestNeighbors

class JobRecommender:
    def __init__(self, data_path='job_database.csv'):
        self.df = pd.read_csv(data_path)
        self.skill_columns = [col for col in self.df.columns if col not in ['Job_Title', 'Job_Type']]
        
    def recommend(self, job_type, user_skills, n_recommendations=3):
        # Filter by job type
        type_filtered = self.df[self.df['Job_Type'] == job_type]
        
        if len(type_filtered) == 0:
            return pd.DataFrame()
        
        # Prepare model
        model = NearestNeighbors(n_neighbors=n_recommendations, metric='hamming')
        model.fit(type_filtered[self.skill_columns])
        
        # Prepare input
        input_vector = [[user_skills.get(skill, 0) for skill in self.skill_columns]]
        distances, indices = model.kneighbors(input_vector)
        
        # Format results
        results = type_filtered.iloc[indices[0]].copy()
        results['Match_Score'] = (1 - distances[0]) * 100
        return results[['Job_Title', 'Match_Score'] + self.skill_columns]
