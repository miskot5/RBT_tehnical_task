class Location:
    def __init__(self, grad, deo_grada):
        self.city = grad
        self.part_of_city = deo_grada

    def __str__(self):
        part_of_city = ""
        if self.part_of_city is not None:
            part_of_city = ", " + self.part_of_city
        return self.city + part_of_city

