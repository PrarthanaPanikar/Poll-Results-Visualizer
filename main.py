"""
Main Application Entry Point
Poll Results Visualizer - Complete data analysis pipeline
"""

import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data_processor import DataProcessor
from analyzer import PollAnalyzer
from visualizer import PollVisualizer
from utils import ensure_directory_exists, export_to_json

def main():
    """
    Main function to run the complete poll analysis pipeline.
    """
    print("=== Poll Results Visualizer ===")
    print("Starting data analysis pipeline...")
    
    # Initialize components
    processor = DataProcessor()
    analyzer = PollAnalyzer()
    visualizer = PollVisualizer()
    
    # Create necessary directories
    ensure_directory_exists('data/raw')
    ensure_directory_exists('data/processed')
    ensure_directory_exists('data/synthetic')
    ensure_directory_exists('outputs/charts')
    ensure_directory_exists('outputs/reports')
    ensure_directory_exists('images')
    
    # Step 1: Generate or load data
    print("\n1. Loading data...")
    
    # Check if we have existing data, otherwise generate synthetic data
    data_file = 'data/synthetic/synthetic_polls.csv'
    if os.path.exists(data_file):
        print("Loading existing synthetic data...")
        data = processor.load_data(data_file)
    else:
        print("Generating new synthetic data...")
        data = processor.generate_synthetic_data(num_responses=1000)
    
    if data is None:
        print("Error: Could not load data")
        return
    
    # Step 2: Clean and validate data
    print("\n2. Cleaning and validating data...")
    cleaned_data = processor.clean_data(data)
    
    # Validate data quality
    validation_report = processor.validate_data(cleaned_data)
    print(f"Data validation: {validation_report['total_rows']} rows, {validation_report['total_columns']} columns")
    
    # Step 3: Analyze data
    print("\n3. Performing analysis...")
    analysis_results = analyzer.analyze_responses(cleaned_data)
    
    # Get summary statistics
    summary_stats = analyzer.get_summary_statistics()
    print(f"Analysis complete: {summary_stats['total_respondents']} respondents, {summary_stats['total_questions']} questions")
    
    # Step 4: Create visualizations
    print("\n4. Creating visualizations...")
    visualizer.set_data(cleaned_data)
    
    # Create various charts
    charts_created = []
    
    # Response distribution
    if 'response' in cleaned_data.columns:
        fig = visualizer.create_bar_chart('response', title='Response Distribution', save_path='outputs/charts/response_distribution.png')
        charts_created.append('response_distribution')
        
        fig = visualizer.create_pie_chart('response', title='Response Percentages', save_path='outputs/charts/response_percentages.png')
        charts_created.append('response_percentages')
    
    # Satisfaction analysis
    if 'satisfaction_score' in cleaned_data.columns:
        fig = visualizer.create_histogram('satisfaction_score', title='Satisfaction Score Distribution', save_path='outputs/charts/satisfaction_histogram.png')
        charts_created.append('satisfaction_histogram')
    
    # Demographic charts
    if 'region' in cleaned_data.columns:
        fig = visualizer.create_bar_chart('region', title='Regional Distribution', save_path='outputs/charts/region_distribution.png')
        charts_created.append('region_distribution')
    
    if 'gender' in cleaned_data.columns:
        fig = visualizer.create_pie_chart('gender', title='Gender Distribution', save_path='outputs/charts/gender_distribution.png')
        charts_created.append('gender_distribution')
    
    if 'age_group' in cleaned_data.columns:
        fig = visualizer.create_bar_chart('age_group', title='Age Group Distribution', save_path='outputs/charts/age_distribution.png')
        charts_created.append('age_distribution')
    
    # Temporal analysis
    if 'timestamp' in cleaned_data.columns:
        cleaned_data['date'] = pd.to_datetime(cleaned_data['timestamp']).dt.date
        daily_counts = cleaned_data.groupby('date').size().reset_index()
        daily_counts.columns = ['date', 'count']
        
        fig = visualizer.create_line_chart('date', 'count', title='Daily Response Trends', save_path='outputs/charts/daily_trends.png')
        charts_created.append('daily_trends')
    
    # Feedback analysis
    if 'feedback' in cleaned_data.columns:
        fig = visualizer.create_word_cloud('feedback', title='Feedback Word Cloud', save_path='outputs/charts/feedback_wordcloud.png')
        charts_created.append('feedback_wordcloud')
    
    # Cross-tabulation
    if 'region' in cleaned_data.columns and 'response' in cleaned_data.columns:
        fig = visualizer.create_stacked_bar_chart('region', 'response', title='Regional Response Patterns', save_path='outputs/charts/regional_responses.png')
        charts_created.append('regional_responses')
    
    # Dashboard layout
    fig = visualizer.create_dashboard_layout(save_path='outputs/charts/dashboard.html')
    charts_created.append('dashboard')
    
    print(f"Created {len(charts_created)} visualizations")
    
    # Step 5: Export results
    print("\n5. Exporting results...")
    
    # Save cleaned data
    cleaned_data.to_csv('data/processed/cleaned_poll_data.csv', index=False)
    print("Cleaned data saved to data/processed/cleaned_poll_data.csv")
    
    # Save analysis results
    export_to_json(analysis_results, 'outputs/reports/analysis_results.json')
    print("Analysis results saved to outputs/reports/analysis_results.json")
    
    # Save summary statistics
    export_to_json(summary_stats, 'outputs/reports/summary_statistics.json')
    print("Summary statistics saved to outputs/reports/summary_statistics.json")
    
    # Generate insights report
    insights_text = generate_insights_report(analysis_results, summary_stats)
    with open('outputs/reports/insights_report.txt', 'w') as f:
        f.write(insights_text)
    print("Insights report saved to outputs/reports/insights_report.txt")
    
    # Step 6: Display summary
    print("\n=== ANALYSIS COMPLETE ===")
    print(f"Total respondents: {summary_stats['total_respondents']}")
    print(f"Total responses: {summary_stats['total_responses']}")
    print(f"Date range: {summary_stats['date_range'].get('start', 'N/A')} to {summary_stats['date_range'].get('end', 'N/A')}")
    print(f"Average satisfaction: {summary_stats['average_satisfaction']}/5.0")
    print(f"Charts created: {len(charts_created)}")
    print(f"Output files saved to: outputs/")
    
    print("\nNext steps:")
    print("1. Run 'streamlit run app.py' to launch the interactive dashboard")
    print("2. Check outputs/charts/ for generated visualizations")
    print("3. Review outputs/reports/ for analysis results")
    
    return analysis_results, summary_stats

