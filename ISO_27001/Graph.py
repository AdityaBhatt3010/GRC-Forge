import pandas as pd
import plotly.graph_objects as go

# Load the CSV
df = pd.read_csv("ISO_27001_Summary.csv")

# Count compliance statuses
status_counts = df["Compliance_Status"].value_counts()
labels = status_counts.index.tolist()
values = status_counts.values.tolist()
total = sum(values)

# Traffic light colors
colors = ['green' if s == 'Compliant' else 'yellow' if s == 'Partially Compliant' else 'red' for s in labels]

# Custom label with line breaks
custom_labels = [
    f"{label}<br>{value} Controls<br>{round((value / total) * 100)}%"
    for label, value in zip(labels, values)
]

# Build the pie chart
fig = go.Figure(data=[
    go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors, line=dict(color='black', width=1.5)),
        text=custom_labels,
        textinfo='text',
        insidetextorientation='horizontal',
        hole=0
    )
])

fig.update_layout(
    title="ISO 27001 Compliance Breakdown",
    font=dict(size=14),
    paper_bgcolor="white",
    showlegend=False
)

fig.write_image("ISO_27001_Compliance_PieChart.jpeg", format="jpeg", width=800, height=600)
print("✅ Pie chart saved as 'ISO_27001_Compliance_PieChart.jpeg'")
