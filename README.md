# RealtimeVis

# Execution
To run the dashboard please first install the requirements.txt as such: 

`pip install -r ./src/requirements.txt`

Then (if data is not already present) download the full Dataset from: https://www.kaggle.com/datasets/sobhanmoosavi/us-accidents

or the sampled Dataset from: https://drive.google.com/file/d/1U3u8QYzLjnEaSurtZfSAS_oh9AT2Mn8X/edit

Then execute the `preprocessing.py` file to generate all necessary data files for the dashboard. The dashboard can then be executed using following command:

`python ./src/app.py`
