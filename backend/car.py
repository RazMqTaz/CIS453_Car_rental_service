class Car:
    def __init__(self, id: int, make: str, model: str, year: int, status: str) -> None:
        self.id = id
        self.make = make
        self.model = model
        self.year = year
        self.status = status
    
    def __str__(self) -> str:
        return f"ID: {self.id}\nMake: {self.make}\nModel: {self.model}\nYear: {self.year}\nStatus: {self.status}"
    
    def updateStatus(self, status: str) -> None:
        self.status = status
    
    def getInfo(self) -> dict:
        return {"ID:" : self.id, "Make:" : self.make, "Model" : self.model, "Year" : self.year, "Status:" : self.status}
    