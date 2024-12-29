import pandas as pd
import openai
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.dates import date2num

# Function to estimate task durations based on historical data or GPT

def estimate_task_duration(task_description, technology, historical_data):
    """
    Estimate the time required for a task using historical data or GPT.

    Parameters:
    - task_description: str, description of the task.
    - technology: str, technology used for the task.
    - historical_data: DataFrame with historical task data.

    Returns:
    - Dictionary with optimistic, most likely, and pessimistic estimations.
    """
    # Filter historical data for similar tasks
    similar_tasks = historical_data[historical_data['Technology'] == technology]

    if not similar_tasks.empty:
        # Use historical data
        optimistic = similar_tasks['Duration'].min()
        most_likely = similar_tasks['Duration'].mean()
        pessimistic = similar_tasks['Duration'].max()
    else:
        # Use GPT for estimation
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in project management and task estimation."},
                {"role": "user", "content": f"Estimate time for the following task: {task_description} using technology: {technology}. Provide optimistic, most likely, and pessimistic estimates."}
            ]
        )
        estimates = response['choices'][0]['message']['content']
        # Parse GPT response (assuming it returns a dictionary-like format)
        estimates = eval(estimates)
        optimistic, most_likely, pessimistic = estimates['optimistic'], estimates['most_likely'], estimates['pessimistic']

    return {
        "Optimistic": optimistic,
        "Most Likely": most_likely,
        "Pessimistic": pessimistic
    }

# Main function to generate Gantt chart with role assignments and cost estimations
def generate_project_plan(tasks_data, historical_data, time_unit, start_date, output_file="project_plan.png"):
    """
    Generate a Gantt chart and estimate resources and costs based on task data and historical data.

    Parameters:
    - tasks_data: DataFrame with columns [Activity, Description, Dependencies, Technology, Roles, Resources].
    - historical_data: DataFrame with historical task data (including durations and costs).
    - time_unit: str, one of 'days', 'weeks', 'months'.
    - start_date: str, the start date in 'YYYY-MM-DD' format.
    - output_file: str, the file name for the output PNG image.

    Returns:
    - None (saves the Gantt chart as a PNG file).
    """
    # Convert start_date to datetime
    start_date = datetime.strptime(start_date, "%Y-%m-%d")

    # Ensure required columns exist
    required_columns = ["Activity", "Description", "Dependencies", "Technology", "Roles"]
    for col in required_columns:
        if col not in tasks_data.columns:
            raise ValueError(f"Missing required column: {col}")

    # Convert time unit to days
    time_unit_map = {"days": 1, "weeks": 7, "months": 30}
    if time_unit not in time_unit_map:
        raise ValueError("Invalid time_unit. Choose from 'days', 'weeks', 'months'.")
    unit_multiplier = time_unit_map[time_unit]

    # Add start, end date, and cost columns
    tasks_data["Start"] = None
    tasks_data["End"] = None
    tasks_data["Optimistic"] = None
    tasks_data["Most Likely"] = None
    tasks_data["Pessimistic"] = None

    # Dictionary to track the end date of each activity
    activity_end_dates = {}

    for index, row in tasks_data.iterrows():
        # Estimate durations
        estimations = estimate_task_duration(row["Description"], row["Technology"], historical_data)
        tasks_data.at[index, "Optimistic"] = estimations["Optimistic"]
        tasks_data.at[index, "Most Likely"] = estimations["Most Likely"]
        tasks_data.at[index, "Pessimistic"] = estimations["Pessimistic"]

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
        duration = estimations["Most Likely"] * unit_multiplier
        end = start + timedelta(days=duration)

        # Update DataFrame
        tasks_data.at[index, "Start"] = start
        tasks_data.at[index, "End"] = end

        # Track the end date for the current activity
        activity_end_dates[row["Activity"]] = end

    # Plot Gantt chart
    fig, ax = plt.subplots(figsize=(12, 8))

    for i, row in tasks_data.iterrows():
        start_num = date2num(row["Start"])
        end_num = date2num(row["End"])
        ax.barh(row["Activity"], end_num - start_num, left=start_num, color="lightblue")

    # Format the plot
    ax.xaxis_date()
    ax.set_xlabel("Date")
    ax.set_ylabel("Activities")
    ax.set_title("Project Plan Gantt Chart")
    plt.tight_layout()

    # Save the plot as a PNG file
    plt.savefig(output_file)
    plt.close()

# Example usage
# Historical data example
historical_data = pd.DataFrame({
    "Technology": ["Python", "Java", "C++"],
    "Duration": [5, 8, 7]
})

# Tasks data example
tasks_data = pd.DataFrame({
    "Activity": ["A", "B", "C"],
    "Description": ["Build API", "Create Frontend", "Optimize Database"],
    "Dependencies": [None, "A", "A, B"],
    "Technology": ["Python", "Java", "Python"],
    "Roles": ["Developer", "UI Designer", "DB Admin"]
})

# Generate project plan
generate_project_plan(tasks_data, historical_data, time_unit="days", start_date="2024-01-01")

