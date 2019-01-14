''' Creates the necessary variables and formulates the 
Glover Assignment problem using generated scenario data.
Uncomment and comment out the appropriate lines in 
the objectives and constraints for the non-linear solution.'''

import gurobipy as gb
from formatting import time_to_int, previous_and_next

# global variables
x, e, z, Z, QF, QC, keys_dict = {}, {}, {}, {}, {}, {}, {}


def set_solver_params(model):
    '''Solver parameters'''
    model.Params.MIPFocus = 1  # Focuses on obtaining an optimal solution
    model.Params.MIPGap = 0.05  # Optimality gap
    return model


def create_variables(model, scenario_dict):
    global x, e, z, Z, QF, QC, keys_dict
    # keys for variables
    keys_dict = {(g, slot.i_d, s): time_to_int(slot.start_t)
                 for s in range(0, len(scenario_dict))
                 for g in range(0, scenario_dict[s]['glovers'])
                 for slot in scenario_dict[s]['slots']}

    x = model.addVars(keys_dict, vtype="B", name="x")   # binary varible x
    e = model.addVars([(slot.i_d, s) for s in range(0, len(scenario_dict))
                       for slot in scenario_dict[s]['slots']],
                      vtype="C", name="e")              # continuous varible e
    z = model.addVars(keys_dict, vtype="B", name="z")   # binary varible z
    Z = model.addVars(keys_dict, vtype="B", name="Z")   # binary varible Z
    # continuous varible QF
    QF = model.addVars([(slot.i_d, s, 'F')
                        for s in range(0, len(scenario_dict))
                        for slot in scenario_dict[s]['slots']],
                       vtype="C", name="QF", lb=0)
    # continuous varible QF
    QC = model.addVars([(slot.i_d, s, 'C')
                        for s in range(0, len(scenario_dict))
                        for slot in scenario_dict[s]['slots']],
                       vtype="C", name="QC", lb=0)
    model.update()
    return model


def set_objective(model, scenario_dict):
    # dummy variables to linearize objective function
    durations = {(g, slot.i_d, s): time_to_int(slot.end_t - slot.start_t)
                 for s in range(0, len(scenario_dict))
                 for g in range(0, scenario_dict[s]['glovers'])
                 for slot in scenario_dict[s]['slots']}
    model.ModelSense = gb.GRB.MINIMIZE
    model.NumObj = 2
    obj1 = gb.quicksum(scenario_dict[s]['prob']*e[slot.i_d, s]
                       for s in range(0, len(scenario_dict))
                       for slot in scenario_dict[s]['slots'])
    obj2 = gb.quicksum(scenario_dict[s]['prob']*x[g, slot.i_d, s]
                       for s in range(0, len(scenario_dict))
                       for g in range(0, scenario_dict[s]['glovers'])
                       for slot in scenario_dict[s]['slots'])
    model.setObjectiveN(obj1, 0, 3)
    model.setObjectiveN(obj2, 1, 2)
    #################################################
    # Constraints for non-linear optimisation model #
    #################################################
    # C1 = model.addVars([s for s in range(0, len(scenario_dict))],
    #                    vtype="C", name="C1", lb=0)
    # C2 = model.addVars([s for s in range(0, len(scenario_dict))],
    #                    vtype="C", name="C2", lb=0)
    # model.addConstrs((QC.sum('*', s) >= QF.sum('*', s) *
    #                   C1[s] for s in range(0, len(scenario_dict))))
    # model.addConstrs((x.prod(durations) >= (z.prod(keys_dict) + Z.prod(durations)) *
    #                   C2[s] for s in range(0, len(scenario_dict))))
    # obj = gb.quicksum(scenario_dict[s]['prob']*(10 * C1[s] - C2[s])
    #                   for s in range(0, len(scenario_dict)))
    # model.setObjective(obj, sense=gb.GRB.MINIMIZE)
    model.update()
    return model


