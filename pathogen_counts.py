# pathogen_counts.py
import requests
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta

# Step 1: Create the 'images' folder if it doesn't exist
os.makedirs("images", exist_ok=True)

# Step 2: Define pathogens to process
pathogens = ["ebola-zaire", "ebola-sudan", "mpox", "west-nile", "cchf"]

# Step 3: Get the last 6 months' date range
end_date = datetime.today()
start_date = end_date - timedelta(days=180)

# Function to fetch and count sequences for a given pathogen
def fetch_monthly_counts(pathogen):
    print(f"Inside monthly counts for {pathogen}")
    monthly_counts = []
    ncbi_monthly_counts = []
    
    for i in range(6):

        # Make calls for all submitters
        # Get first and last day of the month
        month_start = (start_date + timedelta(days=i * 30)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        # API request parameters
        api_url = f"https://lapis.pathoplexus.org/{pathogen}/sample/aggregated"
        params = {
            "earliestReleaseDateFrom": month_start.strftime("%Y-%m-%d"),
            "earliestReleaseDateTo": month_end.strftime("%Y-%m-%d"),
        }

        # Make the API request
        response = requests.get(api_url, params=params)

        if response.status_code == 200:
            data = response.json()
            # Extract count if available, otherwise 0
            count = data['data'][0]['count'] if data.get('data') else 0
            monthly_counts.append((month_start.strftime("%Y-%m"), count))
        else:
            print(f"Error fetching data for {pathogen} in {month_start.strftime('%Y-%m')}: {response.status_code}")
            monthly_counts.append((month_start.strftime("%Y-%m"), 0))

        # Make calls for NCBI submitters
        params = {
            "earliestReleaseDateFrom": month_start.strftime("%Y-%m-%d"),
            "earliestReleaseDateTo": month_end.strftime("%Y-%m-%d"),
            "submitter": "insdc_ingest_user",
        }

        # Make the API request
        response = requests.get(api_url, params=params)

        if response.status_code == 200:
            data = response.json()
            # Extract count if available, otherwise 0
            count = data['data'][0]['count'] if data.get('data') else 0
            ncbi_monthly_counts.append((month_start.strftime("%Y-%m"), count))
        else:
            print(f"Error fetching data for {pathogen} in {month_start.strftime('%Y-%m')}: {response.status_code}")
            ncbi_monthly_counts.append((month_start.strftime("%Y-%m"), 0))
    
    return monthly_counts, ncbi_monthly_counts

# Function to generate and save a stacked bar chart
def generate_chart(pathogen, monthly_counts, ncbi_counts):
    # Create a DataFrame from the counts
    df = pd.DataFrame(monthly_counts, columns=["month", "total_count"])
    df2 = pd.DataFrame(ncbi_counts, columns=["month", "count"])

    # Calculate the "direct" counts as total - ncbi counts
    df["ncbi_count"] = df2["count"]
    df["direct_count"] = df["total_count"] - df["ncbi_count"]

    # Create the stacked bar chart
    plt.figure(figsize=(10, 6))

    # Bar for NCBI (blue)
    plt.bar(df["month"], df["ncbi_count"], color="royalblue", label="NCBI")
    # Bar for Direct (orange)
    plt.bar(df["month"], df["direct_count"], bottom=df["ncbi_count"], color="darkorange", label="Direct")

    # Title and labels
    plt.title(f"{pathogen.replace('-', ' ').title()} Sequences (Last 6 Months)")
    plt.xlabel("Month")
    plt.ylabel("Number of Sequences")
    plt.xticks(rotation=45)
    plt.legend()

    # Layout adjustment for better spacing
    plt.tight_layout()

    # Save the chart with a descriptive name
    image_path = f"images/{pathogen}_6monthcounts.png"
    plt.savefig(image_path)
    print(f"✅ Saved: {image_path}")
    plt.close()


# Step 4: Process each pathogen
for pathogen in pathogens:
    print(f"Working on: {pathogen}")
    counts, ncbi_counts = fetch_monthly_counts(pathogen)
    generate_chart(pathogen, counts, ncbi_counts)

print("✅ All charts generated successfully!")
