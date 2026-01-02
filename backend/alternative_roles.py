career_paths = {
    "Testing Engineer": ["Data Analyst", "QA Lead"],
    "Data Analyst": ["Data Scientist", "Business Analyst"],
    "Software Engineer": ["Full Stack Developer", "ML Engineer"]
}

def get_alternative_roles(role):
    return career_paths.get(role, [])