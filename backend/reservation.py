class Reservation:
    def __init__(
        self,
        vehicle_type: str,
        car_id: int,
        user_id: int,
        start_date: str,
        end_date: str,
        status: str,
    ) -> None:
        self.vehicle_type = vehicle_type
        self.car_id = car_id
        self.user_id = user_id
        self.start_date = start_date
        self.end_date = end_date
        self.status = status

    def __str__(self) -> str:
        return f"Vehicle Type: {self.vehicle_type}\nCar ID: {self.car_id}\nUser ID: {self.user_id}\nStart Date: {self.start_date}\nEnd Date: {self.end_date}\nStatus: {self.status}"

    def get_info(self) -> dict:
        return {
            "Vehicle Type: ": self.vehicle_type,
            "Car ID: ": self.car_id,
            "Assigned User ID: ": self.user_id,
            "Start Date: ": self.start_date,
            "End Date: ": self.end_date,
            "Status: ": self.status,
        }
