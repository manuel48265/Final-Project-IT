import pandas as pd # Necesario para el ejemplo
import openai

openai.api_key = "TU_API_KEY_AQUI"

def estimate_time_with_gpt(activity, description, technologies):
    """
    Use GPT to estimate the optimistic, most likely, and pessimistic times for a task.

    Parameters:
    - activity: str, the name of the activity.
    - description: str, a brief description of the task.
    - technologies: str, the technologies involved in the task.

    Returns:
    - dict with optimistic, most likely, and pessimistic estimates.
    """
    prompt = f"""
    I am managing a project and need time estimates for a task.
    Task Name: {activity}
    Description: {description}
    Technologies: {technologies}
    
    Provide:
    - An optimistic time estimate (in days).
    - A most likely time estimate (in days).
    - A pessimistic time estimate (in days).
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a project management assistant."},
                  {"role": "user", "content": prompt}],
        max_tokens=150
    )

    reply = response['choices'][0]['message']['content']
    
    # Extract results (basic parsing for demonstration)
    return reply


def process_tasks_with_gpt(data):
    results = []

    for _, row in data.iterrows():
        reply = estimate_time_with_gpt(
            activity=row["Activity"],
            description="General task description",
            technologies="General tech stack"
        )
        results.append(reply)

    return results

# Ejemplo de uso con tus datos actuales
data = pd.DataFrame({
    "Activity": ["Design Database", "Develop Backend", "Create Frontend"],
    "Description": [
        "Design the schema for a relational database",
        "Develop RESTful APIs for the backend using Django",
        "Build a responsive UI using React"
    ],
    "Technologies": ["MySQL, PostgreSQL", "Django, Flask", "React, Tailwind CSS"]
})

estimates = process_tasks_with_gpt(data)
for task, estimate in zip(data["Activity"], estimates):
    print(f"Task: {task}\nEstimate:\n{estimate}\n")

