# tools_benchmark.py

import os
import threading
import time
from collections import defaultdict
from pathlib import Path

import duckdb
import pandas as pd
from pyspark.sql import SparkSession

# CSV file to save benchmark results
RESULTS_FILE = "benchmark_results.csv"


def benchmark_tool(
    tool_name, dataset_size, processing_function, dataset_path, timeout=300
):
    """
    Benchmark a tool's processing time and save the result.

    Parameters:
        tool_name (str): The name of the tool/framework
        (e.g., Pandas, DuckDB, Python, Spark).
        dataset_size (str): The dataset size (e.g., '1M', '10M', '100M').
        processing_function (callable): The function that processes the dataset.
        dataset_path (Path): Path to the dataset file.
        timeout (int): Maximum time (in seconds) allowed for the processing.
    """
    result_dict = {
        "Tool": tool_name,
        "Dataset Size": dataset_size,
    }

    def run_function():
        nonlocal result_dict
        start_time = time.time()
        try:
            processing_function(dataset_path)
            elapsed_time = time.time() - start_time
            result_dict["Processing Time (s)"] = round(elapsed_time, 2)
        except Exception as e:
            result_dict["Processing Time (s)"] = f"Error: {str(e)}"

    thread = threading.Thread(target=run_function)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        result_dict["Processing Time (s)"] = f"Timed out after {timeout} seconds"

    results_df = pd.DataFrame([result_dict])
    if Path(RESULTS_FILE).exists():
        results_df.to_csv(RESULTS_FILE, mode="a", header=False, index=False)
    else:
        results_df.to_csv(RESULTS_FILE, index=False)

    print(
        f"{tool_name} completed on {dataset_size} dataset: "
        f"{result_dict['Processing Time (s)']}."
    )


def sort_results_by_dataset_size(results_file):
    """
    Reads the benchmark results CSV, sorts by dataset size, and saves it back.
    """
    size_order = ["10K", "100K", "1M", "2M", "3M", "10M", "100M"]
    df = pd.read_csv(results_file)
    df["Dataset Size"] = pd.Categorical(
        df["Dataset Size"], categories=size_order, ordered=True
    )
    df_sorted = df.sort_values(by="Dataset Size")
    df_sorted.to_csv(results_file, index=False)
    print(f"Benchmark results sorted by dataset size and saved to {results_file}.")


def process_with_pandas(file_path):
    df = pd.read_csv(
        file_path, sep=";", header=None, names=["station_city_name", "temperature"]
    )
    stats = df.groupBy("station_city_name").agg({"temperature": ["min", "avg", "max"]})
    return stats


def process_with_duckdb(file_path):
    conn = duckdb.connect()
    query = """
    SELECT
        stations AS station_city_name,
        MIN(measure) AS min_temp,
        AVG(measure) AS mean_temp,
        MAX(measure) AS max_temp
    FROM read_csv_auto(?, delim=';', header=False, columns={})
    GROUP BY stations
    """
    result = conn.execute(
        query, (file_path, {"stations": "VARCHAR", "measure": "DECIMAL(5,2)"})
    ).fetchdf()
    return result


def process_with_spark(file_path):
    spark = (
        SparkSession.builder.appName("Benchmarking")
        .config("spark.ui.showConsoleProgress", "false")
        .config("spark.executor.memory", "2g")
        .getOrCreate()
    )
    file_path_str = str(file_path)
    df = spark.read.csv(file_path_str, sep=";", header=False, inferSchema=True)
    df = df.withColumnRenamed("_c0", "station_city_name").withColumnRenamed(
        "_c1", "temperature"
    )
    stats = df.groupBy("station_city_name").agg({"temperature": ["min", "avg", "max"]})
    spark.stop()
    return stats


def process_with_python(file_path):
    temperature_per_station = defaultdict(list)
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            station, temperature = line.strip().split(";")
            temperature_per_station[station].append(float(temperature))
    stats = {
        station: {"min": min(temps), "mean": sum(temps) / len(temps), "max": max(temps)}
        for station, temps in temperature_per_station.items()
    }
    return stats


def remove_duplicates_from_results(results_file):
    df = pd.read_csv(results_file)
    df_deduplicated = df.drop_duplicates()
    df_deduplicated.to_csv(results_file, index=False)
    print(f"Duplicates removed from {results_file}.")


if __name__ == "__main__":
    if Path(RESULTS_FILE).exists():
        os.remove(RESULTS_FILE)

    datasets = {
        "10K": Path("data/measurements10K.txt"),
        "100K": Path("data/measurements100K.txt"),
        "1M": Path("data/measurements1M.txt"),
        "2M": Path("data/measurements2M.txt"),
        "3M": Path("data/measurements3M.txt"),
        "10M": Path("data/measurements10M.txt"),
        "100M": Path("data/measurements100M.txt"),
    }

    for dataset_size, dataset_path in datasets.items():
        benchmark_tool("Pandas", dataset_size, process_with_pandas, dataset_path)
        benchmark_tool("DuckDB", dataset_size, process_with_duckdb, dataset_path)
        benchmark_tool("Spark", dataset_size, process_with_spark, dataset_path)
        benchmark_tool("Python", dataset_size, process_with_python, dataset_path)

    sort_results_by_dataset_size(RESULTS_FILE)
    remove_duplicates_from_results(RESULTS_FILE)
