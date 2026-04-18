"""
Analyzer Module
Handles statistical analysis and insights generation for poll data.
"""

import pandas as pd
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class PollAnalyzer:
    """
    A class for analyzing poll data and generating insights.
    """
    
    def __init__(self):
        self.data = None
        self.analysis_results = {}
    
    def analyze_responses(self, df):
        """
        Perform comprehensive analysis of poll responses.
        
        Args:
            df (pd.DataFrame): Cleaned poll data
            
        Returns:
            dict: Analysis results
        """
        self.data = df.copy()
        results = {}
        
        # 1. Response distribution analysis
        results['response_distribution'] = self._analyze_response_distribution()
        
        # 2. Demographic analysis
        results['demographic_analysis'] = self._analyze_demographics()
        
        # 3. Satisfaction analysis
        results['satisfaction_analysis'] = self._analyze_satisfaction()
        
        # 4. Temporal analysis
        results['temporal_analysis'] = self._analyze_temporal_patterns()
        
        # 5. Cross-tabulation analysis
        results['cross_tabulation'] = self._analyze_cross_tabulations()
        
        # 6. Statistical significance tests
        results['statistical_tests'] = self._perform_statistical_tests()
        
        # 7. Key insights
        results['key_insights'] = self._generate_key_insights()
        
        self.analysis_results = results
        return results
    
    def _analyze_response_distribution(self):
        """
        Analyze the distribution of responses for each question.
        
        Returns:
            dict: Response distribution analysis
        """
        if self.data is None or 'question' not in self.data.columns:
            return {}
        
        distribution = {}
        
        for question in self.data['question'].unique():
            question_data = self.data[self.data['question'] == question]
            response_counts = question_data['response'].value_counts()
            response_percentages = (response_counts / len(question_data) * 100).round(2)
            
            distribution[question] = {
                'total_responses': len(question_data),
                'response_counts': response_counts.to_dict(),
                'response_percentages': response_percentages.to_dict(),
                'most_popular': response_counts.index[0] if len(response_counts) > 0 else None,
                'least_popular': response_counts.index[-1] if len(response_counts) > 0 else None,
                'diversity_score': len(response_counts) / len(question_data)  # Response diversity
            }
        
        return distribution
    
    def _analyze_demographics(self):
        """
        Analyze demographic patterns in responses.
        
        Returns:
            dict: Demographic analysis
        """
        if self.data is None:
            return {}
        
        demographics = {}
        
        # Region analysis
        if 'region' in self.data.columns:
            demographics['region'] = {
                'distribution': self.data['region'].value_counts().to_dict(),
                'response_by_region': {}
            }
            
            for question in self.data['question'].unique():
                question_data = self.data[self.data['question'] == question]
                region_responses = question_data.groupby('region')['response'].apply(list).to_dict()
                demographics['region']['response_by_region'][question] = region_responses
        
        # Gender analysis
        if 'gender' in self.data.columns:
            demographics['gender'] = {
                'distribution': self.data['gender'].value_counts().to_dict(),
                'response_by_gender': {}
            }
            
            for question in self.data['question'].unique():
                question_data = self.data[self.data['question'] == question]
                gender_responses = question_data.groupby('gender')['response'].apply(list).to_dict()
                demographics['gender']['response_by_gender'][question] = gender_responses
        
        # Age group analysis
        if 'age_group' in self.data.columns:
            demographics['age_group'] = {
                'distribution': self.data['age_group'].value_counts().to_dict(),
                'response_by_age': {}
            }
            
            for question in self.data['question'].unique():
                question_data = self.data[self.data['question'] == question]
                age_responses = question_data.groupby('age_group')['response'].apply(list).to_dict()
                demographics['age_group']['response_by_age'][question] = age_responses
        
        return demographics
    
    def _analyze_satisfaction(self):
        """
        Analyze satisfaction scores and correlations.
        
        Returns:
            dict: Satisfaction analysis
        """
        if self.data is None or 'satisfaction_score' not in self.data.columns:
            return {}
        
        satisfaction = {}
        
        # Basic statistics
        satisfaction['statistics'] = {
            'mean': self.data['satisfaction_score'].mean(),
            'median': self.data['satisfaction_score'].median(),
            'mode': self.data['satisfaction_score'].mode().iloc[0] if not self.data['satisfaction_score'].mode().empty else None,
            'std': self.data['satisfaction_score'].std(),
            'min': self.data['satisfaction_score'].min(),
            'max': self.data['satisfaction_score'].max()
        }
        
        # Distribution
        satisfaction['distribution'] = self.data['satisfaction_score'].value_counts().sort_index().to_dict()
        
        # Satisfaction by demographics
        satisfaction['by_demographics'] = {}
        
        for demo_col in ['region', 'gender', 'age_group']:
            if demo_col in self.data.columns:
                demo_satisfaction = self.data.groupby(demo_col)['satisfaction_score'].agg(['mean', 'count']).round(2)
                satisfaction['by_demographics'][demo_col] = demo_satisfaction.to_dict()
        
        # Satisfaction correlation with responses
        if 'question' in self.data.columns:
            satisfaction['by_question'] = {}
            for question in self.data['question'].unique():
                question_data = self.data[self.data['question'] == question]
                if len(question_data) > 1:
                    # Convert responses to numeric if possible
                    response_satisfaction = question_data.groupby('response')['satisfaction_score'].mean().round(2)
                    satisfaction['by_question'][question] = response_satisfaction.to_dict()
        
        return satisfaction
    
    def _analyze_temporal_patterns(self):
        """
        Analyze temporal patterns in responses.
        
        Returns:
            dict: Temporal analysis
        """
        if self.data is None or 'timestamp' not in self.data.columns:
            return {}
        
        temporal = {}
        
        # Convert timestamp to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(self.data['timestamp']):
            self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])
        
        # Response patterns over time
        self.data['date'] = self.data['timestamp'].dt.date
        self.data['hour'] = self.data['timestamp'].dt.hour
        self.data['day_of_week'] = self.data['timestamp'].dt.day_name()
        
        # Daily response counts
        temporal['daily_responses'] = self.data.groupby('date').size().to_dict()
        
        # Hourly response patterns
        temporal['hourly_responses'] = self.data.groupby('hour').size().to_dict()
        
        # Day of week patterns
        temporal['day_of_week_responses'] = self.data.groupby('day_of_week').size().to_dict()
        
        # Satisfaction over time
        if 'satisfaction_score' in self.data.columns:
            temporal['satisfaction_over_time'] = self.data.groupby('date')['satisfaction_score'].mean().round(2).to_dict()
        
        return temporal
    
    def _analyze_cross_tabulations(self):
        """
        Perform cross-tabulation analysis between variables.
        
        Returns:
            dict: Cross-tabulation results
        """
        if self.data is None:
            return {}
        
        cross_tabs = {}
        
        # Question vs Region
        if 'question' in self.data.columns and 'region' in self.data.columns:
            cross_tabs['question_region'] = pd.crosstab(
                self.data['question'], 
                self.data['region'], 
                margins=True
            ).to_dict()
        
        # Question vs Gender
        if 'question' in self.data.columns and 'gender' in self.data.columns:
            cross_tabs['question_gender'] = pd.crosstab(
                self.data['question'], 
                self.data['gender'], 
                margins=True
            ).to_dict()
        
        # Satisfaction vs Demographics
        if 'satisfaction_score' in self.data.columns:
            for demo_col in ['region', 'gender', 'age_group']:
                if demo_col in self.data.columns:
                    cross_tabs[f'satisfaction_{demo_col}'] = pd.crosstab(
                        self.data['satisfaction_score'], 
                        self.data[demo_col], 
                        margins=True
                    ).to_dict()
        
        return cross_tabs
    
    def _perform_statistical_tests(self):
        """
        Perform statistical significance tests.
        
        Returns:
            dict: Statistical test results
        """
        if self.data is None:
            return {}
        
        tests = {}
        
        # Chi-square test for independence between categorical variables
        if 'question' in self.data.columns and 'region' in self.data.columns:
            contingency_table = pd.crosstab(self.data['question'], self.data['region'])
            chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
            
            tests['question_region_independence'] = {
                'chi2_statistic': chi2,
                'p_value': p_value,
                'degrees_of_freedom': dof,
                'is_significant': p_value < 0.05,
                'interpretation': 'Variables are dependent' if p_value < 0.05 else 'Variables are independent'
            }
        
        # ANOVA test for satisfaction across regions
        if 'satisfaction_score' in self.data.columns and 'region' in self.data.columns:
            region_groups = [group['satisfaction_score'].values for name, group in self.data.groupby('region')]
            if len(region_groups) > 1 and all(len(group) > 0 for group in region_groups):
                f_stat, p_value = stats.f_oneway(*region_groups)
                
                tests['satisfaction_by_region_anova'] = {
                    'f_statistic': f_stat,
                    'p_value': p_value,
                    'is_significant': p_value < 0.05,
                    'interpretation': 'Significant difference in satisfaction across regions' if p_value < 0.05 else 'No significant difference in satisfaction across regions'
                }
        
        return tests
    
    def _generate_key_insights(self):
        """
        Generate key insights from the analysis.
        
        Returns:
            list: List of key insights
        """
        insights = []
        
        if not self.analysis_results:
            return insights
        
        # Response distribution insights
        if 'response_distribution' in self.analysis_results:
            for question, data in self.analysis_results['response_distribution'].items():
                if data['most_popular']:
                    insights.append(f"'{data['most_popular']}' is the most popular response for '{question}' with {data['response_percentages'][data['most_popular']]}% of responses")
                
                if data['diversity_score'] > 0.5:
                    insights.append(f"High diversity in responses for '{question}' - no clear consensus")
        
        # Satisfaction insights
        if 'satisfaction_analysis' in self.analysis_results:
            sat_data = self.analysis_results['satisfaction_analysis']
            if 'statistics' in sat_data:
                mean_sat = sat_data['statistics']['mean']
                if mean_sat >= 4:
                    insights.append(f"High overall satisfaction: {mean_sat:.1f}/5.0")
                elif mean_sat <= 2:
                    insights.append(f"Low overall satisfaction: {mean_sat:.1f}/5.0 - requires attention")
        
        # Demographic insights
        if 'demographic_analysis' in self.analysis_results:
            demo_data = self.analysis_results['demographic_analysis']
            if 'region' in demo_data:
                top_region = max(demo_data['region']['distribution'].items(), key=lambda x: x[1])
                insights.append(f"Most responses come from {top_region[0]} region ({top_region[1]} responses)")
        
        # Temporal insights
        if 'temporal_analysis' in self.analysis_results:
            temp_data = self.analysis_results['temporal_analysis']
            if 'hourly_responses' in temp_data:
                peak_hour = max(temp_data['hourly_responses'].items(), key=lambda x: x[1])
                insights.append(f"Peak response time: {peak_hour[0]}:00 with {peak_hour[1]} responses")
        
        return insights
    
    def get_summary_statistics(self):
        """
        Get summary statistics for quick overview.
        
        Returns:
            dict: Summary statistics
        """
        if self.data is None:
            return {}
        
        summary = {
            'total_respondents': len(self.data['respondent_id'].unique()) if 'respondent_id' in self.data.columns else len(self.data),
            'total_questions': len(self.data['question'].unique()) if 'question' in self.data.columns else 0,
            'total_responses': len(self.data),
            'date_range': {},
            'demographics': {},
            'average_satisfaction': 0
        }
        
        # Date range
        if 'timestamp' in self.data.columns:
            summary['date_range'] = {
                'start': self.data['timestamp'].min().strftime('%Y-%m-%d'),
                'end': self.data['timestamp'].max().strftime('%Y-%m-%d'),
                'days': (self.data['timestamp'].max() - self.data['timestamp'].min()).days
            }
        
        # Demographics
        for demo_col in ['region', 'gender', 'age_group']:
            if demo_col in self.data.columns:
                summary['demographics'][demo_col] = len(self.data[demo_col].unique())
        
        # Satisfaction
        if 'satisfaction_score' in self.data.columns:
            summary['average_satisfaction'] = round(self.data['satisfaction_score'].mean(), 2)
        
        return summary
