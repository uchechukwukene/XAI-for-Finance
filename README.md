# Explainable AI for Financial Advisory: Churn Prediction
This repository hosts a prototype of an Explainable AI platform for Financial Advisory. The platform aims to provide transparent insights for customers who are at risk of leaving a financial service. The prototype includes three churn prediction models (Logistic Regression, Random Forest and KNN) along with explanations generated using SHAP.

## Repository Contents
data/\
├─ AdvisoryPerformance.csv\
├─ Clients.csv\
├─ clients_dataset.pickle\
├─ Contracts.csv\
├─ MarketPerformance.csv\
├─ Transactions.csv\
.gitignore\
churn_prediction_models.ipynb\
prepare_clients_dataset.py\
requirements.txt

Please note that .csv files are not included due to GitHub file size limits.

The churn_prediction_models.ipynb notebook conducts evaluation and explanation of the churn prediction models. The required dataset to run the notebook, clients_dataset.pickle, is already included in the data/ directory. If you wish to generate the dataset from the original data, download the [original .csv files](https://unibari-my.sharepoint.com/:f:/g/personal/a_martina13_studenti_uniba_it/ElKPy0EWWAxBrsV30M0t7f0BJBE36HDkCyQiZHddhTlTEQ), place them in the data/ directory as shown in the repository contents tree above, and execute the prepare_clients_dataset.py script.

## Requirements
To execute the churn_prediction_models.ipynb notebook or the prepare_clients_dataset.py script, you will need a Python 3.8.10 virtual environment. Follow the instructions below to set up the virtual environment using a Windows Command shell:

1. Create a virtual environment named .venv: `python -m venv .venv`
2. Activate the virtual environment: `.venv\scripts\activate.bat`
3. Install the required Python packages: `pip install -r requirements.txt`
4. Using the .venv virtual environment, run the script from the Windows Command shell or execute the notebook using your preferred notebook interface.
