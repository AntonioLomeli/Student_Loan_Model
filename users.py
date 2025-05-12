import pandas as pd

class Major:
    def __init__(self, data:pd.Series):
        self.data = data
        for col in self.data.index:
            setattr(self, col, self.data[col])

class Student:
    def __init__(self, data:pd.Series, major: Major):
        self.data = data
        for col in self.data.index:
            setattr(self, col, self.data[col])
            
        self.major = major
        