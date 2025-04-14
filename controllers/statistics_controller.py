from models.statistics import StatisticsModel
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from datetime import datetime

class StatisticsController:
    def __init__(self):
        self.statistics_model = StatisticsModel()
    
    def generate_headsets_graph(self, start_date, end_date):
        """
        Generate graph data comparing issued and returned headsets
        
        Args:
            start_date: Start date for data (YYYY-MM-DD)
            end_date: End date for data (YYYY-MM-DD)
            
        Returns:
            DataFrame with date, issued, and returned counts
        """
        # Fetch raw data from model
        raw_data = self.statistics_model.get_headset_stats(start_date, end_date)
        
        # Process data into pandas DataFrame
        data = pd.DataFrame(raw_data, columns=['DateIssued', 'Issued', 'Returned'])
        data['DateIssued'] = pd.to_datetime(data['DateIssued'])
        data['Issued'] = pd.to_numeric(data['Issued'], errors='coerce')
        data['Returned'] = pd.to_numeric(data['Returned'], errors='coerce')
        data.dropna(subset=['Issued', 'Returned'], inplace=True)
        
        return data
    
    def create_comparison_plot(self, data):
        """
        Create a bar plot comparing issued and returned headsets
        
        Args:
            data: DataFrame with issued/returned data
            
        Returns:
            matplotlib figure object
        """
        # Create the plot using matplotlib directly
        fig, ax = plt.subplots(figsize=(10, 6))
        width = 0.35  # the width of the bars

        x = data['DateIssued']
        indices = range(len(x))

        # Create bar plots
        ax.bar(indices, data['Issued'], width, label='Issued')
        ax.bar([i + width for i in indices], data['Returned'], width, label='Returned')

        # Configure plot appearance
        ax.set_title(f'Comparison of Issued and Returned Headsets')
        ax.set_xlabel('Date')
        ax.set_ylabel('Count')
        ax.set_xticks([i for i in indices])  # Set x-ticks to index positions
        ax.set_xticklabels(data['DateIssued'].dt.strftime('%Y-%m-%d'), rotation=360)
        ax.legend(title='Status')

        # Add data labels to the bars
        for p in ax.patches:
            height = p.get_height()
            if height > 0:
                ax.annotate(f'{int(height)}', 
                           (p.get_x() + p.get_width() / 2., p.get_y() + height),
                           ha='center', va='bottom', xytext=(0, 5), 
                           textcoords='offset points')

        # Ensure the x-axis labels are spaced equally
        ax.xaxis.set_major_locator(MaxNLocator(integer=True, prune=None))
        
        return fig
    
    def get_overall_statistics(self):
        """
        Get overall system statistics
        
        Returns:
            Dictionary with various statistics
        """
        return {
            'total_headsets': self.statistics_model.count_total_headsets(),
            'issued_headsets': self.statistics_model.count_issued_headsets(),
            'available_headsets': self.statistics_model.count_available_headsets(),
            'never_returned': self.statistics_model.count_never_returned(),
            'top_borrowers': self.statistics_model.get_top_borrowers(limit=5),
            'most_borrowed_headsets': self.statistics_model.get_most_borrowed_headsets(limit=5)
        }
    
    def export_statistics(self, start_date=None, end_date=None):
        """
        Export statistics to CSV
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Path to exported CSV file or None
        """
        if not start_date:
            start_date = datetime(2000, 1, 1).strftime('%Y-%m-%d')  # Default to year 2000
        
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')  # Default to today
            
        data = self.statistics_model.get_exportable_stats(start_date, end_date)
        
        # Convert data to DataFrame for easy export
        df = pd.DataFrame(data)
        
        # Create export filename with current timestamp
        filename = f"headset_statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Export to CSV
        df.to_csv(filename, index=False)
        
        return filename