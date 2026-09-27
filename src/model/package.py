class Package:
    def __init__(self, pkg_id, dim, val, w, is_fragile, eta):
        self.id = pkg_id
        self.og_dim = dim
        self.cur_dim = dim.copy()
        self.val = val
        self.w = w
        self.is_fragile = is_fragile
        self.eta = eta

        #Orientasi
        self.orient = {'w': 'x', 'l': 'y', 'h': 'z'}

def rotate(self, axis):
    if axis == 'z':
        temp_w = self.cur_dim['w']
        self.cur_dim['w'] = self.cur_dim['l']
        self.cur_dim['l'] = temp_w

        # Update label orientasi
        self.orient['w'], self.orient['l'] = self.orient['l'], self.orient['w']

    if axis == 'x':
        temp_l = self.cur_dim['l']
        self.cur_dim['l'] = self.cur_dim['h']
        self.cur_dim['h'] = temp_l

        # Update label orientasi
        self.orient['l'], self.orient['h'] = self.orient['h'], self.orient['l']

    if axis == 'y':
        temp_w = self.cur_dim['w']
        self.cur_dim['w'] = self.cur_dim['h']
        self.cur_dim['h'] = temp_w

        # Update label orientasi
        self.orient['w'], self.orient['h'] = self.orient['h'], self.orient['w']



    def __repr__(self):
         return f"Package({self.id}, Dim:{self.cur_dim}, Val: {self.val}, W: {self.w}, Fragile: {self.is_fragile}, ETA: {self.eta})"

    
