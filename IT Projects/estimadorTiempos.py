import re
import pandas as pd
from transformers import pipeline

def parse_project_description(description):
    """
    Extract activities, technologies, and dependencies from a project description.
    """
    tasks = re.findall(r"\\bActivity:\\s*(.*)", description)
    technologies = re.findall(r"\\bTechnologies:\\s*(.*)", description)
    dependencies = re.findall(r"\\bDependencies:\\s*(.*)", description)
    
    return pd.DataFrame({
        "Activity": tasks,
        "Technologies": technologies,
        "Dependencies": dependencies
    })

def estimate_times(tasks, optimistic=1, most_likely=3, pessimistic=5):
    """
    Estimate times using PERT method.
    """
    tasks["Optimistic"] = optimistic
    tasks["Most Likely"] = most_likely
    tasks["Pessimistic"] = pessimistic
    tasks["Expected Time"] = (optimistic + 4*most_likely + pessimistic) / 6
    return tasks

# Example project description
description = '''
Activity: Design database schema
Technologies: MySQL, PostgreSQL
Dependencies: None

Activity: Develop backend API
Technologies: Django, Flask
Dependencies: Design database schema

Activity: Create frontend interface
Technologies: React, Tailwind CSS
Dependencies: Develop backend API
'''

# Process the description
tasks = parse_project_description(description)
tasks = estimate_times(tasks)

# Display the result
print(tasks)
