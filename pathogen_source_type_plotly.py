import requests
import pandas as pd
import plotly.graph_objects as go
import os

# Step 1: Create the 'images' folder if it doesn't exist
os.makedirs("images", exist_ok=True)

# Step 2: Define pathogens to process
pathogens = ["ebola-zaire", "ebola-sudan", "mpox", "west-nile", "cchf"]

# Function to fetch and count sequences for a given pathogen
def fetch_counts(pathogen):
    print(f"Inside counts for {pathogen}")
    total_seqs = 0
    total_counts = {'insdc': 0, 'direct': 0}
    open_restricted_counts = {'open': 0, 'restricted': 0}

    # API request parameters (no date range filter for all time data)
    api_url = f"https://lapis.pathoplexus.org/{pathogen}/sample/aggregated"

    # 1. Make the first API request to get the total count of sequences
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        total_count = data['data'][0]['count'] if data.get('data') else 0
        total_counts['direct'] += total_count
        total_seqs = total_counts['direct']
    else:
        print(f"Error fetching data for {pathogen}: {response.status_code}")
    
    # 2. Make the second API request to get the count of sequences from 'insdc_ingest_user'
    params = {'submitter': 'insdc_ingest_user'}
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        data = response.json()
        ncbi_count = data['data'][0]['count'] if data.get('data') else 0
        total_counts['insdc'] += ncbi_count
    else:
        print(f"Error fetching data for {pathogen}: {response.status_code}")
    
    # The remainder will be 'direct' submissions
    total_counts['direct'] = total_counts['direct'] - total_counts['insdc']

    # 3. Make the third API request to find RESTRICTED sequences
    params = {'dataUseTerms': 'RESTRICTED'}
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        data = response.json()
        restricted_count = data['data'][0]['count'] if data.get('data') else 0
        open_restricted_counts['restricted'] += restricted_count
    else:
        print(f"Error fetching data for {pathogen}: {response.status_code}")
    
    # The remainder will be OPEN sequences
    open_restricted_counts['open'] = total_seqs - open_restricted_counts['restricted']
    
    return total_counts, open_restricted_counts

# Function to generate and save the donut plot with two rings
def generate_donut_plot(pathogen, total_counts, open_restricted_counts):
    # Outer ring data: Proportion of sequences from 'insdc_ingest_user' and 'direct'
    outer_labels = ['INSBC', 'Direct']
    outer_values = [total_counts['insdc'], total_counts['direct']]

    # Inner ring data: Proportion of sequences 'OPEN' vs 'RESTRICTED'
    inner_labels = ['OPEN', 'RESTRICTED']
    inner_values = [open_restricted_counts['open'], open_restricted_counts['restricted']]

    # Create the plotly donut plot
    fig = go.Figure()

    # Inner ring (OPEN vs RESTRICTED for non-NCBI sequences)
    fig.add_trace(go.Pie(
        labels=inner_labels,
        values=inner_values,
        direction="counterclockwise",
        domain={'x': [0.15, 0.85], 'y': [0.15, 0.85]},
        hole=0.5,  # smaller hole size for the inner ring
        hoverinfo="label+percent",
        marker=dict(colors=["green", "red"]),
        name="Data Use Terms"
    ))

    # Outer ring (Total counts split by INSBC and Direct)
    fig.add_trace(go.Pie(
        labels=outer_labels,
        values=outer_values,
        direction="counterclockwise",
        hole=0.7,  # hole size to create a donut plot
        hoverinfo="label+percent",
        marker=dict(colors=["royalblue", "darkorange"]),
        name="Submitter Type"
    ))



    # Update layout for better presentation
    fig.update_layout(
        title=f"{pathogen.replace('-', ' ').title()} Data Summary",
        showlegend=True,
        template="plotly",
        annotations=[
            dict(
                font=dict(size=20),
                showarrow=False,
                text="Submitter Type",
                x=0.5,
                y=0.75
            ),
            dict(
                font=dict(size=20),
                showarrow=False,
                text="Data Use Terms",
                x=0.5,
                y=0.25
            )
        ]
    )

    # Save the donut plot as an HTML file
    image_path = f"images/{pathogen}_donut_plot.html"
    fig.write_html(image_path)
    print(f"✅ Saved: {image_path}")

# Step 4: Process each pathogen
for pathogen in pathogens:
    print(f"Working on: {pathogen}")
    total_counts, open_restricted_counts = fetch_counts(pathogen)
    generate_donut_plot(pathogen, total_counts, open_restricted_counts)

print("✅ All donut plots generated successfully!")
