import pickle
from functools import reduce

import pandas as pd
from scipy.stats import stats

periods = [
    "LAST",
    "SECOND-LAST",
    "THIRD-LAST",
    "FOURTH-LAST",
    "FIFTH-LAST",
    "SIXTH-LAST",
]

# Define data directory
data_dir = "data"


def clients():
    # Read the Clients data from a CSV file
    clients = pd.read_csv(data_dir + "/Clients.csv", sep="\t")

    # Drop unnecessary columns from the Clients data
    clients = clients.drop(
        [
            "DATA_DECESSO",
            "TIPO_SOGGETTO_DESC",
            "DATAINSERIMENTO",
            "TIPO_CATEGORIA",
            "ID_FILIALE",
            "SESSO",
            "ID_AGENTE",
            "STATUS_DESC",
        ],
        axis=1,
    )

    # Perform one-hot encoding on the "PSC" column of the Clients data
    clients = pd.get_dummies(clients, prefix_sep="_", columns=["PSC"])

    # Return the modified Clients data
    return clients


def contracts(n):
    # Calculate the number of days by adding 28 days to the input parameter 'n'
    day = n + 28

    # Read the Contracts data from a CSV file
    contracts = pd.read_csv(data_dir + "/Contracts.csv", sep="\t")

    # Replace "(null)" values in the "DATA_CHIUSURA" column with a default date
    contracts["DATA_CHIUSURA"].replace({"(null)": "2019-11-29"}, inplace=True)
    # Replace "(null)" values in the "DATA_APERTURA" column with a default date
    contracts["DATA_APERTURA"].replace({"(null)": "1999-11-29"}, inplace=True)

    # Convert the "DATA_CHIUSURA" and "DATA_APERTURA" columns to datetime format
    contracts["DATA_CHIUSURA"] = pd.to_datetime(contracts.DATA_CHIUSURA)
    contracts["DATA_APERTURA"] = pd.to_datetime(contracts.DATA_APERTURA)

    # Calculate the churn date for each client as the maximum "DATA_CHIUSURA" value
    churn_date = (
        contracts.groupby("CLIENTE")["DATA_CHIUSURA"].max().rename("CHURN_DATE")
    )

    # Merge the churn date information with the Contracts data
    contracts = pd.merge(contracts, churn_date, on="CLIENTE")

    # Calculate the number of active contracts for each client currently
    active_contr_num = (
        contracts[contracts.STATO == 1]
        .groupby("CLIENTE")["ID"]
        .count()
        .reindex(contracts["CLIENTE"].unique())
        .fillna(0)
        .astype(int)
        .rename("ACTIVE_CONTRACTS_CURRENTLY")
        .reset_index()
    )

    # Calculate the number of closed contracts for each client currently
    closed_contr_num = (
        contracts[contracts.STATO == 2]
        .groupby("CLIENTE")["ID"]
        .count()
        .reindex(contracts["CLIENTE"].unique())
        .fillna(0)
        .astype(int)
        .rename("CLOSED_CONTRACTS_CURRENTLY")
        .reset_index()
    )

    # Iterate for 6 months to calculate the number of active and closed contracts for each client in the past months
    for i in range(1, 7):
        # Calculate the number of active contracts for each client X months before churn date
        active_contr_X_months = contracts[
            (
                contracts.DATA_CHIUSURA
                > (contracts.CHURN_DATE - pd.to_timedelta(day, unit="d"))
            )
            & (
                contracts.DATA_APERTURA
                < (contracts.CHURN_DATE - pd.to_timedelta(day, unit="d"))
            )
        ]
        active_contr_num_X_months = (
            active_contr_X_months.groupby("CLIENTE")["ID"]
            .count()
            .reindex(active_contr_X_months["CLIENTE"].unique())
            .fillna(0)
            .astype(int)
            .rename("ACTIVE_CONTRACTS_" + str(i) + "_MONTH_BEFORE")
            .reset_index()
        )

        # Calculate the number of closed contracts for each client X months before churn date
        closed_contr_X_months = contracts[
            (
                contracts.DATA_CHIUSURA
                < (contracts.CHURN_DATE - pd.to_timedelta(day, unit="d"))
            )
            & (contracts.STATO == 2)
        ]
        closed_contr_num_X_months = (
            closed_contr_X_months.groupby("CLIENTE")["ID"]
            .count()
            .reindex(closed_contr_X_months["CLIENTE"].unique())
            .fillna(0)
            .astype(int)
            .rename("CLOSED_CONTRACTS_" + str(i) + "_MONTH_BEFORE")
            .reset_index()
        )

        # Merge the number of active contracts X months before with the overall active contracts data
        active_contr_num = pd.merge(
            active_contr_num, active_contr_num_X_months, on="CLIENTE", how="outer"
        )

        # Merge the number of closed contracts X months before with the overall closed contracts data
        closed_contr_num = pd.merge(
            closed_contr_num, closed_contr_num_X_months, on="CLIENTE", how="outer"
        )

        # Increase the day count for the next iteration
        day += 28

    # Merge the active and closed contracts data using reduce and keep only common columns for all clients
    contracts = reduce(
        lambda x, y: pd.merge(x, y, on="CLIENTE", how="inner"),
        [active_contr_num, closed_contr_num],
    )

    # Fill any missing values with 0 and convert all columns to integer type
    contracts = contracts.fillna(0).astype(int)

    # Return the modified Contracts data
    return contracts


