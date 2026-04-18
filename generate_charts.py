"""
Simple Chart Generation Script
Creates basic charts for the Poll Results Visualizer project
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from wordcloud import WordCloud
import os

# Set style
plt.style.use('default')
sns.set_palette("husl")

def generate_sample_charts():
    """Generate sample charts for demonstration"""
    
    # Ensure output directory exists
    os.makedirs('outputs/charts', exist_ok=True)
    
    # Load synthetic data
    try:
        data = pd.read_csv('data/synthetic/synthetic_polls.csv')
        print(f"Loaded data with {len(data)} rows")
    except FileNotFoundError:
        print("No synthetic data found, generating sample data...")
        data = generate_sample_data()
    
    # 1. Response Distribution Bar Chart
    plt.figure(figsize=(10, 6))
    response_counts = data['response'].value_counts()
    bars = plt.bar(response_counts.index, response_counts.values, 
                   color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'])
    plt.title('Response Distribution', fontsize=16, fontweight='bold')
    plt.xlabel('Response Options', fontsize=12)
    plt.ylabel('Number of Responses', fontsize=12)
    plt.xticks(rotation=45)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('outputs/charts/response_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Satisfaction Score Histogram
    plt.figure(figsize=(10, 6))
    plt.hist(data['satisfaction_score'], bins=5, alpha=0.7, 
             color='#FF6B6B', edgecolor='black')
    plt.title('Satisfaction Score Distribution', fontsize=16, fontweight='bold')
    plt.xlabel('Satisfaction Score', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('outputs/charts/satisfaction_histogram.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. Regional Distribution
    plt.figure(figsize=(10, 6))
    region_counts = data['region'].value_counts()
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
    bars = plt.bar(region_counts.index, region_counts.values, color=colors[:len(region_counts)])
    plt.title('Regional Distribution', fontsize=16, fontweight='bold')
    plt.xlabel('Region', fontsize=12)
    plt.ylabel('Number of Responses', fontsize=12)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('outputs/charts/region_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 4. Gender Distribution Pie Chart
    plt.figure(figsize=(8, 8))
    gender_counts = data['gender'].value_counts()
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    plt.pie(gender_counts.values, labels=gender_counts.index, autopct='%1.1f%%',
            colors=colors[:len(gender_counts)], startangle=90)
    plt.title('Gender Distribution', fontsize=16, fontweight='bold')
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig('outputs/charts/gender_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 5. Age Group Distribution
    plt.figure(figsize=(10, 6))
    age_counts = data['age_group'].value_counts()
    bars = plt.bar(age_counts.index, age_counts.values, 
                   color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'])
    plt.title('Age Group Distribution', fontsize=16, fontweight='bold')
    plt.xlabel('Age Group', fontsize=12)
    plt.ylabel('Number of Responses', fontsize=12)
    plt.xticks(rotation=45)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('outputs/charts/age_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 6. Word Cloud from Feedback
    plt.figure(figsize=(12, 8))
    feedback_text = ' '.join(data['feedback'].dropna().astype(str))
    if feedback_text.strip():
        wordcloud = WordCloud(width=800, height=400, background_color='white',
                              colormap='viridis').generate(feedback_text)
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('Feedback Word Cloud', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig('outputs/charts/feedback_wordcloud.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 7. Daily Response Trends
    plt.figure(figsize=(12, 6))
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    data['date'] = data['timestamp'].dt.date
    daily_counts = data.groupby('date').size()
    
    plt.plot(daily_counts.index, daily_counts.values, 
             marker='o', linewidth=2, markersize=6, color='#FF6B6B')
    plt.title('Daily Response Trends', fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Number of Responses', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('outputs/charts/daily_trends.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 8. Regional Response Patterns (Stacked Bar)
    plt.figure(figsize=(12, 8))
    regional_responses = pd.crosstab(data['region'], data['response'])
    regional_responses.plot(kind='bar', stacked=True, figsize=(12, 8),
                           color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'])
    plt.title('Regional Response Patterns', fontsize=16, fontweight='bold')
    plt.xlabel('Region', fontsize=12)
    plt.ylabel('Number of Responses', fontsize=12)
    plt.xticks(rotation=45)
    plt.legend(title='Response', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig('outputs/charts/regional_responses.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("All charts generated successfully!")
    print("Charts saved to: outputs/charts/")
    
    # List generated files
    chart_files = os.listdir('outputs/charts')
    print(f"Generated {len(chart_files)} chart files:")
    for file in sorted(chart_files):
        print(f"  - {file}")

def generate_sample_data():
    """Generate sample poll data if none exists"""
    np.random.seed(42)
    
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
    for i in range(500):
        timestamp = pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(0, 30))
        question = np.random.choice(questions)
        response = np.random.choice(options[question])
        region = np.random.choice(regions)
        gender = np.random.choice(genders)
        age_group = np.random.choice(options["What is your age group?"])
        satisfaction_score = np.random.randint(1, 6)
        
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
    df.to_csv('data/synthetic/synthetic_polls.csv', index=False)
    return df

if __name__ == "__main__":
    generate_sample_charts()
