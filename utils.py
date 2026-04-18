"""
Utils Module
Utility functions for the Poll Results Visualizer project.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
import os

def format_number(num):
    """
    Format large numbers with appropriate suffixes.
    
    Args:
        num (int/float): Number to format
        
    Returns:
        str: Formatted number
    """
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    else:
        return str(int(num))

def calculate_percentage(part, whole, decimal_places=2):
    """
    Calculate percentage with proper handling of division by zero.
    
    Args:
        part (int/float): Part value
        whole (int/float): Whole value
        decimal_places (int): Number of decimal places
        
    Returns:
        float: Percentage value
    """
    if whole == 0:
        return 0
    return round((part / whole) * 100, decimal_places)

def get_top_n_items(series, n=5):
    """
    Get top N items from a pandas Series.
    
    Args:
        series (pd.Series): Input series
        n (int): Number of top items to return
        
    Returns:
        pd.Series: Top N items
    """
    return series.value_counts().head(n)

def create_color_palette(n_colors, palette_name='husl'):
    """
    Create a color palette for visualizations.
    
    Args:
        n_colors (int): Number of colors needed
        palette_name (str): Name of the seaborn palette
        
    Returns:
        list: List of color codes
    """
    return sns.color_palette(palette_name, n_colors).as_hex()

def safe_divide(numerator, denominator, default=0):
    """
    Safe division with default value for division by zero.
    
    Args:
        numerator (int/float): Numerator
        denominator (int/float): Denominator
        default (int/float): Default value if denominator is zero
        
    Returns:
        float: Result of division or default
    """
    try:
        return numerator / denominator if denominator != 0 else default
    except (TypeError, ZeroDivisionError):
        return default

def clean_text(text):
    """
    Clean text data by removing extra spaces and converting to proper case.
    
    Args:
        text (str): Input text
        
    Returns:
        str: Cleaned text
    """
    if pd.isna(text) or text == '':
        return ''
    
    return str(text).strip().title()

def validate_date(date_string, date_format='%Y-%m-%d'):
    """
    Validate if a string is a valid date.
    
    Args:
        date_string (str): Date string to validate
        date_format (str): Expected date format
        
    Returns:
        bool: True if valid date, False otherwise
    """
    try:
        datetime.strptime(date_string, date_format)
        return True
    except (ValueError, TypeError):
        return False

def generate_date_range(start_date, end_date, freq='D'):
    """
    Generate a date range between two dates.
    
    Args:
        start_date (str/datetime): Start date
        end_date (str/datetime): End date
        freq (str): Frequency ('D' for daily, 'W' for weekly, etc.)
        
    Returns:
        pd.DatetimeIndex: Date range
    """
    if isinstance(start_date, str):
        start_date = pd.to_datetime(start_date)
    if isinstance(end_date, str):
        end_date = pd.to_datetime(end_date)
    
    return pd.date_range(start=start_date, end=end_date, freq=freq)

def calculate_response_rate(total_responses, total_population):
    """
    Calculate response rate with proper formatting.
    
    Args:
        total_responses (int): Number of responses
        total_population (int): Total population size
        
    Returns:
        str: Formatted response rate
    """
    rate = calculate_percentage(total_responses, total_population)
    return f"{rate}%"

def create_summary_table(df, group_column, value_column, agg_func='count'):
    """
    Create a summary table grouped by a column.
    
    Args:
        df (pd.DataFrame): Input dataframe
        group_column (str): Column to group by
        value_column (str): Column to aggregate
        agg_func (str/func): Aggregation function
        
    Returns:
        pd.DataFrame: Summary table
    """
    if group_column not in df.columns or value_column not in df.columns:
        return pd.DataFrame()
    
    summary = df.groupby(group_column)[value_column].agg(agg_func).reset_index()
    
    if agg_func == 'count':
        summary.columns = [group_column, 'count']
        summary['percentage'] = summary['count'].apply(lambda x: calculate_percentage(x, summary['count'].sum()))
    
    return summary.sort_values('count', ascending=False) if 'count' in summary.columns else summary

def export_to_json(data, file_path):
    """
    Export data to JSON file.
    
    Args:
        data (dict/list): Data to export
        file_path (str): Output file path
    """
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"Data exported to {file_path}")
    except Exception as e:
        print(f"Error exporting to JSON: {e}")

def load_from_json(file_path):
    """
    Load data from JSON file.
    
    Args:
        file_path (str): Input file path
        
    Returns:
        dict/list: Loaded data
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return None

