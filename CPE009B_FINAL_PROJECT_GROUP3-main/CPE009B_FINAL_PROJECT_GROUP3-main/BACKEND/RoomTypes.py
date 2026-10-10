class Room:
    def __init__(
        self,
        room_type,
        hourly_rate,
        daily_rate,
        description,
        amenities,
        image
    ):
        self.room_type = room_type
        self.hourly_rate = hourly_rate
        self.daily_rate = daily_rate
        self.description = description
        self.amenities = amenities
        self.image = image


ROOM_DATA = {
    "Econo": Room(
        room_type="Econo",
        hourly_rate=1100 / 12,
        daily_rate=1500,
        description="A simple and affordable room for short stays.",
        amenities=[
            "Double bed",
            "Air conditioning",
            "Private bathroom",
            "Hot shower",
            "Wi-Fi"
        ],
        image="Econo.jpg"
    ),

    "Deluxe": Room(
        room_type="Deluxe",
        hourly_rate=1650 / 12,
        daily_rate=1950,
        description="A comfortable room with upgraded facilities.",
        amenities=[
            "Queen bed",
            "Air conditioning",
            "Private bathroom",
            "Hot shower",
            "Wi-Fi",
            "Smart TV"
        ],
        image="Deluxe.jpg"
    ),

    "Premium": Room(
        room_type="Premium",
        hourly_rate=1400 / 12,
        daily_rate=1800,
        description="A relaxing room with extra comfort and space.",
        amenities=[
            "Queen bed",
            "Air conditioning",
            "Private bathroom",
            "Hot shower",
            "Wi-Fi",
            "Smart TV",
            "Mini refrigerator"
        ],
        image="Premium.jpg"
    )
}


def get_room(room_type):
    return ROOM_DATA.get(room_type)


def get_all_rooms():
    return ROOM_DATA