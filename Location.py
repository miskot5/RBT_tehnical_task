class Location:
    def __init__(self, city, part_of_city):
        self.city = city
        self.part_of_city = part_of_city

    def __str__(self):
        part_of_city = ""
        if self.part_of_city is not None:
            part_of_city = ", " + self.part_of_city
        return self.city + part_of_city

