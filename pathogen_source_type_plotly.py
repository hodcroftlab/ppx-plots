import requests
import plotly.express as px
import os
import pandas as pd

# Step 1: Create the 'images' folder if it doesn't exist
os.makedirs("images", exist_ok=True)

# Step 2: Define pathogens to process
pathogens = ['mpox', 'ebola-zaire', 'ebola-sudan', 'west-nile', 'cchf', 'hmpv', 'rsv-a', 'rsv-b', 'measles']

# Function to fetch and count sequences for a given pathogen
def fetch_counts(pathogen):
    print(f"Fetching counts for {pathogen}")
    total_seqs = 0
    total_counts = {'insdc': 0, 'direct': 0}
    open_restricted_counts = {'open': 0, 'restricted': 0}

    api_url = f"https://lapis.pathoplexus.org/{pathogen}/sample/aggregated"

    # 1. Total sequences
    params = {'versionStatus': 'LATEST_VERSION'}
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        data = response.json()
        total_seqs = data['data'][0]['count'] if data.get('data') else 0
    else:
        print(f"Error fetching total count for {pathogen}")

    # 2. INSDC submissions
    params = {'submitter': 'insdc_ingest_user', 'versionStatus': 'LATEST_VERSION'}
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        data = response.json()
        insdc_count = data['data'][0]['count'] if data.get('data') else 0
        total_counts['insdc'] = insdc_count
    else:
        print(f"Error fetching INSDC count for {pathogen}")

    # 3. Restricted sequences (only from Direct submissions)
    params = {'dataUseTerms': 'RESTRICTED', 'versionStatus': 'LATEST_VERSION'}
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        data = response.json()
        restricted_count = data['data'][0]['count'] if data.get('data') else 0
        open_restricted_counts['restricted'] = restricted_count
    else:
        print(f"Error fetching restricted count for {pathogen}")

    # 4. Calculate Direct submissions and Open Direct submissions
    total_direct = total_seqs - total_counts['insdc']
    total_counts['direct'] = total_direct
    open_restricted_counts['open'] = total_direct - open_restricted_counts['restricted']

    return total_counts, open_restricted_counts

# Function to generate and save the sunburst plot
def generate_sunburst_plot(pathogen, total_counts, open_restricted_counts):
    labels = []
    parents = []
    values = []

    data = {
    'count': [open_restricted_counts['restricted'], open_restricted_counts['open'], total_counts['insdc'], 0],
    'restriction': ['Restricted', 'Open', 'Open', 'Restricted'],
    'source': ['Direct', 'Direct', 'INSDC', 'INSDC']
    }
    df = pd.DataFrame(data)

    # Create a new column for color mapping:
    # We'll assign parents color by 'source' and leaves by 'restriction'
    # The sunburst levels are: source (parent), restriction (child)
    # So the color column will be source for parents, restriction for leaves
    df['label_for_color'] = df['restriction']  # for leaves

    # Trick: append rows for parents with their own color labels and 0 count (to appear)
    parents = df[['source']].drop_duplicates().rename(columns={'source': 'label_for_color'})
    parents['count'] = 0
    parents['source'] = parents['label_for_color']  # just to keep columns consistent
    parents['restriction'] = ''  # empty for parents

    df_plot = pd.concat([df, parents], ignore_index=True)

    fig = px.sunburst(
        df_plot, 
        path=['source', 'restriction'], 
        values='count',
        title=f"{pathogen.replace('-', ' ').title()} Count and Open/Restricted Status",
        color='label_for_color',
        color_discrete_map={
            'Direct': 'orange',
            'INSDC': 'royalblue',
            'Restricted': 'red',
            'Open': 'green'
        },
    )

    # Save as interactive HTML
    out_path = f"images/{pathogen}_donut_plot.html"  # same filename as before
    fig.write_html(out_path)
    print(f"✅ Saved: {out_path}")

# Step 4: Loop through all pathogens
for pathogen in pathogens:
    print(f"🔄 Working on: {pathogen}")
    total_counts, open_restricted_counts = fetch_counts(pathogen)
    generate_sunburst_plot(pathogen, total_counts, open_restricted_counts)

print("✅ All sunburst plots generated and saved!")
