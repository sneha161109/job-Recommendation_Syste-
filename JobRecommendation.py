import pandas as pd
import os
from pathlib import Path
from sklearn.neighbors import NearestNeighbors

class JobRecommender:
    def __init__(self, data_path='job_data.csv'):
        """
        Initialize with data/job_data.csv in the same directory
        """
        self.data_path = Path(__file__).parent / data_path
        self._validate_data_path()
        self.df = self._load_data()
        self.skill_columns = self._get_skill_columns()
        
    def _validate_data_path(self):
        """Ensure data file exists in the same directory"""
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"job_data.csv not found in: {self.data_path.parent}")

    def _load_data(self):
        """Load and validate the dataset"""
        try:
            df = pd.read_csv(self.data_path)
            required_cols = {'Job_Title', 'Job_Type'}
            if not required_cols.issubset(df.columns):
                missing = required_cols - set(df.columns)
                raise ValueError(f"Missing required columns: {missing}")
            return df
        except Exception as e:
            raise ValueError(f"Error loading job_data.csv: {str(e)}")

    def _get_skill_columns(self):
        """Dynamically identify skill columns"""
        return [col for col in self.df.columns 
               if col not in ['Job_Title', 'Job_Type']]

    def recommend(self, job_type, user_skills, n_recommendations=3):
        """Recommend jobs based on skills"""
        try:
            type_filtered = self.df[self.df['Job_Type'] == job_type]
            if len(type_filtered) == 0:
                return pd.DataFrame()
            
            model = NearestNeighbors(n_neighbors=n_recommendations, metric='hamming')
            model.fit(type_filtered[self.skill_columns])
            
            input_vector = [[user_skills.get(skill, 0) for skill in self.skill_columns]]
            distances, indices = model.kneighbors(input_vector)
            
            results = type_filtered.iloc[indices[0]].copy()
            results['Match_Score'] = (1 - distances[0]) * 100
            return results
            
        except Exception as e:
            print(f"Recommendation error: {str(e)}")
            return pd.DataFrame()
