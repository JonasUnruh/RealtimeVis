# Code Documentation
This Markdown file will give a short overview of the functionality of the code in each file. It should give a basic understanding of what is happening, and how this is accomplished.

## `preprocessing.py`
### Purpose
The `preprocessing.py` file is used to preprocess the dataset and break it down into manageble chunks that can be handled by the dashboard itsself. The end goal behind this is to reduce the almost 3GB large file into many smaller files that can be quickly loaded and do not cause excessive stress to the system.

### Functionality
This file achieves its purpose using Polars. Polars is an open-source library for data manipulation made specifically for large datasets. Therefore it is meant to be very efficient and fast when processing our dataset.

The data is read as a Polars dataframe and filtered to give a data overview for each state and year over relevant columns. An aggregate is also drawn for the entire US.

This is repeated for each county within a state so that we create a total of 49 unique datasets. One at state level and 48 at county level (there is no available data for Hawaii and Alska). Each dataset is saved as a parquet file, as these are very efficient to store.

## `app.py`
### Purpose
The `app.py` file is the main project. Executing it creates a interactive plotly dashboard that makes use of the previously created datasets. Its purpose is to give a nice view of our dataset while being effcient and keeping loading times short. This should be combined with only a small loss of information and good readability of the presented data.

### Functionality
This file achieves its purpose by utilising Plotly Dash to create a simple dashboard layout that is filled with two plots and four dropdown menus. All of these are connected and are influenced by eachother. 

We create a choropleth map that shows the selected data and can in turn be used to perform semantic zooming by focusing on a single state. It achieves this by being linked to the dropdowns and loading a different dataset and geojson if a state is selected. The loading time for this action is extremely short due to the relatively small size of each dataset, as well as its parquet form.

Another graph was also created. This graph can appear as either a bar or line chart depending on the selected data and can inturn be used to influence the dashboard. Although only by selecting a severity level in the bar chart form, as the line chart does not contain any information that can change any level of the visualization as it is.

