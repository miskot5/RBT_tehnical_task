class Location:
    def __init__(self, grad, deo_grada):
        self.grad = grad if grad is not None else "nepoznato"
        self.deo_grada = deo_grada if deo_grada is not None else "nepoznato"

    def __str__(self):
        return self.grad + ", " +self.deo_grada

