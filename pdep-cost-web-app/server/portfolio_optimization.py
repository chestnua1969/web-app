import pandas as pd
import numpy as np
from ortools.sat.python import cp_model
from tqdm import tqdm
import matplotlib.pyplot as plt


EXCEL_DOC = "portfolio data.xlsx"


#
# Given budget and set of modernization improvements, allocate funds to maximize total available aircraft with crew
#

# Load Excel spreadsheets
risk_metrics_df = pd.read_excel(EXCEL_DOC, sheet_name="Risk Metrics")
constraints_df = pd.read_excel(EXCEL_DOC, sheet_name="Fleet Constraints")
sus_ops_costs_df = pd.read_excel(EXCEL_DOC, sheet_name="Sustainment & Ops Cost")
mod_options_df = pd.read_excel(EXCEL_DOC, sheet_name="Modernization Options")

# Get risk metrics
TOTAL_AIRCRAFT = {'B-1B': int(risk_metrics_df.query('Program == "B-1B" & Metric == "total_aircraft"')['Value']),
                  'B-52H': int(risk_metrics_df.query('Program == "B-52H" & Metric == "total_aircraft"')['Value'])}

AA_RATE = {'B-1B': float(risk_metrics_df.query('Program == "B-1B" & Metric == "AA_rate"')['Value']),
           'B-52H': float(risk_metrics_df.query('Program == "B-52H" & Metric == "AA_rate"')['Value'])}

# Get constraint values
MIN_AIRCRAFT = {'B-1B': int(constraints_df.query('Constraint == "min_B1Bs"')['Value']),
                'B-52H': int(constraints_df.query('Constraint == "min_B52Hs"')['Value'])}

BUDGET = int(constraints_df.query('Constraint == "budget"')['Value'])
BUDGET_RANGE = (int(np.round(0.5*BUDGET, -4)), int(np.round(1.3*BUDGET, -4)))
BUDGET_STEP = 10000

# Get sustainment costs per aircraft - maintenance, supply, etc
sus_df = sus_ops_costs_df.query('Bucket == "sust"').set_index('Program')
SUS_COSTS = sus_df['Cost (per aircraft)'].to_dict()

# Get operations cost per aircraft - flight crew, training pipeline, etc
ops_df = sus_ops_costs_df.query('Bucket == "ops"').set_index('Program')
OPS_COSTS = ops_df['Cost (per aircraft)'].to_dict()


#
# Optimization model construction
#

# Create models for budgets ranging from 50% to 150% of specified value
models = []
for budget in tqdm( range(BUDGET_RANGE[0], BUDGET_RANGE[1], BUDGET_STEP) ):
    model = cp_model.CpModel()

    # Count variables
    num_aircraft_vars = {'B-1B': model.NewIntVar(MIN_AIRCRAFT['B-1B'], TOTAL_AIRCRAFT['B-1B'], 'num_b1b'),
                    'B-52H': model.NewIntVar(MIN_AIRCRAFT['B-52H'], TOTAL_AIRCRAFT['B-52H'], 'num_b52h')}

    #  Sustainment cost variables
    sus_cost_vars = {}
    for program in ['B-1B', 'B-52H']:
        sus_cost_var = model.NewIntVar(0, budget, f'{program}_sus_cost')
        model.Add(sus_cost_var == num_aircraft_vars[program] * SUS_COSTS[program])
        sus_cost_vars[program] = sus_cost_var

    #  Operation cost variables
    ops_cost_vars = {}
    for program in ['B-1B', 'B-52H']:
        ops_cost_var = model.NewIntVar(0, budget, f'{program}_ops_cost')
        model.Add(ops_cost_var == num_aircraft_vars[program] * OPS_COSTS[program])
        ops_cost_vars[program] = ops_cost_var

    #  Modernization cost variables
    mod_vars = {'B-1B': {}, 'B-52H': {}}  # vars hold number of upgrades if upgrade is per aircraft or boolean value if upgrade is fleet-wide
    mod_cost_vars = {'B-1B': {}, 'B-52H': {}}
    for _, mod_row in mod_options_df.iterrows():
        program = mod_row['Program']
        mod = mod_row['Key']

        # Individual aircraft upgrades
        if mod_row['Implementation  (per aircraft or fleet-wide)'] == 'per aircraft':
                mod_var = model.NewIntVar(0, TOTAL_AIRCRAFT[program], f"{program}_num_{mod}")  # Number of aircraft to upgrade
                model.Add(mod_var <= num_aircraft_vars[program])

        # Fleet-wide modernization options
        elif mod_row['Implementation  (per aircraft or fleet-wide)'] == 'fleet-wide':
                mod_var = model.NewBoolVar(f"{program}_fleetwide_{mod}")  # True if fleet-wide upgrade is implemented

        mod_vars[program][mod] = mod_var
        mod_cost_vars[program][mod] = mod_row['Cost'] * mod_var


    # Build model objective function - Maximize measure of (aircraft availability) * (number of aircraft)
    obj_ftn_terms = [int(100*AA_RATE[program]) * num_aircraft_vars[program] for program in ['B-1B', 'B-52H']]
    for _, mod_row in mod_options_df.iterrows():
        program = mod_row['Program']
        mod = mod_row['Key']

        # Individual aircraft objective measures
        if mod_row['Implementation  (per aircraft or fleet-wide)'] == 'per aircraft':
            obj_ftn_terms.append( int(100 * mod_row['AA improvement']) * mod_vars[program][mod] )

        # Fleet-wide objective measures
        elif mod_row['Implementation  (per aircraft or fleet-wide)'] == 'fleet-wide':
            obj_var = model.NewIntVar(0, 100*TOTAL_AIRCRAFT[program], f"{program}_{mod}_obj_var")
            model.Add(obj_var == 0).OnlyEnforceIf(mod_vars[program][mod].Not())
            model.Add(obj_var == int(100 * mod_row['AA improvement']) * num_aircraft_vars[program]).OnlyEnforceIf(mod_vars[program][mod])
            obj_ftn_terms.append(obj_var)

    model.Maximize( sum(obj_ftn_terms) )

    # Add budget constraints to model
    all_mod_costs = []
    for program in ['B-1B', 'B-52H']:
        for _, cost in mod_cost_vars[program].items():
            all_mod_costs.append(cost)
    model.Add( sum(list(sus_cost_vars.values()) + list(ops_cost_vars.values()) + all_mod_costs) <= budget )

    # Store model with associated budget
    models.append({'budget': budget, 'model': model})