def netpaid_perf(n):
    # Calculate the number of days by adding 28 days to the input parameter 'n'
    day = n + 28

    # Read the Advisory Performance data from a CSV file
    advisory_performance = pd.read_csv(data_dir + "/AdvisoryPerformance.csv", sep="\t")

    # Convert the "DT_INIZIO_PERIODO" and "DT_FINE_PERIODO" columns to datetime format
    advisory_performance["DT_INIZIO_PERIODO"] = pd.to_datetime(
        advisory_performance.DT_INIZIO_PERIODO
    )
    advisory_performance["DT_FINE_PERIODO"] = pd.to_datetime(
        advisory_performance.DT_FINE_PERIODO
    )

    # Calculate the last date for each client by finding the maximum "DT_FINE_PERIODO" value
    last_date = (
        advisory_performance.groupby("ID_CLIENTE")["DT_FINE_PERIODO"]
        .max()
        .rename("LAST_DATE")
    )
    advisory_performance = pd.merge(advisory_performance, last_date, on="ID_CLIENTE")

    # Create empty DataFrames to store net paid and performance data
    net_paid = advisory_performance["ID_CLIENTE"].drop_duplicates()
    performance = advisory_performance["ID_CLIENTE"].drop_duplicates()

    # Iterate for 6 months to calculate net paid and performance data for each client in the past months
    for i in range(0, 6):
        # Filter the Advisory Performance data based on specific conditions to calculate net paid and performance for X months before the last date
        advisory_performance_X_months = advisory_performance[
            (
                advisory_performance.DT_INIZIO_PERIODO
                >= (advisory_performance.LAST_DATE - pd.to_timedelta(day, unit="d"))
            )
            & (
                advisory_performance.DT_FINE_PERIODO
                <= (
                    advisory_performance.LAST_DATE - pd.to_timedelta(day - 28, unit="d")
                )
            )
        ]

        # Calculate the net paid for each client X months before the last date
        net_paid_X_months = (
            advisory_performance_X_months.groupby("ID_CLIENTE")["VERSATO_NETTO"]
            .sum()
            .reindex(advisory_performance_X_months["ID_CLIENTE"].unique())
            .fillna(0)
            .astype(float)
            .rename("NET_PAID_" + periods[i] + "_MONTH")
            .reset_index()
        )

        # Calculate the performance for each client X months before the last date
        performance_X_months = (
            advisory_performance_X_months.groupby("ID_CLIENTE")["RENDIMENTO"]
            .sum()
            .reindex(advisory_performance_X_months["ID_CLIENTE"].unique())
            .fillna(0)
            .astype(float)
            .rename("PERFORMANCE_" + periods[i] + "_MONTH")
            .reset_index()
        )

        # Merge the net paid X months before data with the overall net paid data
        net_paid = pd.merge(net_paid, net_paid_X_months, on="ID_CLIENTE", how="inner")

        # Merge the performance X months before data with the overall performance data
        performance = pd.merge(
            performance, performance_X_months, on="ID_CLIENTE", how="inner"
        )

        # Increase the day count for the next iteration
        day += 28

    # Merge the net paid and performance data using reduce, keeping only common columns for all clients
    depos_withdr_perf = reduce(
        lambda x, y: pd.merge(x, y, on="ID_CLIENTE", how="inner"),
        [net_paid, performance],
    )

    # Return the merged net paid and performance data
    return depos_withdr_perf


