import pandas as pd
import os
from pathlib import Path
from sklearn.neighbors import NearestNeighbors

class JobRecommender:
    def __init__(self, data_path=None):
        """
        Initialize the job recommender system.
        If no path is provided, looks for data/job_database.csv
        """
        self.data_path = data_path if data_path else Path(__file__).parent / "data" / "job_database.csv"
        self._validate_data_path()
        self.df = self._load_data()
        self.skill_columns = self._get_skill_columns()
        
    def _validate_data_path(self):
        """Ensure data file exists"""
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Data file not found at: {self.data_path}")
        if not self.data_path.suffix == '.csv':
            raise ValueError("Data file must be a CSV")

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
            raise ValueError(f"Error loading data: {str(e)}")

    def _get_skill_columns(self):
        """Identify skill columns dynamically"""
        return [col for col in self.df.columns 
               if col not in ['Job_Title', 'Job_Type']]

    def recommend(self, job_type, user_skills, n_recommendations=3):
        """
        Get job recommendations for a specific job type
        
        Args:
            job_type: Category of jobs to recommend from
            user_skills: Dict of {skill_name: level} (0-4)
            n_recommendations: Number of jobs to return
            
        Returns:
            DataFrame with recommended jobs and match scores
        """
        try:
            # Filter by job type
            type_filtered = self.df[self.df['Job_Type'] == job_type]
            if len(type_filtered) == 0:
                return pd.DataFrame()
            
            # Prepare model
            model = NearestNeighbors(n_neighbors=n_recommendations, 
                                   metric='hamming')
            model.fit(type_filtered[self.skill_columns])
            
            # Prepare input vector
            input_vector = [[user_skills.get(skill, 0) 
                           for skill in self.skill_columns]]
            
            # Get recommendations
            distances, indices = model.kneighbors(input_vector)
            
            # Format results
            results = type_filtered.iloc[indices[0]].copy()
            results['Match_Score'] = (1 - distances[0]) * 100
            return results
            
        except Exception as e:
            print(f"Recommendation error: {str(e)}")
            return pd.DataFrame()
