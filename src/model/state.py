class State:
    def __init__(self, truck, packages):
        self.truck = truck
        self.packages = packages

        self.placements = {}

        for pkg in self.packages:
            self.placements[pkg.id] = None

    def initialize_random_state(self):
        # Dilanjutin ntar kalo udah ada keputusan boleh pake library random atau ga
        return self