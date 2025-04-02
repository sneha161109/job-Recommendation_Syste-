import pandas as pd
from sklearn.neighbors import NearestNeighbors
import os

def load_data():
    """Load the job data"""
    if not os.path.exists('job_data.csv'):
        print("Error: Job data file not found!")
        return None, None
    
    try:
        data = pd.read_csv('job_data.csv')
        required_columns = ['Python', 'SQL', 'Data Analysis', 'Machine Learning', 'Cloud Computing', 'Job Title']
        if not all(col in data.columns for col in required_columns):
            print("Error: Required columns missing in the dataset!")
            return None, None
        return data[required_columns[:-1]], data['Job Title']
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return None, None

def train_model(X):
    """Train the recommendation model"""
    model = NearestNeighbors(n_neighbors=5, metric='hamming')
    model.fit(X)
    return model

def get_user_input():
    """Get and validate user input"""
    print("\nPlease rate your skills (1 = Yes, 0 = No):")
    skills = {}
    
    questions = {
        'Python': "Do you know Python? ",
        'SQL': "Do you know SQL? ",
        'Data Analysis': "Do you know Data Analysis? ",
        'Machine Learning': "Do you know Machine Learning? ",
        'Cloud Computing': "Do you know Cloud Computing? "
    }
    
    for skill, question in questions.items():
        while True:
            try:
                val = int(input(question))
                if val not in [0, 1]:
                    raise ValueError
                skills[skill] = val
                break
            except ValueError:
                print("Invalid input! Please enter 1 (Yes) or 0 (No).")
    
    return [[skills['Python'], skills['SQL'], skills['Data Analysis'], 
            skills['Machine Learning'], skills['Cloud Computing']]]

def main():
    print("\n" + "="*50)
    print("JOB RECOMMENDATION SYSTEM".center(50))
    print("="*50)
    
    X, y = load_data()
    if X is None or y is None:
        return
    
    model = train_model(X)
    user_input = get_user_input()
    
    try:
        distances, indices = model.kneighbors(user_input)
        print("\nRecommended Jobs:")
        for i, job in enumerate(y.iloc[indices[0]].tolist(), 1):
            print(f"{i}. {job}")
        
        print("\nMatching Job Details:")
        matched_data = pd.concat([y.iloc[indices[0]], X.iloc[indices[0]]], axis=1)
        print(matched_data.to_string(index=False))
        
    except Exception as e:
        print(f"\nError generating recommendations: {str(e)}")

if __name__ == "__main__":
    main()
