def processing(attribute):
    if attribute is None:
        return None
    else:
        return str(attribute)


class RealEstate:
    def __init__(self, external_id, typeof, offer, location, spm, year, area, storey, num_of_floors, registration,
                 heating, num_of_rooms, num_of_toilets, parking, elevator, other):
        self.external_id = external_id
        self.type = typeof
        self.offer = offer
        self.location = location
        self.spm = spm
        self.year = year
        self.area = area
        self.storey = storey
        self.num_of_floors = num_of_floors
        self.registration = registration
        self.heating_type = heating
        self.num_of_rooms = num_of_rooms
        self.num_of_toilets = num_of_toilets
        self.parking = parking
        self.elevator = elevator
        self.other = other

    def __json__(self):
        return {
            "external_id": processing(self.external_id),
            "type": processing(self.type),
            "location": self.location,
            "sp": processing(self.spm),
            "year": processing(self.year),
            "area": processing(self.area),
            "storey": processing(self.storey),
            "num_of_floors": processing(self.num_of_floors),
            "registration": processing(self.registration),
            "heating_type": processing(self.heating_type),
            "num_of_rooms": processing(self.num_of_rooms),
            "num_of_toilets": processing(self.num_of_toilets),
            "parking": processing(self.parking),
            "elevator": processing(self.elevator),
            "other": processing(self.other),
        }
