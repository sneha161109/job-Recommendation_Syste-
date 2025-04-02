import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Optional

# Define all skill categories at module level for easy importing
TECH_SKILLS = ['Python', 'SQL', 'R', 'Java', 'JavaScript']
DATA_SKILLS = ['DataViz', 'Stats', 'ML', 'DL']
CLOUD_SKILLS = ['Cloud', 'AWS', 'Azure', 'GCP']
BIG_DATA_SKILLS = ['Spark', 'Kafka']
ALL_SKILLS = TECH_SKILLS + DATA_SKILLS + CLOUD_SKILLS + BIG_DATA_SKILLS

class AdvancedJobRecommender:
    def __init__(self, data_path: str = 'job_data.csv'):
        """Initialize the recommender with job data"""
        self.df = self._load_and_preprocess(data_path)
        self.scaler = StandardScaler()
        self.model = None
        self._validate_data()

    def _validate_data(self) -> None:
        """Validate that required columns exist in the data"""
        required_columns = ALL_SKILLS + ['Job Title', 'Experience', 'Remote', 'Industry', 'TechStack']
        missing_cols = [col for col in required_columns if col not in self.df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns in data: {missing_cols}")

    def _load_and_preprocess(self, path: str) -> pd.DataFrame:
        """Load and preprocess the job data"""
        try:
            df = pd.read_csv(path)
            
            # Ensure all skills columns exist and are numeric (0-4)
            for skill in ALL_SKILLS:
                if skill in df.columns:
                    df[skill] = pd.to_numeric(df[skill], errors='coerce').clip(0, 4).fillna(0)
                else:
                    df[skill] = 0  # Add missing skill columns with 0 values
                    
            # Convert experience levels to ordered categories
            df['Experience'] = pd.Categorical(
                df['Experience'],
                categories=['Entry', 'Mid', 'Senior'],
                ordered=True
            )
            
            # Fill other required columns if missing
            for col in ['Remote', 'Industry', 'TechStack']:
                if col not in df.columns:
                    df[col] = '' if col == 'TechStack' else 0
            
            return df
        
        except Exception as e:
            raise ValueError(f"Error loading data: {str(e)}")

    def _calculate_skill_match(self, user_skills: Dict[str, int], job_requirements: pd.Series) -> float:
        """Calculate weighted match score between user skills and job requirements"""
        total_possible = 0.0
        matched = 0.0
        
        for skill in ALL_SKILLS:
            required_level = job_requirements[skill]
            user_level = user_skills.get(skill, 0)
            
            # Higher requirements get more weight
            weight = required_level + 1  # Add 1 to avoid zero-weight skills
            total_possible += weight
            
            if user_level >= required_level:
                matched += weight
        
        return (matched / total_possible) * 100 if total_possible > 0 else 0

    def recommend_jobs(
        self,
        user_skills: Dict[str, int],
        filters: Dict[str, any]
    ) -> pd.DataFrame:
        """
        Generate job recommendations based on skills and filters
        
        Args:
            user_skills: Dictionary of {skill: proficiency_level (0-4)}
            filters: Dictionary containing:
                - experience: 'Entry', 'Mid', 'Senior', or 'All'
                - remote_only: bool
                - n_recommendations: int
                - industry: Optional[str]
        
        Returns:
            DataFrame of recommended jobs with match metrics
        """
        # Validate user skills input
        if not isinstance(user_skills, dict):
            raise ValueError("user_skills must be a dictionary")
            
        for skill, level in user_skills.items():
            if skill not in ALL_SKILLS:
                raise ValueError(f"Unknown skill: {skill}")
            if not 0 <= level <= 4:
                raise ValueError(f"Skill level for {skill} must be 0-4")

        # Prepare user input vector (normalized 0-1)
        user_vector = np.array([user_skills.get(skill, 0)/4 for skill in ALL_SKILLS])
        
        # Filter jobs based on preferences
        filtered_df = self.df.copy()
        
        if filters.get('experience', 'All') != 'All':
            filtered_df = filtered_df[filtered_df['Experience'] == filters['experience']]
        
        if filters.get('remote_only', False):
            filtered_df = filtered_df[filtered_df['Remote'] == 1]
            
        if filters.get('industry'):
            filtered_df = filtered_df[filtered_df['Industry'] == filters['industry']]
        
        if len(filtered_df) == 0:
            return pd.DataFrame()  # Return empty if no matches
        
        # Scale features
        job_vectors = self.scaler.fit_transform(filtered_df[ALL_SKILLS])
        user_vector_scaled = self.scaler.transform([user_vector])
        
        # Find matches using cosine similarity (better for skill profiles)
        model = NearestNeighbors(
            n_neighbors=min(filters.get('n_recommendations', 5), len(filtered_df)),
            metric='cosine',
            algorithm='brute'
        )
        model.fit(job_vectors)
        
        distances, indices = model.kneighbors(user_vector_scaled)
        
        # Prepare results with multiple match metrics
        results = filtered_df.iloc[indices[0]].copy()
        results['Match_Score'] = 100 * (1 - distances[0])  # Convert cosine distance to percentage
        
        # Calculate additional metrics
        results['Skill_Coverage'] = results.apply(
            lambda row: self._calculate_skill_match(user_skills, row[ALL_SKILLS]),
            axis=1
        )
        
        # Add skill gap analysis
        results['Missing_Skills'] = results.apply(
            lambda row: [
                skill for skill in ALL_SKILLS 
                if row[skill] > 0 and user_skills.get(skill, 0) < row[skill]
            ],
            axis=1
        )
        
        # Sort by best matches and return
        return results.sort_values('Match_Score', ascending=False)

    def get_skill_distribution(self, jobs_df: pd.DataFrame) -> pd.Series:
        """Analyze skill distribution in job listings"""
        if not isinstance(jobs_df, pd.DataFrame):
            raise ValueError("Input must be a DataFrame")
        return jobs_df[ALL_SKILLS].mean().sort_values(ascending=False)

    def get_industry_distribution(self, jobs_df: pd.DataFrame) -> pd.Series:
        """Analyze industry distribution in job listings"""
        if not isinstance(jobs_df, pd.DataFrame):
            raise ValueError("Input must be a DataFrame")
        return jobs_df['Industry'].value_counts()
