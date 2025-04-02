import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler

class JobRecommender:
    def __init__(self, data_path='job_data.csv'):
        self.df = pd.read_csv(data_path)
        self.skills = ['Python','SQL','R','Java','JavaScript','DataViz',
                      'Stats','ML','DL','Cloud','AWS','Azure','GCP','Spark','Kafka']
        self.scaler = MinMaxScaler()
        self._prepare_model()
    
    def _prepare_model(self):
        """Prepare KNN model with normalized data"""
        X = self.df[self.skills]
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)
        self.model = NearestNeighbors(n_neighbors=5, metric='cosine')
        self.model.fit(X_scaled)
    
    def recommend(self, user_skills, filters):
        """Get recommendations with filters"""
        # Prepare user input
        user_input = np.array([[user_skills.get(skill, 0) for skill in self.skills]])
        user_scaled = self.scaler.transform(user_input)
        
        # Find nearest neighbors
        distances, indices = self.model.kneighbors(user_scaled)
        
        # Get recommendations
        recs = self.df.iloc[indices[0]].copy()
        recs['Match_Score'] = 100 * (1 - distances[0])
        
        # Apply filters
        if filters['experience'] != 'All':
            recs = recs[recs['Experience'] == filters['experience']]
        if filters['remote']:
            recs = recs[recs['Remote'] == 1]
        if filters['industry'] != 'All':
            recs = recs[recs['Industry'] == filters['industry']]
            
        return recs.sort_values('Match_Score', ascending=False)