def mkt_performance(n):
    # Calculate the number of days by adding 28 days to the input parameter 'n'
    day = n + 28

    # Read the Advisory Performance and Market Performance data from CSV files
    advisory_performance = pd.read_csv(data_dir + "/AdvisoryPerformance.csv", sep="\t")
    market_performance = pd.read_csv(data_dir + "/MarketPerformance.csv", sep="\t")

    # Convert relevant columns to datetime format
    advisory_performance["DT_INIZIO_PERIODO"] = pd.to_datetime(
        advisory_performance.DT_INIZIO_PERIODO
    )
    advisory_performance["DT_FINE_PERIODO"] = pd.to_datetime(
        advisory_performance.DT_FINE_PERIODO
    )
    market_performance["DATA"] = pd.to_datetime(market_performance.DATA)

    # Calculate the last date for each client in the Advisory Performance data
    last_date = (
        advisory_performance.groupby("ID_CLIENTE")["DT_FINE_PERIODO"]
        .max()
        .rename("LAST_DATE")
    )
    advisory_performance = pd.merge(advisory_performance, last_date, on="ID_CLIENTE")

    # Create a new DataFrame to store market performance data for each client
    mkt_performance = advisory_performance[
        ["ID_CLIENTE", "LAST_DATE"]
    ].drop_duplicates()

    # Iterate for 6 months to calculate the market performance for each client in the past months
    for i in range(0, 6):
        monthly_performance = []

        # Iterate over each row in the market performance DataFrame
        for k, row in mkt_performance.iterrows():
            # Filter the Market Performance data based on specific conditions to calculate market performance for X months before the last date
            mkt_performance_X_months = market_performance[
                (
                    market_performance.DATA
                    >= (row["LAST_DATE"] - pd.to_timedelta(day, unit="d"))
                )
                & (
                    market_performance.DATA
                    < (row["LAST_DATE"] - pd.to_timedelta(day - 28, unit="d"))
                )
            ]

            # Calculate the sum of daily returns for the filtered market performance data
            single_monthly_perf = mkt_performance_X_months["REND_GIORN"].sum()
            monthly_performance.append(single_monthly_perf)

        # Create a new column with the calculated monthly performance data and insert it into the market performance DataFrame
        new_col = pd.DataFrame(monthly_performance)
        new_col = new_col.set_index(mkt_performance.index)
        mkt_performance.insert(
            i, "MARKET_PERFORMANCE_" + periods[i] + "_MONTH", new_col
        )

        # Increase the day count for the next iteration
        day += 28

    # Remove the "LAST_DATE" column from the market performance DataFrame
    mkt_performance = mkt_performance.drop("LAST_DATE", axis=1)

    # Return the market performance DataFrame
    return mkt_performance


def investments(n):
    # Calculate the number of days by adding 28 days to the input parameter 'n'
    day = n + 28

    # Read the Transactions and Contracts data from CSV files
    transactions = pd.read_csv(data_dir + "/Transactions.csv", sep=",")
    contracts = pd.read_csv(data_dir + "/Contracts.csv", sep="\t")

    # Rename columns in the Contracts data
    contracts.rename(columns={"DATA_CHIUSURA": "LAST_DATE"}, inplace=True)
    contracts.rename(columns={"ID": "ID_CONTRATTO"}, inplace=True)
    contracts["LAST_DATE"].replace({"(null)": "2019-11-29"}, inplace=True)

    # Merge Transactions and Contracts data based on the contract ID
    transactions_last_date = pd.merge(transactions, contracts, on="ID_CONTRATTO")

    # Convert relevant columns to datetime format
    transactions_last_date["DATA_CONTABILE"] = pd.to_datetime(
        transactions_last_date.DATA_CONTABILE
    )
    transactions_last_date["LAST_DATE"] = pd.to_datetime(
        transactions_last_date.LAST_DATE
    )

    # Create empty DataFrames to store the sum and count of investments for each client
    sum_investments = transactions_last_date["ID_CLIENTE"].drop_duplicates()
    num_investments = transactions_last_date["ID_CLIENTE"].drop_duplicates()

    # Iterate for 6 months to calculate the sum and count of investments for each client in the past months
    for i in range(0, 6):
        # Filter the Transactions data based on specific conditions to calculate investments for X months before the last date
        transactions_X_months = transactions_last_date[
            (
                transactions_last_date.DATA_CONTABILE
                >= (transactions_last_date.LAST_DATE - pd.to_timedelta(day, unit="d"))
            )
            & (
                transactions_last_date.DATA_CONTABILE
                < (
                    transactions_last_date.LAST_DATE
                    - pd.to_timedelta(day - 28, unit="d")
                )
            )
        ]

        # Calculate the sum of investments for each client X months before the last date
        sum_investments_X_months = (
            transactions_X_months[transactions_X_months.NOME == "ACQUISTO TITOLI"]
            .groupby("ID_CLIENTE")["IMP_LORDO"]
            .sum()
            .reindex(transactions_X_months["ID_CLIENTE"].unique())
            .fillna(0)
            .astype(float)
            .rename("INVESTMENTS_" + periods[i] + "_MONTH")
            .reset_index()
        )

        # Calculate the count of investments for each client X months before the last date
        num_investments_X_months = (
            transactions_X_months[transactions_X_months.NOME == "ACQUISTO TITOLI"]
            .groupby("ID_CLIENTE")["IMP_LORDO"]
            .count()
            .reindex(transactions_X_months["ID_CLIENTE"].unique())
            .fillna(0)
            .astype(int)
            .rename("NUM_INVESTMENTS_" + periods[i] + "_MONTH")
            .reset_index()
        )

        # Merge the sum of investments X months before with the overall sum of investments data
        sum_investments = pd.merge(
            sum_investments, sum_investments_X_months, on="ID_CLIENTE", how="outer"
        )

        # Merge the count of investments X months before with the overall count of investments data
        num_investments = pd.merge(
            num_investments, num_investments_X_months, on="ID_CLIENTE", how="outer"
        )

        # Increase the day count for the next iteration
        day += 28

    # Merge the sum and count of investments data using reduce, keeping only common columns for all clients
    investments = reduce(
        lambda x, y: pd.merge(x, y, on="ID_CLIENTE", how="inner"),
        [sum_investments, num_investments],
    )

    # Fill any missing values with 0
    investments.fillna(0, inplace=True)

    # Return the investments DataFrame
    return investments


