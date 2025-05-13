import pandas as pd

def scores_for_first_assesment():
    data = [
        # Aval - warranty_principal_ratio
        {"Variable": "Aval", "Rango": "warranty_principal_ratio", "Valor mínimo": 0.0, "Valor máximo": 1.0, "Puntaje": -10, "Factor":0.3},
        {"Variable": "Aval", "Rango": "warranty_principal_ratio", "Valor mínimo": 1.0, "Valor máximo": 1.5, "Puntaje": -5, "Factor":0.3},
        {"Variable": "Aval", "Rango": "warranty_principal_ratio", "Valor mínimo": 1.5, "Valor máximo": 2.0, "Puntaje": 0, "Factor":0.3},
        {"Variable": "Aval", "Rango": "warranty_principal_ratio", "Valor mínimo": 2.0, "Valor máximo": 3.0, "Puntaje": 5, "Factor":0.3},
        {"Variable": "Aval", "Rango": "warranty_principal_ratio", "Valor mínimo": 3.0, "Valor máximo": 10000000, "Puntaje": 5, "Factor":0.3},  # "3 o más"

        # Aval - Score (primera sección)
        {"Variable": "Aval", "Rango": "credit_score", "Valor mínimo": 456, "Valor máximo": 516, "Puntaje": -10, "Factor":0.35},
        {"Variable": "Aval", "Rango": "credit_score", "Valor mínimo": 517, "Valor máximo": 577, "Puntaje": -5, "Factor":0.35},
        {"Variable": "Aval", "Rango": "credit_score", "Valor mínimo": 578, "Valor máximo": 638, "Puntaje": 0, "Factor":0.35},
        {"Variable": "Aval", "Rango": "credit_score", "Valor mínimo": 639, "Valor máximo": 699, "Puntaje": 5, "Factor":0.35},
        {"Variable": "Aval", "Rango": "credit_score", "Valor mínimo": 700, "Valor máximo": 760, "Puntaje": 10, "Factor":0.35},

        # Edad (primera sección)
        {"Variable": "Aval", "Rango": "age", "Valor mínimo": 25, "Valor máximo": 38, "Puntaje": 0, "Factor":0.20},
        {"Variable": "Aval", "Rango": "age", "Valor mínimo": 39, "Valor máximo": 55, "Puntaje": 10, "Factor":0.20},
        {"Variable": "Aval", "Rango": "age", "Valor mínimo": 56, "Valor máximo": 65, "Puntaje": 5, "Factor":0.20},


        # Estudiante - Promedio preparatoria
        {"Variable": "Estudiante", "Rango": "gpa", "Valor mínimo": 9, "Valor máximo": 10, "Puntaje": 10, "Factor":0.15},
        {"Variable": "Estudiante", "Rango": "gpa", "Valor mínimo": 8, "Valor máximo": 9, "Puntaje": 5, "Factor":0.15},
        {"Variable": "Estudiante", "Rango": "gpa", "Valor mínimo": 0, "Valor máximo": 8, "Puntaje": 0, "Factor":0.15},
    ]

    return pd.DataFrame(data)

