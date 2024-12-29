import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
from datetime import datetime, timedelta

def generate_gantt_chart(data, time_unit, start_date, output_file="gantt_chart.png"):
    """
    Generate a Gantt chart based on provided data and save it as a PNG image.

    Parameters:
    - data: DataFrame with columns [Activity, Dependencies, Most Likely Time (M), ...].
    - time_unit: str, one of 'days', 'weeks', 'months'.
    - start_date: str, the start date in 'YYYY-MM-DD' format.
    - output_file: str, the file name for the output PNG image.

    Returns:
    - None (saves the Gantt chart as a PNG file).
    """
    # Convert start_date to datetime
    start_date = datetime.strptime(start_date, "%Y-%m-%d")

    # Create a copy of the data to avoid modifying the original DataFrame
    df = data.copy()

    # Ensure required columns exist
    required_columns = ["Activity", "Dependencies", "Most Likely Time (M)"]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Convert time unit to days
    time_unit_map = {"days": 1, "weeks": 7, "months": 30}
    if time_unit not in time_unit_map:
        raise ValueError("Invalid time_unit. Choose from 'days', 'weeks', 'months'.")
    unit_multiplier = time_unit_map[time_unit]

    # Add start and end date columns
    df["Start"] = None
    df["End"] = None

    # Dictionary to track the end date of each activity
    activity_end_dates = {}

    for index, row in df.iterrows():
        # Get dependencies
        dependencies = row["Dependencies"]

        # Calculate start date
        if pd.isna(dependencies):
            # No dependencies: start at the project start date
            start = start_date
        else:
            # Dependencies: start after the latest end date of dependencies
            dep_activities = [dep.strip() for dep in dependencies.split(",")]
            dep_end_dates = [activity_end_dates[dep] for dep in dep_activities]
            start = max(dep_end_dates)

        # Calculate end date
        duration = row["Most Likely Time (M)"] * unit_multiplier
        end = start + timedelta(days=duration)

        # Update DataFrame
        df.at[index, "Start"] = start
        df.at[index, "End"] = end

        # Track the end date for the current activity
        activity_end_dates[row["Activity"]] = end

    # Plot Gantt chart
    fig, ax = plt.subplots(figsize=(10, 6))

    for i, row in df.iterrows():
        start_num = date2num(row["Start"])
        end_num = date2num(row["End"])
        ax.barh(row["Activity"], end_num - start_num, left=start_num, color="skyblue")

    # Format the plot
    ax.xaxis_date()
    ax.set_xlabel("Date")
    ax.set_ylabel("Activities")
    ax.set_title("Gantt Chart")
    plt.tight_layout()

    # Save the plot as a PNG file
    plt.savefig(output_file)
    plt.close()

# Example usage
data = pd.DataFrame({
    "Activity": ["A", "B", "C", "D"],
    "Dependencies": [None, "A", "A", "B, C"],
    "Most Likely Time (M)": [5, 3, 2, 4],
})

generate_gantt_chart(data, time_unit="days", start_date="2024-01-01")
