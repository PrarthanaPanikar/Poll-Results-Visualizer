"""
Visualizer Module
Handles creation of various charts and visualizations for poll data.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as pyo
from wordcloud import WordCloud
import warnings
warnings.filterwarnings('ignore')

# Set style for matplotlib
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class PollVisualizer:
    """
    A class for creating various visualizations from poll data.
    """
    
    def __init__(self, data=None):
        self.data = data
        self.charts = {}
        self.color_palette = px.colors.qualitative.Set3
    
    def set_data(self, data):
        """Set the data for visualization."""
        self.data = data
    
    def create_bar_chart(self, data_column, title=None, interactive=False, save_path=None):
        """
        Create a bar chart for categorical data.
        
        Args:
            data_column (str): Column name to visualize
            title (str): Chart title
            interactive (bool): Whether to create interactive chart
            save_path (str): Path to save the chart
            
        Returns:
            Figure object
        """
        if self.data is None or data_column not in self.data.columns:
            return None
        
        # Count values
        value_counts = self.data[data_column].value_counts()
        
        if interactive:
            # Create interactive Plotly bar chart
            fig = px.bar(
                x=value_counts.index,
                y=value_counts.values,
                title=title or f'Distribution of {data_column}',
                labels={'x': data_column.title(), 'y': 'Count'},
                color=value_counts.index,
                color_discrete_sequence=self.color_palette
            )
            
            fig.update_layout(
                xaxis_title=data_column.title(),
                yaxis_title='Count',
                showlegend=False,
                height=500
            )
            
            if save_path:
                fig.write_html(save_path)
        else:
            # Create static matplotlib bar chart
            plt.figure(figsize=(10, 6))
            bars = plt.bar(value_counts.index, value_counts.values, color=self.color_palette[:len(value_counts)])
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}',
                        ha='center', va='bottom')
            
            plt.title(title or f'Distribution of {data_column}')
            plt.xlabel(data_column.title())
            plt.ylabel('Count')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            fig = plt.gcf()
        
        self.charts[f'bar_{data_column}'] = fig
        return fig
    
    def create_pie_chart(self, data_column, title=None, interactive=False, save_path=None):
        """
        Create a pie chart for categorical data.
        
        Args:
            data_column (str): Column name to visualize
            title (str): Chart title
            interactive (bool): Whether to create interactive chart
            save_path (str): Path to save the chart
            
        Returns:
            Figure object
        """
        if self.data is None or data_column not in self.data.columns:
            return None
        
        # Count values
        value_counts = self.data[data_column].value_counts()
        
        if interactive:
            # Create interactive Plotly pie chart
            fig = px.pie(
                names=value_counts.index,
                values=value_counts.values,
                title=title or f'Percentage Distribution of {data_column}',
                color_discrete_sequence=self.color_palette
            )
            
            fig.update_traces(
                textposition='inside', 
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
            )
            
            if save_path:
                fig.write_html(save_path)
        else:
            # Create static matplotlib pie chart
            plt.figure(figsize=(8, 8))
            plt.pie(
                value_counts.values, 
                labels=value_counts.index, 
                autopct='%1.1f%%',
                startangle=90,
                colors=self.color_palette[:len(value_counts)]
            )
            
            plt.title(title or f'Percentage Distribution of {data_column}')
            plt.axis('equal')
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            fig = plt.gcf()
        
        self.charts[f'pie_{data_column}'] = fig
        return fig
    
    def create_line_chart(self, x_column, y_column, title=None, interactive=False, save_path=None):
        """
        Create a line chart for time series or continuous data.
        
        Args:
            x_column (str): X-axis column
            y_column (str): Y-axis column
            title (str): Chart title
            interactive (bool): Whether to create interactive chart
            save_path (str): Path to save the chart
            
        Returns:
            Figure object
        """
        if self.data is None or x_column not in self.data.columns or y_column not in self.data.columns:
            return None
        
        # Prepare data
        plot_data = self.data.groupby(x_column)[y_column].mean().reset_index()
        
        if interactive:
            # Create interactive Plotly line chart
            fig = px.line(
                plot_data,
                x=x_column,
                y=y_column,
                title=title or f'{y_column.title()} over {x_column.title()}',
                markers=True,
                line_shape='linear'
            )
            
            fig.update_layout(
                xaxis_title=x_column.title(),
                yaxis_title=y_column.title(),
                height=500
            )
            
            if save_path:
                fig.write_html(save_path)
        else:
            # Create static matplotlib line chart
            plt.figure(figsize=(12, 6))
            plt.plot(plot_data[x_column], plot_data[y_column], marker='o', linewidth=2, markersize=6)
            
            plt.title(title or f'{y_column.title()} over {x_column.title()}')
            plt.xlabel(x_column.title())
            plt.ylabel(y_column.title())
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            fig = plt.gcf()
        
        self.charts[f'line_{x_column}_{y_column}'] = fig
        return fig
    
    def create_stacked_bar_chart(self, group_column, value_column, title=None, interactive=False, save_path=None):
        """
        Create a stacked bar chart for grouped categorical data.
        
        Args:
            group_column (str): Column for grouping
            value_column (str): Column with values
            title (str): Chart title
            interactive (bool): Whether to create interactive chart
            save_path (str): Path to save the chart
            
        Returns:
            Figure object
        """
        if self.data is None or group_column not in self.data.columns or value_column not in self.data.columns:
            return None
        
        # Create cross-tabulation
        cross_tab = pd.crosstab(self.data[group_column], self.data[value_column])
        
        if interactive:
            # Create interactive Plotly stacked bar chart
            fig = go.Figure()
            
            for i, column in enumerate(cross_tab.columns):
                fig.add_trace(go.Bar(
                    name=column,
                    x=cross_tab.index,
                    y=cross_tab[column],
                    marker_color=self.color_palette[i % len(self.color_palette)]
                ))
            
            fig.update_layout(
                barmode='stack',
                title=title or f'{value_column.title()} by {group_column.title()}',
                xaxis_title=group_column.title(),
                yaxis_title='Count',
                height=500
            )
            
            if save_path:
                fig.write_html(save_path)
        else:
            # Create static matplotlib stacked bar chart
            plt.figure(figsize=(12, 6))
            cross_tab.plot(kind='bar', stacked=True, color=self.color_palette[:len(cross_tab.columns)])
            
            plt.title(title or f'{value_column.title()} by {group_column.title()}')
            plt.xlabel(group_column.title())
            plt.ylabel('Count')
            plt.xticks(rotation=45)
            plt.legend(title=value_column.title())
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            fig = plt.gcf()
        
        self.charts[f'stacked_{group_column}_{value_column}'] = fig
        return fig
    
    def create_histogram(self, data_column, bins=10, title=None, interactive=False, save_path=None):
        """
        Create a histogram for numerical data.
        
        Args:
            data_column (str): Column name to visualize
            bins (int): Number of bins
            title (str): Chart title
            interactive (bool): Whether to create interactive chart
            save_path (str): Path to save the chart
            
        Returns:
            Figure object
        """
        if self.data is None or data_column not in self.data.columns:
            return None
        
        if interactive:
            # Create interactive Plotly histogram
            fig = px.histogram(
                self.data,
                x=data_column,
                nbins=bins,
                title=title or f'Distribution of {data_column}',
                color_discrete_sequence=['#636EFA']
            )
            
            fig.update_layout(
                xaxis_title=data_column.title(),
                yaxis_title='Frequency',
                height=500
            )
            
            if save_path:
                fig.write_html(save_path)
        else:
            # Create static matplotlib histogram
            plt.figure(figsize=(10, 6))
            plt.hist(self.data[data_column], bins=bins, alpha=0.7, color='#636EFA', edgecolor='black')
            
            plt.title(title or f'Distribution of {data_column}')
            plt.xlabel(data_column.title())
            plt.ylabel('Frequency')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            fig = plt.gcf()
        
        self.charts[f'hist_{data_column}'] = fig
        return fig
    
    def create_box_plot(self, group_column, value_column, title=None, interactive=False, save_path=None):
        """
        Create a box plot for comparing distributions across groups.
        
        Args:
            group_column (str): Column for grouping
            value_column (str): Column with values
            title (str): Chart title
            interactive (bool): Whether to create interactive chart
            save_path (str): Path to save the chart
            
        Returns:
            Figure object
        """
        if self.data is None or group_column not in self.data.columns or value_column not in self.data.columns:
            return None
        
        if interactive:
            # Create interactive Plotly box plot
            fig = px.box(
                self.data,
                x=group_column,
                y=value_column,
                title=title or f'{value_column.title()} by {group_column.title()}'
            )
            
            fig.update_layout(
                xaxis_title=group_column.title(),
                yaxis_title=value_column.title(),
                height=500
            )
            
            if save_path:
                fig.write_html(save_path)
        else:
            # Create static matplotlib box plot
            plt.figure(figsize=(12, 6))
            sns.boxplot(data=self.data, x=group_column, y=value_column)
            
            plt.title(title or f'{value_column.title()} by {group_column.title()}')
            plt.xlabel(group_column.title())
            plt.ylabel(value_column.title())
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            fig = plt.gcf()
        
        self.charts[f'box_{group_column}_{value_column}'] = fig
        return fig
    
    def create_word_cloud(self, text_column, title=None, save_path=None, max_words=100):
        """
        Create a word cloud from text data.
        
        Args:
            text_column (str): Column containing text data
            title (str): Chart title
            save_path (str): Path to save the chart
            max_words (int): Maximum number of words
            
        Returns:
            Figure object
        """
        if self.data is None or text_column not in self.data.columns:
            return None
        
        # Combine all text
        text = ' '.join(self.data[text_column].astype(str))
        
        # Generate word cloud
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color='white',
            max_words=max_words,
            colormap='viridis'
        ).generate(text)
        
        # Create plot
        plt.figure(figsize=(12, 6))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(title or f'Word Cloud of {text_column}', fontsize=16, pad=20)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        fig = plt.gcf()
        self.charts[f'wordcloud_{text_column}'] = fig
        return fig
    
    def create_heatmap(self, columns=None, title=None, save_path=None):
        """
        Create a correlation heatmap for numerical columns.
        
        Args:
            columns (list): List of columns to include
            title (str): Chart title
            save_path (str): Path to save the chart
            
        Returns:
            Figure object
        """
        if self.data is None:
            return None
        
        # Select numerical columns
        if columns is None:
            numerical_cols = self.data.select_dtypes(include=[np.number]).columns
        else:
            numerical_cols = [col for col in columns if col in self.data.columns and pd.api.types.is_numeric_dtype(self.data[col])]
        
        if len(numerical_cols) < 2:
            return None
        
        # Calculate correlation matrix
        correlation_matrix = self.data[numerical_cols].corr()
        
        # Create heatmap
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            correlation_matrix,
            annot=True,
            cmap='coolwarm',
            center=0,
            square=True,
            linewidths=1,
            cbar_kws={"shrink": .8}
        )
        
        plt.title(title or 'Correlation Heatmap', fontsize=16)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        fig = plt.gcf()
        self.charts['heatmap'] = fig
        return fig
    
    def create_dashboard_layout(self, save_path=None):
        """
        Create a comprehensive dashboard layout with multiple charts.
        
        Args:
            save_path (str): Path to save the dashboard
            
        Returns:
            Figure object
        """
        if self.data is None:
            return None
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('Response Distribution', 'Satisfaction Scores', 
                          'Regional Responses', 'Daily Response Trends',
                          'Age Group Distribution', 'Gender Distribution'),
            specs=[[{"type": "bar"}, {"type": "histogram"}],
                   [{"type": "bar"}, {"type": "scatter"}],
                   [{"type": "pie"}, {"type": "pie"}]]
        )
        
        # Add traces based on available columns
        row, col = 1, 1
        
        # Response distribution
        if 'response' in self.data.columns:
            response_counts = self.data['response'].value_counts()
            fig.add_trace(
                go.Bar(x=response_counts.index, y=response_counts.values, name="Responses"),
                row=row, col=col
            )
        
        # Satisfaction histogram
        if 'satisfaction_score' in self.data.columns:
            row, col = 1, 2
            fig.add_trace(
                go.Histogram(x=self.data['satisfaction_score'], name="Satisfaction"),
                row=row, col=col
            )
        
        # Regional responses
        if 'region' in self.data.columns:
            row, col = 2, 1
            region_counts = self.data['region'].value_counts()
            fig.add_trace(
                go.Bar(x=region_counts.index, y=region_counts.values, name="Regions"),
                row=row, col=col
            )
        
        # Daily trends
        if 'timestamp' in self.data.columns:
            row, col = 2, 2
            daily_counts = self.data.groupby(self.data['timestamp'].dt.date).size()
            fig.add_trace(
                go.Scatter(x=daily_counts.index, y=daily_counts.values, mode='lines+markers', name="Daily Responses"),
                row=row, col=col
            )
        
        # Age group pie chart
        if 'age_group' in self.data.columns:
            row, col = 3, 1
            age_counts = self.data['age_group'].value_counts()
            fig.add_trace(
                go.Pie(labels=age_counts.index, values=age_counts.values, name="Age Groups"),
                row=row, col=col
            )
        
        # Gender pie chart
        if 'gender' in self.data.columns:
            row, col = 3, 2
            gender_counts = self.data['gender'].value_counts()
            fig.add_trace(
                go.Pie(labels=gender_counts.index, values=gender_counts.values, name="Gender"),
                row=row, col=col
            )
        
        # Update layout
        fig.update_layout(
            height=1200,
            title_text="Poll Results Dashboard",
            showlegend=False
        )
        
        if save_path:
            fig.write_html(save_path)
        
        self.charts['dashboard'] = fig
        return fig
    
    def save_all_charts(self, output_dir='outputs/charts'):
        """
        Save all created charts to the specified directory.
        
        Args:
            output_dir (str): Directory to save charts
        """
        import os
        
        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        for chart_name, chart in self.charts.items():
            if hasattr(chart, 'write_html'):
                # Plotly chart
                chart.write_html(f'{output_dir}/{chart_name}.html')
            else:
                # Matplotlib chart
                chart.savefig(f'{output_dir}/{chart_name}.png', dpi=300, bbox_inches='tight')
        
        print(f"All charts saved to {output_dir}")
    
    def get_chart_summary(self):
        """
        Get a summary of all created charts.
        
        Returns:
            dict: Chart summary
        """
        return {
            'total_charts': len(self.charts),
            'chart_types': list(self.charts.keys()),
            'data_shape': self.data.shape if self.data is not None else None
        }