def labeling(dataset):
    # Create an empty list to store the labels
    col = []

    # Iterate over each row in the dataset
    for k, row in dataset.iterrows():
        # Check if the value of "ACTIVE_CONTRACTS_CURRENTLY" column is 0
        if row["ACTIVE_CONTRACTS_CURRENTLY"] == 0:
            # If the value is 0, append "CHURN" label to the list
            col.append("CHURN")
        else:
            # If the value is not 0, append "NO CHURN" label to the list
            col.append("NO CHURN")

    # Create a new DataFrame from the list of labels
    new_col = pd.DataFrame(col)

    # Insert the new column of labels at the beginning of the dataset DataFrame
    dataset.insert(0, "PREDICTION", new_col)


def REGRESS(data):
    # Create an empty list to store the x-axis values
    x_axis = []

    # Create an empty list to store the new column values
    new_col = []

    # Convert the input data to a NumPy array
    arr = data.to_numpy()

    # Generate the x-axis values based on the number of columns in the data
    for x in range(len(data.columns), 0, -1):
        x_axis.append(x - 1)

    # Iterate over each row in the array
    for row in arr:
        # Perform linear regression on the row data using the x-axis values
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_axis, row)

        # Append the slope value to the new column list
        new_col.append(slope)

    # Create a new DataFrame from the list of new column values
    return pd.DataFrame(new_col)


