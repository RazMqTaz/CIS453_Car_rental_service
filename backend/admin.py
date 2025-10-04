from .reservation import Reservation
from .user import User


class Admin(User):
    def __init__(
        self, user_id: int, name: str, email: str, license_number: str
    ) -> None:
        super().__init__(user_id, name, email, license_number, role="admin")

    # Define class for viewing/cancel reservations from database, implementation depends on what database we use
