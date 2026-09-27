class Truck:
    def __init__(self, dim, max_cap):
        self.dim = dim
        self.max_cap = max_cap
        
    def __repr__(self):
        return f"Truck(Dim:{self.dimensions}, MaxCap:{self.max_capacity})"