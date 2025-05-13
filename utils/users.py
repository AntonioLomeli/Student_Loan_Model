import pandas as pd

class Major:
    def __init__(self, data:pd.Series):
        self.data = data
        for col in self.data.index:
            setattr(self, col.replace(" ", "_").lower(), self.data[col])

class Aval:
    def __init__(self, data:pd.Series):
        self.data = data

        for col in self.data.index:
            setattr(self, col.replace(" ", "_").lower(), self.data[col])


class Student:
    def __init__(self, data:pd.Series, major: Major):
        self.data = data
        for col in self.data.index:
            setattr(self, col.replace(" ", "_").lower(), self.data[col])
            
        self.major = major
    
    def get_aval(self, data_avales):
        data_avales_filtered = data_avales[self.id == data_avales["ID_Alumno"]].iloc[0]
        self.aval = Aval(data_avales_filtered)
