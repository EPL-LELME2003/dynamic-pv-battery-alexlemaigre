from pyomo.environ import ConcreteModel, Var, Objective, Constraint, NonNegativeReals, minimize, SolverFactory
import matplotlib.pyplot as plt

# Data / Parameters
load = [99,93, 88, 87, 87, 88, 109, 127, 140, 142, 142, 140, 140, 140, 137, 139, 146, 148, 148, 142, 134, 123, 108, 93] #KWh
lf_pv = [0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 9.80E-04, 2.47E-02, 9.51E-02, 1.50E-01, 2.29E-01, 2.98E-01, 3.52E-01, 4.15E-01, 4.58E-01, 3.73E-01, 2.60E-01, 2.19E-01, 1.99E-01, 8.80E-02, 7.03E-02, 3.90E-02, 9.92E-03, 1.39E-06, 0.00E+00, 0.00E+00] #%
timestep = len(load)
c_pv = 2500  #euro/kW
c_batt = 1000   #euro/kWh
eff_batt_in = 0.95
eff_batt_out = 0.95
chargetime = 4  # hours to charge fully the battery

# Model
model = ConcreteModel()

# Define model variables
##########################################
############ CODE TO ADD HERE ############
##########################################

model.Ppv = Var(within=NonNegativeReals)  #(kW)
model.SoC_max = Var(within=NonNegativeReals)  #(kWh)

model.Epv = Var(range(1,timestep+1), within=NonNegativeReals)  #(kWh)
model.SoC = Var(range(1,timestep+1), within=NonNegativeReals)  #(kWh)
model.Pbatt_in = Var(range(1,timestep+1), within=NonNegativeReals)  #(kW)
model.Pbatt_out = Var(range(1,timestep+1), within=NonNegativeReals)  #(kW)


# Define the constraints
##########################################
############ CODE TO ADD HERE ############
##########################################

def pv_generation_rule(model, t):
    return model.Epv[t] <= model.Ppv * lf_pv[t-1]

model.pv_generation = Constraint(range(1,timestep+1), rule=pv_generation_rule)


def battery_rule(model, t):
    return model.SoC[t] <= model.SoC_max

model.battery = Constraint(range(1,timestep+1), rule=battery_rule)


def battery_charge_rule(model, t):
    if t == 1:
        return model.SoC[t] == model.SoC_max
    else:
        return model.SoC[t] == model.SoC[t-1] + eff_batt_in * model.Pbatt_in[t-1] - model.Pbatt_out[t-1] / eff_batt_out

model.battery_charge = Constraint(range(1,timestep+1), rule=battery_charge_rule)


def battery_charge_in_rule(model, t):
    if t==1:
        return model.Pbatt_in[t] == 0
    return model.Pbatt_in[t] <= model.SoC_max / chargetime

model.battery_charge_in = Constraint(range(1,timestep+1), rule=battery_charge_in_rule)


def battery_charge_out_rule(model, t):
    return model.Pbatt_out[t] <= model.SoC_max / chargetime

model.battery_charge_out = Constraint(range(1,timestep+1), rule=battery_charge_out_rule)


def load_rule(model, t):
    return model.Epv[t] + model.Pbatt_out[t] - model.Pbatt_in[t] == load[t-1]

model.load_state = Constraint(range(1,timestep+1), rule=load_rule)


# Define the objective functions
##########################################
############ CODE TO ADD HERE ############
##########################################

def objective_rule(model):
    return c_pv * model.Ppv + c_batt * model.SoC_max

model.objective = Objective(rule=objective_rule, sense=minimize)


# Specify the path towards your solver (gurobi) file
solver = SolverFactory('gurobi')
solver.solve(model)

# Results - Print the optimal PV size and optimal battery capacity
##########################################
############ CODE TO ADD HERE ############
##########################################
print(f"Taille optimale du PV : {model.Ppv.value:.2f} kW")
print(f"Capacité optimale de la batterie : {model.SoC_max.value:.2f} kWh")

# Plotting - Generate a graph showing the evolution of (i) the load, 
# (ii) the PV production and, (iii) the soc of the battery
##########################################
############ CODE TO ADD HERE ############
##########################################

load_values = load
epv_values = [model.Epv[t].value for t in range(1, timestep+1)]
soc_values = [model.SoC[t].value for t in range(1, timestep+1)]

plt.figure(figsize=(10, 5))
plt.plot(range(1, timestep+1), load_values, label="Charge (kWh)", color="black", linestyle="--")
plt.plot(range(1, timestep+1), epv_values, label="Production PV (kWh)", color="orange")
plt.plot(range(1, timestep+1), soc_values, label="État de charge batterie (kWh)", color="blue")


plt.xlabel("Heure")
plt.ylabel("Énergie (kWh)")
plt.title("Évolution de la charge, de la production PV et de la batterie")
plt.legend()
plt.grid(True)
plt.show()
