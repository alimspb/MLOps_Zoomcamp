import os
import pickle
import click
import mlflow
from mlflow.models import infer_signature

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import root_mean_squared_error


def load_pickle(filename: str):
    with open(filename, "rb") as f_in:
        return pickle.load(f_in)


@click.command()
@click.option(
    "--data_path",
    default="./output",
    help="Location where the processed NYC taxi trip data was saved"
)
def run_train(data_path: str):
    # Enable autologging for scikit-learn
    mlflow.sklearn.autolog()

    X_train, y_train = load_pickle(os.path.join(data_path, "train.pkl"))
    X_val, y_val = load_pickle(os.path.join(data_path, "val.pkl"))

    with mlflow.start_run():
        rf = RandomForestRegressor(max_depth=10, random_state=0)
        rf.fit(X_train, y_train)
        y_pred = rf.predict(X_val)

        rmse = root_mean_squared_error(y_val, y_pred)

        # Log the RMSE metric
        mlflow.log_metric("rmse", rmse)

        # Log model signature
        signature = infer_signature(X_val, y_pred)
        mlflow.sklearn.log_model(rf, "model", signature=signature)

        print(f"RMSE: {rmse}")


if __name__ == '__main__':
    run_train()