def generate_insights_report(analysis_results, summary_stats):
    """
    Generate a comprehensive insights report.
    
    Args:
        analysis_results (dict): Results from analysis
        summary_stats (dict): Summary statistics
        
    Returns:
        str: Formatted report text
    """
    report = []
    report.append("POLL RESULTS ANALYSIS REPORT")
    report.append("=" * 50)
    report.append(f"Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Executive Summary
    report.append("EXECUTIVE SUMMARY")
    report.append("-" * 20)
    report.append(f"Total Respondents: {summary_stats['total_respondents']}")
    report.append(f"Total Responses: {summary_stats['total_responses']}")
    report.append(f"Average Satisfaction: {summary_stats['average_satisfaction']}/5.0")
    
    if 'date_range' in summary_stats and summary_stats['date_range']:
        report.append(f"Analysis Period: {summary_stats['date_range']['start']} to {summary_stats['date_range']['end']}")
    
    report.append("")
    
    # Key Insights
    if 'key_insights' in analysis_results:
        report.append("KEY INSIGHTS")
        report.append("-" * 15)
        for i, insight in enumerate(analysis_results['key_insights'], 1):
            report.append(f"{i}. {insight}")
        report.append("")
    
    # Response Analysis
    if 'response_distribution' in analysis_results:
        report.append("RESPONSE ANALYSIS")
        report.append("-" * 18)
        for question, data in analysis_results['response_distribution'].items():
            report.append(f"Question: {question}")
            report.append(f"  - Total responses: {data['total_responses']}")
            report.append(f"  - Most popular: {data['most_popular']} ({data['response_percentages'][data['most_popular']]}%)")
            report.append(f"  - Least popular: {data['least_popular']} ({data['response_percentages'][data['least_popular']]}%)")
            report.append("")
    
    # Demographic Analysis
    if 'demographic_analysis' in analysis_results:
        report.append("DEMOGRAPHIC ANALYSIS")
        report.append("-" * 20)
        
        demo_data = analysis_results['demographic_analysis']
        
        if 'region' in demo_data:
            report.append("Regional Distribution:")
            for region, count in demo_data['region']['distribution'].items():
                report.append(f"  - {region}: {count} responses")
            report.append("")
        
        if 'gender' in demo_data:
            report.append("Gender Distribution:")
            for gender, count in demo_data['gender']['distribution'].items():
                report.append(f"  - {gender}: {count} responses")
            report.append("")
        
        if 'age_group' in demo_data:
            report.append("Age Group Distribution:")
            for age, count in demo_data['age_group']['distribution'].items():
                report.append(f"  - {age}: {count} responses")
            report.append("")
    
    # Satisfaction Analysis
    if 'satisfaction_analysis' in analysis_results:
        report.append("SATISFACTION ANALYSIS")
        report.append("-" * 22)
        
        sat_data = analysis_results['satisfaction_analysis']
        if 'statistics' in sat_data:
            stats = sat_data['statistics']
            report.append(f"Average Satisfaction: {stats['mean']:.2f}/5.0")
            report.append(f"Median Satisfaction: {stats['median']}")
            report.append(f"Standard Deviation: {stats['std']:.2f}")
            report.append(f"Range: {stats['min']} - {stats['max']}")
            report.append("")
    
    # Recommendations
    report.append("RECOMMENDATIONS")
    report.append("-" * 16)
    
    if summary_stats['average_satisfaction'] >= 4:
        report.append("1. High satisfaction levels indicate strong performance")
        report.append("2. Consider expanding successful features")
        report.append("3. Use positive feedback in marketing materials")
    elif summary_stats['average_satisfaction'] <= 2:
        report.append("1. Low satisfaction requires immediate attention")
        report.append("2. Conduct follow-up surveys to identify specific issues")
        report.append("3. Implement improvement action plan")
    else:
        report.append("1. Moderate satisfaction levels offer room for improvement")
        report.append("2. Focus on addressing specific pain points")
        report.append("3. Monitor satisfaction trends over time")
    
    report.append("")
    
    # Next Steps
    report.append("NEXT STEPS")
    report.append("-" * 12)
    report.append("1. Review interactive dashboard for detailed exploration")
    report.append("2. Share findings with stakeholders")
    report.append("3. Plan follow-up surveys based on insights")
    report.append("4. Implement data-driven improvements")
    report.append("")
    
    report.append("END OF REPORT")
    
    return "\n".join(report)

if __name__ == "__main__":
    try:
        results, stats = main()
        print("\nAnalysis completed successfully!")
    except Exception as e:
        print(f"\nError during analysis: {e}")
        print("Please check the error and try again.")
        sys.exit(1)
