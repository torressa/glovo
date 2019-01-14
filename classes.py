class Slot(object):
    '''slot object'''

    def __init__(self, i_d, time_available, delivery_time, demand, leave):
        self.i_d = i_d                          # integer
        self.start_t = time_available           # datetime
        self.end_t = delivery_time              # datetime
        self.demand = demand                    # float
        self.leave = leave                      # float [0,1] or int {0,1}

    def __repr__(self):
        return str(self)

    def __str__(self):  # for printing purposes
        return "SlotObj(%r,%r,%r, %r, %r)" % (
            self.i_d, self.start_t, self.end_t, self.demand, self.leave)
