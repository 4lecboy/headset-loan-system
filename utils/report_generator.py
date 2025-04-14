"""
Report generation utilities for creating various reports
"""
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import csv
from datetime import datetime
import os
from models.loan import LoanModel
from models.headset import HeadsetModel
from models.statistics import StatisticsModel

def generate_inventory_report(output_path=None):
    """
    Generate an inventory report of headsets
    
    Args:
        output_path (str, optional): Path to save the report
        
    Returns:
        str: Path to the generated report
    """
    headset_model = HeadsetModel()
    issued_count, available_count = headset_model.get_issued_available_counts()
    
    # Get detailed headset information
    headsets = headset_model.get_all_headsets()
    
    # Convert to DataFrame for easy manipulation
    df = pd.DataFrame(headsets, columns=['AssetTagID', 'Description', 'Status'])
    df['Status'] = df['Status'].apply(lambda x: 'Available' if x == 1 else 'Issued')
    
    # Generate timestamp for filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if not output_path:
        output_path = f"inventory_report_{timestamp}.csv"
    
    # Write to CSV
    df.to_csv(output_path, index=False)
    
    # Create a summary at the top
    with open(output_path, 'r') as original:
        content = original.read()
    
    with open(output_path, 'w') as modified:
        modified.write(f"Inventory Report - Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        modified.write(f"Total Headsets: {issued_count + available_count}\n")
        modified.write(f"Available: {available_count}\n")
        modified.write(f"Issued: {issued_count}\n")
        modified.write("\n")
        modified.write(content)
    
    return output_path

def generate_loan_history_report(start_date, end_date, output_path=None):
    """
    Generate a report of loan history within a date range
    
    Args:
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        output_path (str, optional): Path to save the report
        
    Returns:
        str: Path to the generated report
    """
    loan_model = LoanModel()
    loan_history = loan_model.get_loan_history(start_date, end_date)
    
    # Convert to DataFrame
    df = pd.DataFrame(loan_history, columns=['DateIssued', 'AshimaID', 'Name', 'Campaign', 
                                          'RoomNumber', 'AssetTag', 'IssuedBy', 'Status', 
                                          'ReceivedBy', 'ReturnedDate'])
    
    # Generate timestamp for filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if not output_path:
        output_path = f"loan_history_{timestamp}.csv"
    
    # Write to CSV
    df.to_csv(output_path, index=False)
    
    return output_path

def generate_monthly_statistics_report(year, month, output_path=None):
    """
    Generate a monthly statistics report with charts
    
    Args:
        year (int): Year
        month (int): Month (1-12)
        output_path (str, optional): Path to save the PDF report
        
    Returns:
        str: Path to the generated PDF report
    """
    stats_model = StatisticsModel()
    
    # Generate start and end dates for the month
    start_date = f"{year}-{month:02d}-01"
    if month == 12:
        end_date = f"{year+1}-01-01"
    else:
        end_date = f"{year}-{month+1:02d}-01"
    
    # Get headset statistics
    data = stats_model.get_headset_stats(start_date, end_date)
    
    # Convert to DataFrame
    df = pd.DataFrame(data, columns=['Date', 'Issued', 'Returned'])
    df['Date'] = pd.to_datetime(df['Date'])
    df['Issued'] = pd.to_numeric(df['Issued'])
    df['Returned'] = pd.to_numeric(df['Returned'])
    
    # Generate timestamp for filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if not output_path:
        output_path = f"monthly_stats_{year}_{month:02d}_{timestamp}.pdf"
    
    # Create PDF with charts
    with PdfPages(output_path) as pdf:
        # Summary page
        fig, ax = plt.subplots(figsize=(10, 2))
        ax.axis('off')
        ax.text(0.5, 0.8, f"Headset Loan Statistics: {datetime.strptime(str(month), '%m').strftime('%B')} {year}", 
               ha='center', fontsize=16)
        ax.text(0.5, 0.6, f"Total Issued: {df['Issued'].sum()}", ha='center')
        ax.text(0.5, 0.4, f"Total Returned: {df['Returned'].sum()}", ha='center')
        ax.text(0.5, 0.2, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ha='center', fontsize=10)
        pdf.savefig(fig)
        plt.close(fig)
        
        # Daily comparison chart
        fig, ax = plt.subplots(figsize=(12, 6))
        df.plot(x='Date', y=['Issued', 'Returned'], kind='bar', ax=ax)
        ax.set_title('Daily Comparison of Issued and Returned Headsets')
        ax.set_xlabel('Date')
        ax.set_ylabel('Count')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Add data labels
        for p in ax.patches:
            height = p.get_height()
            if height > 0:
                ax.annotate(f'{int(height)}', 
                          (p.get_x() + p.get_width() / 2., p.get_y() + height),
                          ha='center', va='bottom', xytext=(0, 5), 
                          textcoords='offset points')
        
        plt.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)
        
        # Cumulative chart
        fig, ax = plt.subplots(figsize=(12, 6))
        df['Cumulative Issued'] = df['Issued'].cumsum()
        df['Cumulative Returned'] = df['Returned'].cumsum()
        df.plot(x='Date', y=['Cumulative Issued', 'Cumulative Returned'], kind='line', ax=ax, marker='o')
        ax.set_title('Cumulative Issued and Returned Headsets')
        ax.set_xlabel('Date')
        ax.set_ylabel('Count')
        ax.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)
    
    return output_path