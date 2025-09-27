from .reservation import Reservation


class User:
    def __init__(
        self,
        user_id: int,
        name: str,
        email: str,
        license_number: str,
        role: str = "customer",
    ) -> None:
        self.id = user_id
        self.name = name
        self.email = email
        self.license_number = license_number
        self.role = role
        self.reservations = []

    def __str__(self) -> str:
        reservations_str = "\n--------------------\n".join(
            str(r) for r in self.reservations
        )
        return f"User ID: {self.id}\nName: {self.name}\nEmail: {self.email}\nLicense Number: {self.license_number}\nRole: {self.role}\nReservations:\n--------------------\n{reservations_str}"

    def login(self, email, password) -> bool:
        # Placeholder: if email and password match whats in db, then success
        return True

    def view_reservations(self):  # -> list[Reservation]:
        # Returns a list of reservation objects
        for reservation in self.reservations:
            print(reservation.get_info())

    def add_reservation(self, reservation) -> None:
        # Possible way to update a Users reservations,
        # not sure how we want to have the backend/db interact
        self.reservations.append(reservation)
