import pandas as pd
import plotly.figure_factory as ff
from datetime import datetime, timedelta

def generate_gantt_chart(data, time_unit, start_date):
    """
    Generate a Gantt chart based on provided data.

    Parameters:
    - data: DataFrame with columns [Activity, Dependencies, Most Likely Time (M), ...].
    - time_unit: str, one of 'days', 'weeks', 'months'.
    - start_date: str, the start date in 'YYYY-MM-DD' format.

    Returns:
    - Gantt chart as a Plotly figure.
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

    # Convert dates to strings for Plotly
    df["Start"] = df["Start"].apply(lambda x: x.strftime("%Y-%m-%d") if isinstance(x, datetime) else x)
    df["End"] = df["End"].apply(lambda x: x.strftime("%Y-%m-%d") if isinstance(x, datetime) else x)

    # Create Gantt chart
    gantt_data = [
        dict(Task=row["Activity"], Start=row["Start"], Finish=row["End"], Resource="")
        for _, row in df.iterrows()
    ]

    fig = ff.create_gantt(gantt_data, index_col="Resource", show_colorbar=True, group_tasks=True)
    return fig

# Example usage
data = pd.DataFrame({
    "Activity": ["A", "B", "C", "D"],
    "Dependencies": [None, "A", "A", "B, C"],
    "Most Likely Time (M)": [5, 3, 2, 4],
})

gantt_chart = generate_gantt_chart(data, time_unit="days", start_date="2024-01-01")
gantt_chart.show()