def add_constraints(model, scenario_dict):
    from math import floor
    M = 1e5  # Big M constraint
    # Demand #
    model.addConstrs((x.sum('*', slot.i_d, s) + e[slot.i_d, s]
                      >= floor(slot.demand)
                      for s in range(0, len(scenario_dict))
                      for slot in scenario_dict[s]['slots']),
                     name='Demand(4)')
    # Glovers Leaving #
    model.addConstrs((Z[g, slot.i_d, s] >= slot.leave
                      for s in range(0, len(scenario_dict))
                      for g in range(0, scenario_dict[s]['glovers'])
                      for slot in scenario_dict[s]['slots']),
                     name='Leaving(6)')
    model.addConstrs((x[g, slot_d.i_d, s] <= 1 - x[g, slot.i_d, s]
                      for s in range(0, len(scenario_dict))
                      for g in range(0, scenario_dict[s]['glovers'])
                      for slot in scenario_dict[s]['slots']
                      for slot_d in scenario_dict[s]['slots']
                      if slot.start_t < slot_d.start_t < slot.end_t))
    for s in range(0, len(scenario_dict)):
        for g in range(0, scenario_dict[s]['glovers']):
            for slot in scenario_dict[s]['slots']:
                slots_after = [_ for _ in scenario_dict[s]['slots']
                               if slot.end_t <= _.start_t]
                if len(slots_after) > 0:
                    model.addConstr(x[g, slots_after[0].i_d, s]
                                    <= 1 - Z[g, slot.i_d, s])
    #################################################
    # Constraints for non-linear optimisation model #
    #################################################
    # Orders #
    # model.addConstrs((QC[slot.i_d, s, 'C'] <= QF[slot.i_d, s, 'F']
    #                   for s in range(0, len(scenario_dict))
    #                   for slot in scenario_dict[s]['slots']),
    #                  name='Orders(2)')
    # model.addConstrs((x.sum('*', slot.i_d, s) <= QF[slot.i_d, s, 'F']
    #                   for s in range(0, len(scenario_dict))
    #                   for slot in scenario_dict[s]['slots']),
    #                  name='Orders(3)')
    # Transitivity constraints #
    # model.addConstrs((z[g, scenario_dict[s]['slots'][0].i_d, s] >=
    #                   x[g, scenario_dict[s]['slots'][0].i_d, s]
    #                   for s in range(0, len(scenario_dict))
    #                   for g in range(0, scenario_dict[s]['glovers'])),
    #                  name='TransitivityInit(9)')
    # model.addConstrs((z[g, slot.i_d, s] >= x[g, slot.i_d, s] - x[g, slot_p.i_d, s]
    #                   for s in range(0, len(scenario_dict))
    #                   for g in range(0, scenario_dict[s]['glovers'])
    #                   for slot_p, slot, slot_n in previous_and_next(scenario_dict[s]['slots'])
    #                   if slot_p is not None))
    # model.addConstrs((z.sum(g, '*', s) <= 1
    #                   for s in range(0, len(scenario_dict))
    #                   for g in range(0, scenario_dict[s]['glovers'])),
    #                  name='Transitivity(11)')
    model.write("./output/lp.lp")
    model.update()
    return model


def optimise(model):
    model.optimize()

    if model.getAttr("Status") == 3:  # Infeasible
        model.computeIIS()
        model.write("model.ilp")
    elif model.getAttr("Status") == 4:
        model.Params.DualReductions = 0
        model.optimize()
    else:  # Save solution
        model.write("./output/solution.sol")
    return


def generate(scenario_dict):
    '''Formulates the problem.
    scenario_dict :: dictionary with dictionary entries for each scenario.
    Each of these contains a 'slots' field which contains a list of Slot objects.
    And a 'glovers' field with the maximum number of glovers for that scenario'''
    model = gb.Model("Stochastic Glover Allocation")
    model = set_solver_params(model)
    model = create_variables(model, scenario_dict)
    model = set_objective(model, scenario_dict)
    model = add_constraints(model, scenario_dict)
    optimise(model)
    return
