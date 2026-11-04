class Room:
    def __init__(
        self,
        room_type,
        hourly_rate,
        daily_rate,
        description,
        amenities,
        image,
        max_guests=2
    ):
        self.room_type = room_type
        self.hourly_rate = hourly_rate
        self.daily_rate = daily_rate
        self.description = description
        self.amenities = amenities
        self.image = image
        self.max_guests = max_guests


ROOM_DATA = {
    "Economy": Room(
        room_type="Economy",
        hourly_rate=1100 / 12,
        daily_rate=1500,
        description="A simple and affordable room for short stays.",
        amenities=[
            "Double bed",
            "Air conditioning",
            "Private bathroom",
            "Hot shower",
            "Wi-Fi",
            "Smart TV"
        ],
        image="Econo.jpg",
        max_guests=2,   # placeholder: set to your real capacity
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
        image="Deluxe.jpg",
        max_guests=3,   # placeholder: set to your real capacity
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
        image="Premium.jpg",
        max_guests=4,   # placeholder: set to your real capacity
    ),

    "Family Suite": Room(
        room_type="Family Suite",
        hourly_rate=2400 / 12,
        daily_rate=3200,
        description="A spacious suite with a sofa bed, made for families.",
        amenities=["Queen bed", "Sofa bed", "Air conditioning", "Private bathroom",
                   "Hot shower", "Wi-Fi", "Smart TV", "Mini refrigerator"],
        image="images/FamilySuite",
        max_guests=6,
    ),

    "Executive Suite": Room(
        room_type="Executive Suite",
        hourly_rate=2800 / 12,
        daily_rate=3800,
        description="A suite with a king bed, work desk and bathtub.",
        amenities=["King bed", "Air conditioning", "Private bathroom", "Bathtub",
                   "Hot shower", "Wi-Fi", "Smart TV", "Mini refrigerator", "Work desk"],
        image="images/Executive",
        max_guests=5,
    ),

    "Presidential Suite": Room(
        room_type="Presidential Suite",
        hourly_rate=4800 / 12,
        daily_rate=6500,
        description="Our top suite with a living area and private balcony.",
        amenities=["King bed", "Sofa bed", "Air conditioning", "Private bathroom",
                   "Bathtub", "Hot shower", "Wi-Fi", "Smart TV", "Mini refrigerator",
                   "Work desk", "Balcony"],
        image="images/Presidential",
        max_guests=10,
    ),
}


def get_room(room_type):
    return ROOM_DATA.get(room_type)


def get_all_rooms():
    return ROOM_DATA
