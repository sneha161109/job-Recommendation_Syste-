import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

class AdvancedJobRecommender:
    def __init__(self, data_path='job_data.csv'):
        self.df = self._load_and_preprocess(data_path)
        self.scaler = StandardScaler()
        self.model = None
    
    def _load_and_preprocess(self, path):
        df = pd.read_csv(path)
        
        # Convert binary skills to weighted values
        skill_weights = {
            'Python': [0.2, 0.5, 0.8, 1.0],  # [Basic, Intermediate, Advanced, Expert]
            'SQL': [0.3, 0.6, 0.9, 1.0],
            # ... define weights for all 15 skills
        }
        
        for skill in ALL_SKILLS:
            if skill in skill_weights:
                df[skill] = df[skill].apply(lambda x: skill_weights[skill][3] if x == 1 else 0)
        
        return df
    
    def recommend_jobs(self, user_skills, filters):
        """Advanced recommendation with skill weights"""
        # Prepare user input vector
        user_vector = np.array([user_skills.get(skill, 0) for skill in ALL_SKILLS])
        
        # Filter jobs
        filtered_df = self.df.copy()
        if filters['experience'] != 'All':
            filtered_df = filtered_df[filtered_df['Experience'] == filters['experience']]
        if filters['remote_only']:
            filtered_df = filtered_df[filtered_df['Remote'] == 1]
        
        # Scale features
        job_vectors = self.scaler.fit_transform(filtered_df[ALL_SKILLS])
        user_vector_scaled = self.scaler.transform([user_vector])
        
        # Hybrid similarity metric
        def hybrid_metric(x, y):
            cosine_sim = np.dot(x, y) / (np.linalg.norm(x) * np.linalg.norm(y))
            euclidean_dist = np.linalg.norm(x - y)
            return 0.7 * cosine_sim + 0.3 * (1 / (1 + euclidean_dist))
        
        # Find matches
        model = NearestNeighbors(
            n_neighbors=filters['n_recommendations'],
            metric=hybrid_metric,
            algorithm='brute'
        )
        model.fit(job_vectors)
        
        distances, indices = model.kneighbors(user_vector_scaled)
        matches = filtered_df.iloc[indices[0]]
        
        # Calculate match quality metrics
        matches['Match_Score'] = 100 * (1 - distances[0])
        matches['Skill_Coverage'] = matches[ALL_SKILLS].apply(
            lambda row: sum((user_vector > 0) & (row > 0)) / sum(row > 0), axis=1
        )
        
        return matches.sort_values('Match_Score', ascending=False)
