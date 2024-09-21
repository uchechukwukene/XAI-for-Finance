## Explainable AI for Financial Advisory: Churn Prediction with SHAP and LIME

This repository contains a prototype of an Explainable AI (XAI) platform designed to predict customer churn in financial advisory services. The platform focuses on making predictions **transparent** and **understandable** by using explainability techniques like **SHAP** and **LIME**.

##  Overview

This project predicts which customers are at risk of leaving a financial service and explains **why** they might leave, helping financial advisors take proactive actions. We implemented **three churn prediction models**:
- Logistic Regression
- Random Forest
- K-Nearest Neighbors (KNN)

Explanations for the model predictions are generated using **SHAP** (SHapley Additive exPlanations), ensuring that each prediction is not only accurate but also interpretable.

## Project Structure

```bash
data/
├─ AdvisoryPerformance.csv         # Advisory service performance data
├─ Clients.csv                     # Client information
├─ clients_dataset.pickle           # Preprocessed dataset
├─ Contracts.csv                   # Client contract information
├─ MarketPerformance.csv           # Market trends and data
├─ Transactions.csv                # Financial transactions data
.gitignore
churn_prediction_models.ipynb       # Main notebook for model building & explanation
prepare_clients_dataset.py          # Script to preprocess data
requirements.txt                   # Required Python packages
```
##  Explainability Features
This project leverages SHAP and LIME to make the model’s predictions understandable:

SHAP: Provides global and local interpretability by calculating feature contributions for each prediction.
LIME: Offers explanations by approximating complex models with interpretable ones on a local level.

##  Why Explainability Matters
In finance, making predictions is not enough. Advisors and stakeholders need to trust these predictions by understanding why decisions were made. That’s why this project focuses on explainable AI—helping bridge the gap between complex models and human insight.

# Happy coding! 👨‍💻👩‍💻
