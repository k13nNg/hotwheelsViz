import plotly.express as px
import pandas as pd


# Import data from GitHub
# data = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_with_codes.csv')
data = pd.read_csv("./Phase 2/processedPhase2.csv")

summary_data = (
    data.groupby(["Country Code", "Country (Normalized)", "Year"])
      .size()
      .reset_index(name="Number of Hotwheels versions produced")
)

# Ensure Year is numeric and sorted
summary_data = summary_data.sort_values("Year")


# Create basic choropleth map
fig = px.choropleth(summary_data, 
                    locations='Country Code', 
                    color='Number of Hotwheels versions produced', 
                    hover_name='Country (Normalized)',
                    projection='natural earth', 
                    animation_frame='Year',
                    title='Hotwheels Cars Produced by Country and Year')

# fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1000
fig.show()