#
# Solve model and process solution
#

def solve_model(model_dict):

    # Solve model
    model = model_dict['model']
    budget = model_dict['budget']
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Process solution
    if status == cp_model.OPTIMAL:

        num_aircraft = {program: solver.Value(num_aircraft_vars[program]) for program in ['B-1B', 'B-52H']}
        aa_rates = {program: [AA_RATE[program]] * num_aircraft[program] for program in
                    ['B-1B', 'B-52H']}  # initial AA rates
        solution = {'budget': budget,
                    'B-1B': {'num_aircraft': num_aircraft['B-1B'], 'mod_cost': 0},
                    'B-52H': {'num_aircraft': num_aircraft['B-52H'], 'mod_cost': 0}}

        print("---------------------------------------------------------------------")
        print(f"Total budget: {budget}\n")

        # Total aircraft remaining in fleet after optimization
        accum_costs = []
        for program in ['B-1B', 'B-52H']:
            print(f"# {program} active: {num_aircraft[program]}")

            ops_cost = solver.Value(ops_cost_vars[program])
            print(f"Total operations cost: {ops_cost}")
            solution[program]['ops_cost'] = ops_cost
            accum_costs.append(ops_cost)

            sus_cost = solver.Value(sus_cost_vars[program])
            print(f"Total sustainment cost: {sus_cost}\n")
            solution[program]['sus_cost'] = sus_cost
            accum_costs.append(sus_cost)

        # Optimized modernization decisions
        for _, mod_row in mod_options_df.iterrows():
            program = mod_row['Program']
            mod = mod_row['Key']

            if mod_row['Implementation  (per aircraft or fleet-wide)'] == 'fleet-wide':
                do_mod = solver.Value(mod_vars[program][mod])
                print(f"{program} {mod} modernization (fleet-wide): {'True' if do_mod else 'False'}")
                if do_mod:
                    for i in range(num_aircraft[program]):
                        aa_rates[program][i] += mod_row['AA improvement']

            elif mod_row['Implementation  (per aircraft or fleet-wide)'] == 'per aircraft':
                num_mods = solver.Value(mod_vars[program][mod])
                print(f"{program} {mod} modernization (# aircraft upgraded): {num_mods}")
                for i in range(num_mods):
                    aa_rates[program][i] += mod_row['AA improvement']

            mod_cost = solver.Value(mod_cost_vars[program][mod])
            print(f"Total cost of modernization {mod_cost}\n")
            solution[program]['mod_cost'] += mod_cost
            accum_costs.append(mod_cost)

        # Calculate average AA rate
        for program in ['B-1B', 'B-52H']:
            avg_aa_rate = np.mean(aa_rates[program])
            print(f"{program} average AA rate: {avg_aa_rate}\n")
            solution[program]['avg_aa_rate'] = avg_aa_rate

        total_cost = sum(accum_costs)
        print(f"Total spent: {total_cost}")
        print("---------------------------------------------------------------------\n")
        # solution['total_cost'] = total_cost

        return solution

    elif status == cp_model.INFEASIBLE:
        print("Model is infeasible\n")
    else:
        print("Solution is not optimal for some reason (shouldn't happen)\n")


# Iterate through models and solve
# budget = 350000
# model_dict = filter(lambda m: True if m['budget'] == budget else False, models).__next__()
solutions = []
for model_dict in tqdm(models):
    sol = solve_model(model_dict)
    if sol:
        solutions.append(sol)

# Create dataframe from solutions of all models for analysis/viz
mindx = pd.MultiIndex.from_product([['B-1B', 'B-52H'], [sol['budget'] for sol in solutions]], names=['program', 'budget'])
cols = ['num_aircraft', 'ops_cost', 'sus_cost', 'mod_cost', 'avg_aa_rate']
solutions_df = pd.DataFrame(index=mindx, columns=cols)
for sol in solutions:
    budget = sol['budget']
    for program in ['B-1B', 'B-52H']:
        sol_series = pd.Series(sol[program])
        sol_series['prog_cost'] = sol_series[['ops_cost', 'sus_cost', 'mod_cost']].sum()
        solutions_df.loc[(program, budget)] = sol_series


#
# Viz solutions
#

fig, axs = plt.subplots(3, 2, sharex=True)
for j, prog in enumerate(['B-1B', 'B-52H']):
    # Number of aircraft
    axs[0,j].plot(solutions_df.loc[prog, 'num_aircraft'])
    axs[0, j].set_title(f" # {prog} aircraft")

    # Average AA rate
    axs[1, j].plot(solutions_df.loc[prog, 'avg_aa_rate'])
    axs[1, j].set_title(f"{prog} avg AA rate")

    # Cost data
    data = solutions_df.loc[prog, ['ops_cost', 'sus_cost', 'mod_cost']]
    line_objs = axs[2, j].plot(data)
    axs[2, j].set_title(f"{prog} costs")
    axs[2, j].set_xlabel("Budget")
    axs[2, j].legend(line_objs, data.columns)