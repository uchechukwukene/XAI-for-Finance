#Explainable AI for Financial Advisory: Churn Prediction with SHAP and LIME
This repository hosts a prototype of an Explainable AI (XAI) platform for Financial Advisory. The platform enhances transparency and interpretability in machine learning models, focusing on predicting customer churn. The goal is to provide clear, understandable insights for financial institutions and stakeholders, enabling them to identify and retain customers at risk of leaving. This prototype includes three churn prediction models—Logistic Regression, Random Forest, and K-Nearest Neighbors (KNN)—with explanations generated using SHAP and LIME.

Key Deliverables
Explainable Models: Designed and implemented machine learning models with built-in explainability features, using SHAP and LIME to make the model’s predictions transparent and accessible.
AI Frameworks: Leveraged advanced AI frameworks and libraries like Scikit-learn, TensorFlow, and SHAP to develop and test models that prioritize both performance and interpretability, ensuring they are applicable to high-stakes domains like finance.
Transparent Decision-Making: Preprocessed and analyzed data to build models that not only predict customer churn with high accuracy but also provide understandable justifications for each decision—critical for regulatory compliance and building user trust.
Multidisciplinary Collaboration: Worked in a team that ensured the models adhered to ethical AI standards, producing outcomes that could be easily interpreted by non-technical stakeholders, thus improving their practical usability.
Balanced Performance and Transparency: Successfully balanced achieving high model accuracy with providing interpretable explanations, addressing the critical need for transparency in AI-driven decisions.

data/
├─ AdvisoryPerformance.csv
├─ Clients.csv
├─ clients_dataset.pickle
├─ Contracts.csv
├─ MarketPerformance.csv
├─ Transactions.csv
.gitignore
churn_prediction_models.ipynb
prepare_clients_dataset.py
requirements.txt

The churn_prediction_models.ipynb notebook evaluates and explains the churn prediction models. The required dataset, clients_dataset.pickle, is included in the data/ directory. If you prefer to generate the dataset from the original data, download the original .csv files, place them in the data/ directory as shown in the repository contents tree, and execute the prepare_clients_dataset.py script.

Requirements
To run the churn_prediction_models.ipynb notebook or the prepare_clients_dataset.py script, set up a Python 3.8.10 virtual environment. Use the following steps for setup on Windows:

Create a virtual environment: python -m venv .venv
Activate the virtual environment: .venv\scripts\activate.bat
Install the required packages: pip install -r requirements.txt
Run the notebook or script using your preferred environment or notebook interface within the virtual environment.
This project illustrates the powerful potential of Explainable AI in building trust and enhancing decision-making in financial advisory, all while ensuring that AI models are transparent, accessible, and aligned with ethical standards.
