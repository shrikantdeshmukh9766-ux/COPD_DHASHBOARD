import requests
import pandas as pd
from datetime import datetime

# Configuration
KOBO_TOKEN = "23801d339dd6d16509a79250731f126401d5f7a3"
FORM_ID = "afWux6DQFqmZrEpK54BobD"
KOBO_URL = "https://kobo.humanitarianresponse.info/api/v2"  # or https://kobo.humanitarianresponse.info

def fetch_kobo_data(token, form_id):
    """Fetch data from KoBoToolbox API"""
    url = f"{KOBO_URL}/api/v2/assets/{form_id}/data.json"
    headers = {
        "Authorization": f"Token {token}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()['results']
        print(f"✓ Successfully fetched {len(data)} records")
        return data
    else:
        print(f"✗ Error: {response.status_code} - {response.text}")
        return None

def analyze_asha_submissions(data):
    """Analyze ASHA submissions with overall and monthly breakdown"""
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Select only the 3 columns with exact names from KoBoToolbox
    required_cols = ['asha', 'Paticipant', '_submission_time']
    
    # Check if columns exist
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"✗ Missing columns: {missing_cols}")
        print(f"Available columns: {df.columns.tolist()}")
        return None
    
    df = df[required_cols]
    
    # Convert submission time to datetime
    df['_submission_time'] = pd.to_datetime(df['_submission_time'])
    
    # Extract date components
    df['date'] = df['_submission_time'].dt.date
    df['month'] = df['_submission_time'].dt.to_period('M')
    df['month_name'] = df['_submission_time'].dt.strftime('%B %Y')
    df['year'] = df['_submission_time'].dt.year
    
    return df

def print_overall_summary(df):
    """Print overall summary of forms by ASHA"""
    print("\n" + "="*80)
    print("📊 OVERALL SUMMARY - Total Forms Filled by Each ASHA Worker")
    print("="*80)
    
    summary = df.groupby('asha').agg({
        'Paticipant': 'count',
        '_submission_time': ['min', 'max']
    }).reset_index()
    
    summary.columns = ['ASHA Worker', 'Total Forms', 'First Submission', 'Last Submission']
    summary = summary.sort_values('Total Forms', ascending=False)
    
    # Add percentage
    summary['Percentage (%)'] = (summary['Total Forms'] / summary['Total Forms'].sum() * 100).round(2)
    
    print(summary.to_string(index=False))
    print(f"\n{'Total Forms:':<20} {summary['Total Forms'].sum()}")
    print(f"{'Total ASHA Workers:':<20} {len(summary)}")
    print(f"{'Average per ASHA:':<20} {summary['Total Forms'].mean():.2f}")
    
    return summary

def print_monthly_summary(df):
    """Print monthly breakdown of forms by ASHA"""
    print("\n" + "="*80)
    print("📅 MONTHLY BREAKDOWN - Forms Filled by Each ASHA Worker")
    print("="*80)
    
    # Create pivot table
    monthly = df.groupby(['asha', 'month_name']).size().reset_index(name='Forms')
    pivot = monthly.pivot(index='asha', columns='month_name', values='Forms').fillna(0).astype(int)
    
    # Add total column
    pivot['TOTAL'] = pivot.sum(axis=1)
    
    # Sort by total descending
    pivot = pivot.sort_values('TOTAL', ascending=False)
    
    # Add row totals
    pivot.loc['TOTAL'] = pivot.sum()
    
    print(pivot.to_string())
    
    return pivot

def filter_by_month(df, year=None, month=None):
    """Filter and display data for specific month"""
    filtered = df.copy()
    
    if year:
        filtered = filtered[filtered['year'] == year]
    
    if month:
        filtered = filtered[filtered['_submission_time'].dt.month == month]
    
    if year and month:
        month_name = datetime(year, month, 1).strftime('%B %Y')
    elif year:
        month_name = f"Year {year}"
    else:
        month_name = "All Time"
    
    print("\n" + "="*80)
    print(f"🔍 FILTERED SUMMARY - {month_name}")
    print("="*80)
    
    summary = filtered.groupby('asha').size().reset_index(name='Forms Count')
    summary = summary.sort_values('Forms Count', ascending=False)
    summary['Percentage (%)'] = (summary['Forms Count'] / summary['Forms Count'].sum() * 100).round(2)
    
    print(summary.to_string(index=False))
    print(f"\n{'Total Forms:':<20} {summary['Forms Count'].sum()}")
    
    return summary

def print_detailed_view(df):
    """Print detailed view with all submissions"""
    print("\n" + "="*80)
    print("📋 DETAILED VIEW - All Submissions")
    print("="*80)
    
    detailed = df[['asha', 'Paticipant', '_submission_time', 'date', 'month_name']].copy()
    detailed = detailed.sort_values('_submission_time', ascending=False)
    
    print(detailed.to_string(index=False))
    print(f"\nTotal Records: {len(detailed)}")

def export_to_excel(df, overall, monthly, filename='asha_report.xlsx'):
    """Export all summaries to Excel"""
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Raw data with exact column names
        df[['asha', 'Paticipant', '_submission_time', 'date', 'month_name']].to_excel(
            writer, sheet_name='Raw Data', index=False
        )
        
        # Overall summary
        overall.to_excel(writer, sheet_name='Overall Summary', index=False)
        
        # Monthly breakdown
        monthly.to_excel(writer, sheet_name='Monthly Breakdown')
        
        # ASHA-wise detailed list
        for asha_name in df['asha'].unique():
            asha_data = df[df['asha'] == asha_name][['Paticipant', '_submission_time', 'date', 'month_name']]
            asha_data = asha_data.sort_values('_submission_time', ascending=False)
            sheet_name = f"{asha_name}"[:31]  # Excel sheet name limit
            asha_data.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"\n✓ Report exported to '{filename}'")

# Main Execution
if __name__ == "__main__":
    print("Starting KoBoToolbox Data Analysis...")
    print("="*80)
    
    # Step 1: Fetch data
    data = fetch_kobo_data(KOBO_TOKEN, FORM_ID)
    
    if data:
        # Step 2: Process data
        df = analyze_asha_submissions(data)
        
        if df is not None:
            # Step 3: Display overall summary
            overall_summary = print_overall_summary(df)
            
            # Step 4: Display monthly breakdown
            monthly_summary = print_monthly_summary(df)
            
            # Step 5: Example filters (uncomment to use)
            
            # Filter for March 2024
            # filter_by_month(df, year=2024, month=3)
            
            # Filter for February 2024
            # filter_by_month(df, year=2024, month=2)
            
            # Filter for entire year 2024
            # filter_by_month(df, year=2024)
            
            # Filter for January 2025
            # filter_by_month(df, year=2025, month=1)
            
            # Step 6: Show detailed view (optional)
            # print_detailed_view(df)
            
            # Step 7: Export to Excel
            export_to_excel(df, overall_summary, monthly_summary)
            
            print("\n" + "="*80)
            print("✓ Analysis Complete!")
            print("="*80)
        else:
            print("✗ Failed to process data. Please check column names.")
    else:
        print("✗ Failed to fetch data. Please check your token and form ID.")

