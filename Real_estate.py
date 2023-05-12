class Real_Estate:
    def __init__(self, type, offer, location, spm, year, area, storey, num_of_floors,registration, heating_type, num_of_rooms, num_of_toilets, parking, elevator, other):
        self.type = type
        self.offer = offer
        self.location = location
        self.spm = spm
        self.year = year
        self.area = area
        self.storey = storey
        self.num_of_floors = num_of_floors
        self.registration = registration
        self.heating_type = heating_type
        self.num_of_rooms = num_of_rooms
        self.num_of_toilets = num_of_toilets
        self.parking = parking
        self.elevator = elevator
        self.other = other
    def processing(self, attribute):
        if attribute is None:
            return  None
        else:
            return str(attribute)
    def __json__(self):
        return {
            "type": self.processing(self.type),
            "location": self.processing(self.location),
            "sp": self.processing(self.spm),
            "year": self.processing(self.year),
            "area": self.processing(self.area),
            "storey": self.processing(self.storey),
            "num_of_floors": self.processing(self.num_of_floors),
            "registration": self.processing(self.registration),
            "heating_type": self.processing(self.heating_type),
            "num_of_rooms": self.processing(self.num_of_rooms),
            "num_of_toilets": self.processing(self.num_of_toilets),
            "parking": self.processing(self.parking),
            "elevator": self.processing(self.elevator),
            "other": self.processing(self.other),
        }