def scores_second_assesment():
    data2 = [
    # Aval - warranty_principal_ratio
    {"Variable": "Aval", "Rango": "warranty_principal_ratio", "Valor mínimo": 0.0, "Valor máximo": 1.0, "Puntaje": -10, "Factor":0.05},
    {"Variable": "Aval", "Rango": "warranty_principal_ratio", "Valor mínimo": 1.0, "Valor máximo": 1.5, "Puntaje": -5, "Factor":0.05},
    {"Variable": "Aval", "Rango": "warranty_principal_ratio", "Valor mínimo": 1.5, "Valor máximo": 2.0, "Puntaje": 0, "Factor":0.05},
    {"Variable": "Aval", "Rango": "warranty_principal_ratio", "Valor mínimo": 2.0, "Valor máximo": 3.0, "Puntaje": 5, "Factor":0.05},
    {"Variable": "Aval", "Rango": "warranty_principal_ratio", "Valor mínimo": 3.0, "Valor máximo": 1000000000, "Puntaje": 5, "Factor":0.05},  # "3 o más"

    # Aval - Score (primera sección)
    {"Variable": "Aval", "Rango": "credit_score", "Valor mínimo": 456, "Valor máximo": 516, "Puntaje": -10, "Factor":0.05},
    {"Variable": "Aval", "Rango": "credit_score", "Valor mínimo": 517, "Valor máximo": 577, "Puntaje": -5, "Factor":0.05},
    {"Variable": "Aval", "Rango": "credit_score", "Valor mínimo": 578, "Valor máximo": 638, "Puntaje": 0, "Factor":0.05},
    {"Variable": "Aval", "Rango": "credit_score", "Valor mínimo": 639, "Valor máximo": 699, "Puntaje": 5, "Factor":0.05},
    {"Variable": "Aval", "Rango": "credit_score", "Valor mínimo": 700, "Valor máximo": 760, "Puntaje": 10, "Factor":0.05},

    # Edad (primera sección)
    {"Variable": "Aval", "Rango": "age", "Valor mínimo": 25, "Valor máximo": 38, "Puntaje": 0, "Factor":0.05},
    {"Variable": "Aval", "Rango": "age", "Valor mínimo": 39, "Valor máximo": 55, "Puntaje": 10, "Factor":0.05},
    {"Variable": "Aval", "Rango": "age", "Valor mínimo": 56, "Valor máximo": 65, "Puntaje": 5, "Factor":0.05},

    # Estudiante - Salario mensual
    {"Variable": "Estudiante", "Rango": "mthly_income", "Valor mínimo": 0, "Valor máximo": 14000, "Puntaje": -10, "Factor":0.3},
    {"Variable": "Estudiante", "Rango": "mthly_income", "Valor mínimo": 14001, "Valor máximo": 26000, "Puntaje": 5, "Factor":0.3},
    {"Variable": "Estudiante", "Rango": "mthly_income", "Valor mínimo": 26001, "Valor máximo": 32000, "Puntaje": 10, "Factor":0.3},
    {"Variable": "Estudiante", "Rango": "mthly_income", "Valor mínimo": 32001, "Valor máximo": 10000000000, "Puntaje": 15, "Factor":0.3},  # "32,000+"

    # Estudiante - Score 
    {"Variable": "Estudiante", "Rango": "credit_score", "Valor mínimo": 456, "Valor máximo": 516, "Puntaje": -20, "Factor":0.3},
    {"Variable": "Estudiante", "Rango": "credit_score", "Valor mínimo": 517, "Valor máximo": 577, "Puntaje": -10, "Factor":0.3},
    {"Variable": "Estudiante", "Rango": "credit_score", "Valor mínimo": 578, "Valor máximo": 638, "Puntaje": 0, "Factor":0.3},
    {"Variable": "Estudiante", "Rango": "credit_score", "Valor mínimo": 639, "Valor máximo": 699, "Puntaje": 5, "Factor":0.3},
    {"Variable": "Estudiante", "Rango": "credit_score", "Valor mínimo": 700, "Valor máximo": 760, "Puntaje": 10, "Factor":0.3},

    # Hijos
    {"Variable": "Estudiante", "Rango": "n_dependants", "Valor mínimo": 0, "Valor máximo": 0, "Puntaje": 0, "Factor":0.05},
    {"Variable": "Estudiante", "Rango": "n_dependants", "Valor mínimo": 1, "Valor máximo": 1, "Puntaje": -5, "Factor":0.05},
    {"Variable": "Estudiante", "Rango": "n_dependants", "Valor mínimo": 2, "Valor máximo": 2, "Puntaje": -10, "Factor":0.05},
    {"Variable": "Estudiante", "Rango": "n_dependants", "Valor mínimo": 3, "Valor máximo": 1000000, "Puntaje": -15, "Factor":0.05},

    # Renta (categórico)
    {"Variable": "Estudiante", "Rango": "rents", "Valor mínimo": None, "Valor máximo": None, "Valor categórico": "Sí", "Puntaje": -5, "Factor":0.05},
    {"Variable": "Estudiante", "Rango": "rents", "Valor mínimo": None, "Valor máximo": None, "Valor categórico": "No", "Puntaje": 0, "Factor":0.05},

    # Tipo de empleo (categórico)
    {"Variable": "Estudiante", "Rango": "job_type", "Valor mínimo": None, "Valor máximo": None, "Valor categórico": "Formal", "Puntaje": 10, "Factor":0.1},
    {"Variable": "Estudiante", "Rango": "job_type", "Valor mínimo": None, "Valor máximo": None, "Valor categórico":"Informal", "Puntaje": 5, "Factor":0.1},
    {"Variable": "Estudiante", "Rango": "job_type", "Valor mínimo": None, "Valor máximo": None, "Valor categórico": "Independiente", "Puntaje": 0, "Factor":0.1},

    # Edad
    {"Variable": "Estudiante", "Rango": "age", "Valor mínimo": 21, "Valor máximo": 25, "Puntaje": 10, "Factor":0.05},
    {"Variable": "Estudiante", "Rango": "age", "Valor mínimo": 25, "Valor máximo": 30, "Puntaje": 0, "Factor":0.05},
    {"Variable": "Estudiante", "Rango": "age", "Valor mínimo": 30, "Valor máximo": 100, "Puntaje": 5, "Factor":0.05},
    ]

    df2 = pd.DataFrame(data2)
    df2 = df2[["Variable", "Rango", "Valor mínimo", "Valor máximo", "Valor categórico", "Puntaje", "Factor"]]
    return df2


def get_scores_assesment():
    return scores_for_first_assesment(), scores_second_assesment()