def create_dataset(day):
    # Obtain the 'dataset' DataFrame from the 'clients' function
    dataset = clients()

    # Merge 'dataset' with the 'contracts' data for the given 'day'
    dataset = pd.merge(
        dataset, contracts(day), left_on="ID_CLIENTE", right_on="CLIENTE"
    )

    # Remove the 'CLIENTE' column from 'dataset'
    dataset = dataset.drop("CLIENTE", axis=1)

    # Merge 'dataset' with the 'netpaid_perf' data for the given 'day'
    dataset = pd.merge(dataset, netpaid_perf(day), on="ID_CLIENTE", how="inner")

    # Merge 'dataset' with the 'mkt_performance' data for the given 'day'
    dataset = pd.merge(dataset, mkt_performance(day), on="ID_CLIENTE")

    # Calculate relative performance and modify 'dataset' accordingly for each month
    for i in range(0, 6):
        relative_performance = (
            dataset["PERFORMANCE_" + periods[i] + "_MONTH"]
            - dataset["MARKET_PERFORMANCE_" + periods[i] + "_MONTH"]
        )
        dataset[
            "RELATIVE_PERFORMANCE_" + periods[i] + "_MONTH"
        ] = relative_performance.astype(float)
        dataset = dataset.drop("MARKET_PERFORMANCE_" + periods[i] + "_MONTH", axis=1)

    # Merge 'dataset' with the 'investments' data for the given 'day'
    dataset = pd.merge(dataset, investments(day), on="ID_CLIENTE")

    # Insert regression analysis results into 'dataset' for active contracts, closed contracts, net paid, performance, relative performance, and investments
    dataset.insert(
        6,
        "REGRESS_ACTIVE_CONTRACTS",
        REGRESS(
            dataset[
                [
                    "ACTIVE_CONTRACTS_2_MONTH_BEFORE",
                    "ACTIVE_CONTRACTS_3_MONTH_BEFORE",
                    "ACTIVE_CONTRACTS_4_MONTH_BEFORE",
                    "ACTIVE_CONTRACTS_5_MONTH_BEFORE",
                    "ACTIVE_CONTRACTS_6_MONTH_BEFORE",
                ]
            ]
        ),
    )
    dataset.insert(
        7,
        "REGRESS_CLOSED_CONTRACTS",
        REGRESS(
            dataset[
                [
                    "CLOSED_CONTRACTS_2_MONTH_BEFORE",
                    "CLOSED_CONTRACTS_3_MONTH_BEFORE",
                    "CLOSED_CONTRACTS_4_MONTH_BEFORE",
                    "CLOSED_CONTRACTS_5_MONTH_BEFORE",
                    "CLOSED_CONTRACTS_6_MONTH_BEFORE",
                ]
            ]
        ),
    )
    dataset.insert(
        8,
        "REGRESS_NET_PAID",
        REGRESS(
            dataset[
                [
                    "NET_PAID_SECOND-LAST_MONTH",
                    "NET_PAID_THIRD-LAST_MONTH",
                    "NET_PAID_FOURTH-LAST_MONTH",
                    "NET_PAID_FIFTH-LAST_MONTH",
                    "NET_PAID_SIXTH-LAST_MONTH",
                ]
            ]
        ),
    )
    dataset.insert(
        9,
        "REGRESS_PERFORMANCE",
        REGRESS(
            dataset[
                [
                    "PERFORMANCE_SECOND-LAST_MONTH",
                    "PERFORMANCE_THIRD-LAST_MONTH",
                    "PERFORMANCE_FOURTH-LAST_MONTH",
                    "PERFORMANCE_FIFTH-LAST_MONTH",
                    "PERFORMANCE_SIXTH-LAST_MONTH",
                ]
            ]
        ),
    )
    dataset.insert(
        10,
        "REGRESS_RELATIVE_PERFORMANCE",
        REGRESS(
            dataset[
                [
                    "RELATIVE_PERFORMANCE_SECOND-LAST_MONTH",
                    "RELATIVE_PERFORMANCE_THIRD-LAST_MONTH",
                    "RELATIVE_PERFORMANCE_FOURTH-LAST_MONTH",
                    "RELATIVE_PERFORMANCE_FIFTH-LAST_MONTH",
                    "RELATIVE_PERFORMANCE_SIXTH-LAST_MONTH",
                ]
            ]
        ),
    )
    dataset.insert(
        11,
        "REGRESS_INVESTMENTS",
        REGRESS(
            dataset[
                [
                    "INVESTMENTS_SECOND-LAST_MONTH",
                    "INVESTMENTS_THIRD-LAST_MONTH",
                    "INVESTMENTS_FOURTH-LAST_MONTH",
                    "INVESTMENTS_FIFTH-LAST_MONTH",
                    "INVESTMENTS_SIXTH-LAST_MONTH",
                ]
            ]
        ),
    )

    # Perform labeling of churn and non-churn based on active contracts in 'dataset'
    labeling(dataset)

    # Remove unnecessary columns from 'dataset'
    dataset = dataset.drop(
        [
            "ID_CLIENTE",
            "ACTIVE_CONTRACTS_CURRENTLY",
            "CLOSED_CONTRACTS_CURRENTLY",
            "ACTIVE_CONTRACTS_1_MONTH_BEFORE",
            "CLOSED_CONTRACTS_1_MONTH_BEFORE",
            "NET_PAID_LAST_MONTH",
            "PERFORMANCE_LAST_MONTH",
            "RELATIVE_PERFORMANCE_LAST_MONTH",
            "INVESTMENTS_LAST_MONTH",
            "NUM_INVESTMENTS_LAST_MONTH",
        ],
        axis=1,
    )

    # Return the modified 'dataset'
    return dataset


# Create a dataset using the 'create_dataset' function with the parameter '0'
dataset = create_dataset(0)

# Save the dataset to a pickle file
with open(data_dir + "/clients_dataset.pickle", "wb") as handle:
    pickle.dump(dataset, handle, protocol=pickle.HIGHEST_PROTOCOL)
