"""
Data Processor Module
Handles loading, cleaning, and preprocessing of poll data.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class DataProcessor:
    """
    A class for processing poll/survey data including loading, cleaning, and validation.
    """
    
    def __init__(self):
        self.raw_data = None
        self.cleaned_data = None
        self.data_quality_report = {}
    
    def load_data(self, file_path, file_type='csv'):
        """
        Load data from various file formats.
        
        Args:
            file_path (str): Path to the data file
            file_type (str): Type of file ('csv', 'excel', 'json')
            
        Returns:
            pd.DataFrame: Loaded data
        """
        try:
            if file_type == 'csv':
                self.raw_data = pd.read_csv(file_path)
            elif file_type == 'excel':
                self.raw_data = pd.read_excel(file_path)
            elif file_type == 'json':
                self.raw_data = pd.read_json(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            print(f"Data loaded successfully: {self.raw_data.shape}")
            return self.raw_data
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return None
    
    def validate_data(self, df=None):
        """
        Validate data structure and content.
        
        Args:
            df (pd.DataFrame): DataFrame to validate (default: self.raw_data)
            
        Returns:
            dict: Validation report
        """
        if df is None:
            df = self.raw_data
            
        if df is None:
            return {"error": "No data to validate"}
        
        report = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "missing_values": df.isnull().sum().to_dict(),
            "data_types": df.dtypes.to_dict(),
            "duplicate_rows": df.duplicated().sum(),
            "memory_usage": df.memory_usage(deep=True).sum()
        }
        
        # Check for required columns
        required_columns = ['respondent_id', 'question', 'response']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            report["missing_required_columns"] = missing_columns
        else:
            report["missing_required_columns"] = []
        
        self.data_quality_report = report
        return report
    
    def clean_data(self, df=None):
        """
        Clean and preprocess the data.
        
        Args:
            df (pd.DataFrame): DataFrame to clean (default: self.raw_data)
            
        Returns:
            pd.DataFrame: Cleaned data
        """
        if df is None:
            df = self.raw_data.copy()
        else:
            df = df.copy()
        
        print(f"Starting data cleaning with {len(df)} rows")
        
        # 1. Remove duplicates
        initial_rows = len(df)
        df = df.drop_duplicates()
        duplicates_removed = initial_rows - len(df)
        print(f"Removed {duplicates_removed} duplicate rows")
        
        # 2. Handle missing values
        # For critical columns, drop rows with missing values
        critical_columns = ['respondent_id', 'question', 'response']
        for col in critical_columns:
            if col in df.columns:
                missing_before = df[col].isnull().sum()
                df = df.dropna(subset=[col])
                missing_after = df[col].isnull().sum()
                print(f"Removed {missing_before - missing_after} rows with missing {col}")
        
        # 3. Standardize text columns
        text_columns = ['question', 'response', 'region', 'gender']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.title()
        
        # 4. Convert timestamp to datetime if exists
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df = df.dropna(subset=['timestamp'])  # Remove invalid dates
        
        # 5. Clean numeric columns
        numeric_columns = ['satisfaction_score', 'age']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 6. Create additional features
        if 'timestamp' in df.columns:
            df['date'] = df['timestamp'].dt.date
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.day_name()
        
        # 7. Create response length for text feedback
        if 'feedback' in df.columns:
            df['feedback_length'] = df['feedback'].astype(str).str.len()
        
        print(f"Data cleaning completed. Final shape: {df.shape}")
        self.cleaned_data = df
        return df
    
    def generate_synthetic_data(self, num_responses=1000, save_to_file=True):
        """
        Generate synthetic poll data for testing.
        
        Args:
            num_responses (int): Number of responses to generate
            save_to_file (bool): Whether to save to file
            
        Returns:
            pd.DataFrame: Synthetic data
        """
        np.random.seed(42)  # For reproducibility
        
        # Define poll questions and options
        questions = [
            "What is your preferred programming language?",
            "How satisfied are you with our product?",
            "Which feature do you use most frequently?",
            "Would you recommend our product to others?",
            "What is your age group?"
        ]
        
        options = {
            "What is your preferred programming language?": ["Python", "JavaScript", "Java", "C++", "Go", "Rust"],
            "How satisfied are you with our product?": ["Very Satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very Dissatisfied"],
            "Which feature do you use most frequently?": ["Data Analysis", "Reporting", "Dashboard", "Export", "Integration"],
            "Would you recommend our product to others?": ["Yes", "No", "Maybe"],
            "What is your age group?": ["18-24", "25-34", "35-44", "45-54", "55+"]
        }
        
        regions = ["North", "South", "East", "West", "Central"]
        genders = ["Male", "Female", "Other", "Prefer not to say"]
        
        data = []
        
        for i in range(num_responses):
            # Generate timestamp over the last 30 days
            timestamp = pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(0, 30))
            
            # Select random question
            question = np.random.choice(questions)
            response = np.random.choice(options[question])
            
            # Create demographic data
            region = np.random.choice(regions, p=[0.25, 0.20, 0.20, 0.20, 0.15])
            gender = np.random.choice(genders, p=[0.45, 0.40, 0.10, 0.05])
            age_group = np.random.choice(options["What is your age group?"])
            
            # Generate satisfaction score (1-5)
            satisfaction_score = np.random.randint(1, 6)
            
            # Generate feedback text
            feedback_templates = [
                "Great product, very user-friendly!",
                "Needs improvement in user interface.",
                "Excellent customer support.",
                "Could use more features.",
                "Best tool I've used for data analysis.",
                "Sometimes slow performance.",
                "Love the dashboard design.",
                "More customization options needed."
            ]
            feedback = np.random.choice(feedback_templates) if np.random.random() > 0.3 else ""
            
            data.append({
                'respondent_id': f'RESP_{i+1:04d}',
                'timestamp': timestamp,
                'question': question,
                'response': response,
                'region': region,
                'gender': gender,
                'age_group': age_group,
                'satisfaction_score': satisfaction_score,
                'feedback': feedback
            })
        
        df = pd.DataFrame(data)
        
        if save_to_file:
            df.to_csv('data/synthetic/synthetic_polls.csv', index=False)
            print(f"Synthetic data saved to data/synthetic/synthetic_polls.csv")
        
        self.raw_data = df
        print(f"Generated {len(df)} synthetic poll responses")
        return df
    
    def get_data_summary(self, df=None):
        """
        Get summary statistics of the data.
        
        Args:
            df (pd.DataFrame): DataFrame to summarize (default: self.cleaned_data)
            
        Returns:
            dict: Summary statistics
        """
        if df is None:
            df = self.cleaned_data if self.cleaned_data is not None else self.raw_data
        
        if df is None:
            return {"error": "No data available"}
        
        summary = {
            "shape": df.shape,
            "columns": list(df.columns),
            "numeric_summary": df.describe().to_dict() if len(df.select_dtypes(include=[np.number]).columns) > 0 else {},
            "categorical_summary": {},
            "date_range": {},
            "response_rates": {}
        }
        
        # Categorical columns summary
        cat_columns = df.select_dtypes(include=['object']).columns
        for col in cat_columns:
            if col not in ['respondent_id', 'feedback']:  # Skip ID and long text
                summary["categorical_summary"][col] = df[col].value_counts().to_dict()
        
        # Date range if timestamp exists
        if 'timestamp' in df.columns:
            summary["date_range"] = {
                "start": df['timestamp'].min(),
                "end": df['timestamp'].max(),
                "duration_days": (df['timestamp'].max() - df['timestamp'].min()).days
            }
        
        # Response rates by question
        if 'question' in df.columns:
            summary["response_rates"] = df['question'].value_counts().to_dict()
        
        return summary