def ensure_directory_exists(directory_path):
    """
    Ensure that a directory exists, create if it doesn't.
    
    Args:
        directory_path (str): Directory path
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Created directory: {directory_path}")

def get_file_size(file_path):
    """
    Get file size in human-readable format.
    
    Args:
        file_path (str): File path
        
    Returns:
        str: Human-readable file size
    """
    if not os.path.exists(file_path):
        return "File not found"
    
    size_bytes = os.path.getsize(file_path)
    
    if size_bytes >= 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    elif size_bytes >= 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes} bytes"

def validate_dataframe(df, required_columns=None):
    """
    Validate DataFrame structure and content.
    
    Args:
        df (pd.DataFrame): DataFrame to validate
        required_columns (list): List of required columns
        
    Returns:
        dict: Validation results
    """
    results = {
        'is_valid': True,
        'errors': [],
        'warnings': [],
        'info': {}
    }
    
    # Check if DataFrame is empty
    if df.empty:
        results['is_valid'] = False
        results['errors'].append("DataFrame is empty")
        return results
    
    # Check required columns
    if required_columns:
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            results['is_valid'] = False
            results['errors'].append(f"Missing required columns: {missing_columns}")
    
    # Check for duplicate columns
    duplicate_columns = df.columns[df.columns.duplicated()].tolist()
    if duplicate_columns:
        results['warnings'].append(f"Duplicate columns found: {duplicate_columns}")
    
    # Check data types
    results['info']['shape'] = df.shape
    results['info']['columns'] = df.columns.tolist()
    results['info']['dtypes'] = df.dtypes.to_dict()
    results['info']['missing_values'] = df.isnull().sum().to_dict()
    
    return results

def format_currency(amount, currency='USD'):
    """
    Format amount as currency.
    
    Args:
        amount (float): Amount to format
        currency (str): Currency code
        
    Returns:
        str: Formatted currency string
    """
    if currency == 'USD':
        return f"${amount:,.2f}"
    elif currency == 'EUR':
        return f"EUR {amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"

def calculate_growth_rate(current_value, previous_value):
    """
    Calculate growth rate between two values.
    
    Args:
        current_value (float): Current value
        previous_value (float): Previous value
        
    Returns:
        float: Growth rate percentage
    """
    if previous_value == 0:
        return 0 if current_value == 0 else float('inf')
    
    return ((current_value - previous_value) / previous_value) * 100

def create_sentiment_score(text):
    """
    Create a simple sentiment score for text (placeholder function).
    
    Args:
        text (str): Input text
        
    Returns:
        float: Sentiment score (-1 to 1)
    """
    if not text or pd.isna(text):
        return 0
    
    # Simple keyword-based sentiment (placeholder)
    positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'best', 'wonderful']
    negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'poor', 'disappointing']
    
    text_lower = text.lower()
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count + negative_count == 0:
        return 0
    
    return (positive_count - negative_count) / (positive_count + negative_count)

def generate_insights_text(analysis_results):
    """
    Generate human-readable insights text from analysis results.
    
    Args:
        analysis_results (dict): Results from PollAnalyzer
        
    Returns:
        str: Formatted insights text
    """
    insights_text = "Key Insights from Poll Analysis\n"
    insights_text += "=" * 40 + "\n\n"
    
    if 'key_insights' in analysis_results:
        for i, insight in enumerate(analysis_results['key_insights'], 1):
            insights_text += f"{i}. {insight}\n"
    
    if 'response_distribution' in analysis_results:
        insights_text += "\nResponse Distribution:\n"
        for question, data in analysis_results['response_distribution'].items():
            insights_text += f"- {question}: {data['most_popular']} leads with {data['response_percentages'][data['most_popular']]}%\n"
    
    return insights_text

def create_performance_metrics(df):
    """
    Create performance metrics for the dashboard.
    
    Args:
        df (pd.DataFrame): Input dataframe
        
    Returns:
        dict: Performance metrics
    """
    metrics = {}
    
    # Response metrics
    metrics['total_responses'] = len(df)
    metrics['unique_respondents'] = df['respondent_id'].nunique() if 'respondent_id' in df.columns else len(df)
    metrics['response_rate'] = calculate_percentage(metrics['total_responses'], metrics['unique_respondents'])
    
    # Time metrics
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        metrics['date_range_days'] = (df['timestamp'].max() - df['timestamp'].min()).days
        metrics['avg_responses_per_day'] = round(metrics['total_responses'] / max(metrics['date_range_days'], 1), 1)
    
    # Satisfaction metrics
    if 'satisfaction_score' in df.columns:
        metrics['avg_satisfaction'] = round(df['satisfaction_score'].mean(), 2)
        metrics['satisfaction_std'] = round(df['satisfaction_score'].std(), 2)
    
    # Diversity metrics
    if 'response' in df.columns:
        metrics['unique_responses'] = df['response'].nunique()
        metrics['response_diversity'] = round(metrics['unique_responses'] / len(df), 3)
    
    return metrics
