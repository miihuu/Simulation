import pygad
import random
import json
import subprocess
import datetime
import json
import sys
import csv
import numpy as np
from tqdm import tqdm
from itertools import product

from simulation.model.Simulation import Simulation, SimulationReturnType
from simulation.utils.InputBounds import InputBounds
from simulation.config import config_directory
from simulation.utils.SimulationBuilder import SimulationBuilder
from simulation.optimization.genetic import GeneticOptimization, OptimizationSettings
from simulation.data.results import results_directory
from simulation.data.assemble import Assembler
from simulation.cmd.run_simulation import get_default_settings, SimulationSettings

# Parameter grid
param_grid = {
    'chromosome_size': [24, 32, 48],
    'generation_limit': [30, 40, 50],
    'num_parents': [8, 12, 16],
    'k_tournament': [3, 5, 7],
    'elitism': [8, 10, 12],
    'mutation_percent': [5, 10, 20],
    'max_mutation': [0.05, 0.1, 0.2],
}

# Generate all combinations of parameters
param_combinations = list(product(*param_grid.values()))

# Number of random combinations to evaluate
num_evaluations = 10

# Select random combinations to evaluate from the parameter grid
random_combinations = random.sample(param_combinations, num_evaluations)

best_fitness = -np.inf
best_params = None
results = []

# Build simulation model
settings = SimulationSettings()
initial_conditions, model_parameters = get_default_settings(settings.race_type)
simulation_builder = SimulationBuilder() \
    .set_initial_conditions(initial_conditions) \
    .set_model_parameters(model_parameters, settings.race_type) \
    .set_golang(settings.golang) \
    .set_return_type(settings.return_type) \
    .set_granularity(settings.granularity)

simulation_model = simulation_builder.get()

# Initialize a "guess" speed array
driving_hours = simulation_model.get_driving_time_divisions()
input_speed = np.array([60] * driving_hours)

# Run simulation model with the "guess" speed array
unoptimized_time = simulation_model.run_model(speed=input_speed, plot_results=True,
                                            verbose=settings.verbose,
                                            route_visualization=settings.route_visualization)

# Set up optimization models
maximum_speed = 60
minimum_speed = 0

bounds = InputBounds()
bounds.add_bounds(driving_hours, minimum_speed, maximum_speed)

# Iterate over randomly selected parameter combinations
for params in random_combinations:
    
    print("Evaluating: ", params)

    # Perform optimization with Genetic Optimization
    optimization_settings: OptimizationSettings = OptimizationSettings(
        chromosome_size=params[0],
        generation_limit=params[1],
        num_parents=params[2],
        k_tournament=params[3],
        elitism=params[4],
        mutation_percent=params[5],
        max_mutation=params[6]
    )

    with tqdm(total=optimization_settings.generation_limit, file=sys.stdout, desc="Optimizing driving speeds",
            position=0, leave=True, unit="Generation", smoothing=1.0) as pbar:
        geneticOptimization = GeneticOptimization(simulation_model, bounds, settings=optimization_settings, pbar=pbar)
        geneticOptimization.ga_instance.run()
        
    solution, solution_fitness, solution_idx = geneticOptimization.ga_instance.best_solution()
    
    # Save results
    result = {
        'params': {
            'chromosome_size': params[0],
            'generation_limit': params[1],
            'num_parents': params[2],
            'k_tournament': params[3],
            'elitism': params[4],
            'mutation_percent': params[5],
            'max_mutation': params[6]
        },
        'fitness': solution_fitness
    }
    results.append(result)
    
    # Update best fitness and parameters
    if solution_fitness > best_fitness:
        best_fitness = solution_fitness
        best_params = params

    # Write results to file
    with open('ga_results.json', 'w') as f:
        json.dump(results, f, indent=4)
    
    print("Current best fitness:", best_fitness)

print("Best fitness:", best_fitness)
print("Best parameters:", best_params)
