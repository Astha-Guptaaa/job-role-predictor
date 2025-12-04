# backend/models/education.py

class Education:
    def __init__(self, user_id, degree, specialization, cgpa, graduation_year, certifications):
        self.user_id = user_id
        self.degree = degree
        self.specialization = specialization
        self.cgpa = cgpa
        self.graduation_year = graduation_year
        self.certifications = certifications

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "degree": self.degree,
            "specialization": self.specialization,
            "cgpa": self.cgpa,
            "graduation_year": self.graduation_year,
            "certifications": self.certifications
        }
