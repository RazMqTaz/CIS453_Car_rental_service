from user import User
from reservation import Reservation


class Main:
    # Purely for testing backend stuff for now
    test_user1 = User(
        user_id=123, name="bob", email="bob@gmail.com", license_number="FD53Q1"
    )
    res1 = Reservation(
        vehicle_type="sedan",
        car_id=321,
        user_id=123,
        start_date="october 4",
        end_date="november 15",
        status="active",
    )
    res2 = Reservation(
        vehicle_type="SUV",
        car_id=543,
        user_id=123,
        start_date="november 15",
        end_date="november 17",
        status="reserved",
    )
    test_user1.add_reservation(res1)
    test_user1.add_reservation(res2)
    print(test_user1)
