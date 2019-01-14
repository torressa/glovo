'''
Main file. To read and preprocess data, simulate scenarios for order demand, 
and formulate and solve the Glover Assingment problem. Please see README.pdf for more details.
Author: David Torres Sanchez
Email: d.torressanchez@lancaster.ac.uk
'''

import pandas as pd
from math import exp
from datetime import datetime, timedelta


class expand(object):
    pass


class run(object):
    """docstring for orders"""

    def __init__(self, scenarios=1):
        self.scenarios = scenarios
        self.orders = expand()
        self.delivery_times = expand()
        self.last_slot = expand()
        self.results = expand()
        self._build()

    def _build(self):
        self._load_data()
        self._preprocess()
        self._fit_distrs()
        self._build_model()

    def _load_data(self):
        print "Loading data"
        self.orders.data = pd.read_csv('./input/orders.csv')
        self.delivery_times.data = pd.read_csv(
            './input/estimated_delivery_times.csv')
        self.last_slot.data = pd.read_csv('./input/last_slot_booked.csv')

    def _preprocess(self):
        from classes import Slot  # import slot object

        self.orders.slots = []  # initialise list of slot objects
        self.orders.slots = [
            Slot(i,  # id
                 datetime.strptime(   # start time in datetime format
                     self.orders.data['time_frame'][i], "%Y-%m-%d %H:%M:%S"),
                 0,  # duration (provisional)
                 exp(self.orders.data['orders_log'][i]),  # demand
                 0)  # leave probability (provisional)
            for i in range(0, 287)]  # len(self.orders.data)

        # Fill probabilites and delivery times using other data sets
        for slot in self.orders.slots:
            for entry in self.delivery_times.data.iterrows():
                # if the delivery day and hour matches get delivery time
                if entry[1].day == slot.start_t.weekday() and\
                        entry[1].hour == slot.start_t.hour:
                    slot.end_t = slot.start_t + \
                        timedelta(
                            seconds=entry[1].delivery_time)  # update end time
                    # update leaving probability
                    slot.leave = \
                        self.last_slot.data['last_slot_booked'][slot.start_t.hour]

    def _fit_distrs(self):
        from classes import Slot
        from fit import sample_pymc

        self.results.fits = {}

        for s in range(0, self.scenarios):
            print "Generating data for scenario %r" % (s)
            self.results.fits[s] = {}
            # Initialiase lis of empty Slot objects, otherwise updates won't work!
            self.results.fits[s]['slots'] = [
                Slot(0, 0, 0, 0, 0) for i in range(0, len(self.orders.slots))]

            demand_samples, leave_samples, scenario_prob = \
                sample_pymc(s, self.orders.slots)
            self.results.fits[s]['glovers'] = int(max(demand_samples))
            self.results.fits[s]['prob'] = scenario_prob

            count = 0
            # update demand and leave values for each slot
            for slot in self.results.fits[s]['slots']:
                slot.i_d = self.orders.slots[count].i_d
                slot.start_t = self.orders.slots[count].start_t
                slot.end_t = self.orders.slots[count].end_t
                slot.demand = demand_samples[count]
                slot.leave = leave_samples[count]
                count += 1

    def _build_model(self):
        from formulation import generate
        generate(self.results.fits)
