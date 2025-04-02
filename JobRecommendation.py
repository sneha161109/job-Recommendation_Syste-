import pandas as pd
from sklearn.neighbors import NearestNeighbors

class SkillRecommender:
    def __init__(self, data_path='job_data.csv'):
        self.jobs = pd.read_csv(data_path)
        self.skills = [col for col in self.jobs.columns if col != 'Job Title']
        self.model = NearestNeighbors(n_neighbors=3, metric='hamming')
        self.model.fit(self.jobs[self.skills])
    
    def recommend(self, user_skills):
        """Recommend jobs based on skill match"""
        try:
            # Convert user skills to binary vector
            input_vector = [[user_skills.get(skill, 0) for skill in self.skills]]
            distances, indices = self.model.kneighbors(input_vector)
            
            # Prepare results
            results = self.jobs.iloc[indices[0]].copy()
            results['Match_Score'] = (1 - distances[0]) * 100
            return results[['Job Title', 'Match_Score']]
        except Exception as e:
            print(f"Recommendation error: {e}")
            return pd.DataFrame(columns=['Job Title', 'Match_Score'])
