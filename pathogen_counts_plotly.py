# pathogen_counts_plotly
import plotly.graph_objects as go
import pandas as pd

# Function to generate and save an interactive stacked bar chart using Plotly
def generate_chart(pathogen, monthly_counts, ncbi_counts):
    # Create a DataFrame from the counts
    df = pd.DataFrame(monthly_counts, columns=["month", "total_count"])
    df2 = pd.DataFrame(ncbi_counts, columns=["month", "count"])

    # Calculate the "direct" counts as total - ncbi counts
    df["ncbi_count"] = df2["count"]
    df["direct_count"] = df["total_count"] - df["ncbi_count"]

    # Create the stacked bar chart with Plotly
    fig = go.Figure()

    # Add bar for NCBI (blue)
    fig.add_trace(go.Bar(
        x=df["month"], y=df["ncbi_count"], name="NCBI", marker_color="royalblue"
    ))

    # Add bar for Direct (orange)
    fig.add_trace(go.Bar(
        x=df["month"], y=df["direct_count"], name="Direct", marker_color="darkorange"
    ))

    # Update layout
    fig.update_layout(
        title=f"{pathogen.replace('-', ' ').title()} Sequences (Last 6 Months)",
        xaxis_title="Month",
        yaxis_title="Number of Sequences",
        barmode='stack',
        xaxis_tickangle=-45,
        template="plotly_dark",  # Optional: Change theme for better appearance
        autosize=True
    )

    # Save the chart as an HTML file
    image_path = f"images/{pathogen}_6monthcounts_interactive.html"
    fig.write_html(image_path)
    print(f"✅ Saved: {image_path}")

# Example of usage for a single pathogen
pathogen = "ebola-zaire"
monthly_counts = [("2025-02", 100), ("2025-03", 200), ("2025-04", 150)]  # Sample data
ncbi_counts = [("2025-02", 50), ("2025-03", 120), ("2025-04", 80)]  # Sample NCBI counts
generate_chart(pathogen, monthly_counts, ncbi_counts)
