import pandas as pd
import requests
from io import BytesIO

def read_excel_drive(file_id, file_type='xlsx'):
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    response = requests.get(url)
    response.raise_for_status()  # lanza excepción si hay error

    excel_data = BytesIO(response.content)

    if file_type == 'xlsx':
        df = pd.read_excel(excel_data, engine='openpyxl')
    else:
        df = pd.read_csv(excel_data)
    return df


if __name__ == "__main__":
    # Example usage
    # For CSV
    file_id = "1JXuh9SqIa0O4gaSMBEKDuVaJ2TotCD3X"
    df = read_excel_drive(file_id, file_type='csv')
    print(df.head())
