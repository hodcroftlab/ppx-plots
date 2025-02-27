import requests
import plotly.express as px
import pandas as pd

# List of pathogens to process
pathogens = ['mpox', 'ebola-zaire', 'ebola-sudan', 'west-nile', 'cchf']

# Function to fetch data and create map
def create_map_for_pathogen(pathogen):
    # Step 1: Fetch data from the API for the given pathogen
    url = f"https://lapis.pathoplexus.org/{pathogen}/sample/details?fields=geoLocCountry"
    response = requests.get(url)
    data = response.json()

    # Step 2: Process the data to count the occurrences of each country
    countries = [entry['geoLocCountry'] for entry in data['data']]
    country_counts = pd.Series(countries).value_counts().reset_index()
    country_counts.columns = ['Country', 'Sequence Count']

    # Step 3: Load a map using plotly.express
    fig = px.choropleth(country_counts, 
                        locations='Country', 
                        locationmode='country names', 
                        color='Sequence Count', 
                        hover_name='Country', 
                        color_continuous_scale=px.colors.sequential.Plasma,
                        labels={'Sequence Count': 'Number of Sequences'},
                        title=f"Geographic Distribution of {pathogen.capitalize()} Sequences")

    # Step 4: Save the map as an HTML file
    image_path = f"images/{pathogen}_geo_map.html"
    fig.write_html(image_path)
    print(f"✅ Saved: {image_path}")

# Loop through all pathogens and create a map for each
for pathogen in pathogens:
    create_map_for_pathogen(pathogen)
