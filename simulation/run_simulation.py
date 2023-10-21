import numpy as np
import json
import sys
import pandas as pd
import os
import datetime

from matplotlib import pyplot as plt
from main.Simulation import SimulationReturnType
from optimization.bayesian import BayesianOptimization
from optimization.random import RandomOptimization
from utils.InputBounds import InputBounds
from config import config_directory
from common.simulationBuilder import SimulationBuilder

"""
Description: Execute simulation optimization sequence. 
"""


class SimulationSettings:
    """

    This class stores settings that will be used by the simulation.

    """

    def __init__(self, race_type="ASC", golang=True, return_type=SimulationReturnType.time_taken,
                 optimization_iterations=5, route_visualization=False, verbose=False, granularity=1):
        self.race_type = race_type
        self.optimization_iterations = optimization_iterations
        self.golang = golang
        self.return_type = return_type
        self.route_visualization = route_visualization
        self.verbose = verbose
        self.granularity = granularity


def run_simulation(settings):
    """

    This method parses initial conditions for the simulation and store them in a simulationState object. Then, begin
    optimizing simulation with Bayesian optimization and then random optimization.

    :param SimulationSettings settings: object that stores settings for the simulation and optimization sequence
    :return: returns the time taken for simulation to complete before optimization
    :rtype: float

    """

    #  ----- Load initial conditions ----- #

    if settings.race_type == "ASC":
        initial_conditions_path = config_directory / "initial_conditions_ASC.json"
    else:
        initial_conditions_path = config_directory / "initial_conditions_FSGP.json"

    with open(initial_conditions_path) as f:
        initial_conditions = json.load(f)

    # ----- Load from settings_*.json -----

    if settings.race_type == "ASC":
        config_path = config_directory / "settings_ASC.json"
    else:
        config_path = config_directory / "settings_FSGP.json"

    with open(config_path) as f:
        model_parameters = json.load(f)

    # Build simulation model
    simulation_builder = SimulationBuilder() \
        .set_initial_conditions(initial_conditions) \
        .set_model_parameters(model_parameters, settings.race_type) \
        .set_golang(settings.golang) \
        .set_return_type(settings.return_type) \
        .set_granularity(settings.granularity)

    simulation_model = simulation_builder.get()

    # Initialize a "guess" speed array
    driving_hours = simulation_model.get_driving_time_divisions()
    input_speed = np.array([30] * driving_hours)

    # Run simulation model with the "guess" speed array
    unoptimized_time = simulation_model.run_model(speed=input_speed, plot_results=True,
                                                  verbose=settings.verbose,
                                                  route_visualization=settings.route_visualization)

    # Set up optimization models
    bounds = InputBounds()
    bounds.add_bounds(driving_hours, 20, 60)
    optimization = BayesianOptimization(bounds, simulation_model.run_model)
    random_optimization = RandomOptimization(bounds, simulation_model.run_model)

    # Perform optimization with Bayesian optimization
    results = optimization.maximize(init_points=3, n_iter=settings.optimization_iterations, kappa=10)
    optimized = simulation_model.run_model(speed=np.fromiter(results, dtype=float), plot_results=True,
                                           verbose=settings.verbose,
                                           route_visualization=settings.route_visualization)

    # Perform optimization with random optimization
    results_random = random_optimization.maximize(iterations=settings.optimization_iterations)
    optimized_random = simulation_model.run_model(speed=np.fromiter(results_random, dtype=float), plot_results=True,
                                                  verbose=settings.verbose,
                                                  route_visualization=settings.route_visualization)

    #  ----- Output results ----- #

    display_output(settings.return_type, unoptimized_time, optimized, optimized_random, results, results_random)

    return unoptimized_time


def main():
    """

    This is the entry point to Simulation.
    First, parse command line arguments, then execute simulation optimization sequence.

    """

    #  ----- Parse commands passed from command line ----- #

    cmds = sys.argv
    simulation_settings = parse_commands(cmds)

    print("GoLang is " + str("enabled." if simulation_settings.golang else "disabled."))
    print("Verbose is " + str("on." if simulation_settings.verbose else "off."))
    print("Route visualization is " + str("on." if simulation_settings.route_visualization else "off."))
    print("Optimizing for " + str("time." if simulation_settings.return_type == 0 else "distance."))
    print(f"Will perform {simulation_settings.optimization_iterations} optimization iterations.")

    #  ----- Run simulation ----- #

    run_simulation(simulation_settings)

    print("Simulation has completed.")


def display_output(return_type, unoptimized, optimized, optimized_random, results, results_random):
    if return_type is SimulationReturnType.time_taken:
        print(f'TimeSimulation results. Time Taken: {-1 * unoptimized} seconds, ({str(datetime.timedelta(seconds=int(-1 * unoptimized)))})')
        print(f'Optimized results. Time taken: {-1 * optimized} seconds, ({str(datetime.timedelta(seconds=int(-1 * optimized)))})')
        print(f'Random results. Time taken: {-1 * optimized_random} seconds, ({str(datetime.timedelta(seconds=int(-1 * optimized_random)))})')

    elif return_type is SimulationReturnType.distance_travelled:
        print(f'Distance travelled: {unoptimized}')
        print(f'Optimized results. Max traversable distance: {optimized}')
        print(f'Random results. Max traversable distance: {optimized_random}')

    print(f'Optimized Speeds array: {results}')
    print(f'Random Speeds array: {results_random}')

    return unoptimized


def display_commands():
    """

    Display all valid command line arguments to the user.

    """

    print("------------------------COMMANDS-----------------------\n"
          "-help                 Display list of valid commands.\n"
          "\n"                   
          "-race_type            Define which race should be simulated. \n"     
          "                      (ASC/FSGP)\n"
          "\n"
          "-golang               Define whether golang implementations\n"
          "                      will be used. \n"
          "                      (True/False)\n"
          "\n"
          "-optimize             Define what data the simulation\n"
          "                      should optimize. \n"
          "                      (time_taken/distance_travelled)\n"
          "\n"
          "-iter                 Set how many iterations of optimizations\n"
          "                      should be performed on the simulation.\n"
          "\n"
          "-verbose              Set whether simulation methods should\n"
          "                      execute as verbose.\n"
          "                      (True/False)\n"
          "\n"                  
          "-route_visualization   Define whether the simulation route\n"
          "                      should be plotted and visualized.\n"
          "                      (True/False)\n"
          "\n"
          "-granularity          Define how granular the speed array\n"
          "                      should be, where 1 is hourly and 2 is\n"
          "                      bi-hourly.\n"
          "\n"
          "-------------------------USAGE--------------------------\n"
          ">>>python3 run_simulation.py -golang=False -optimize=time_taken -iter=3\n")


valid_commands = ["-help", "-race_type", "-golang", "-optimize", "-iter", "-verbose", "-route_visualization", "-granularity"]


def identify_invalid_commands(cmds):
    """

    Check to make sure that commands passed from user are valid.

    :param cmds: list of commands from command line
    :return: the first invalid command detected.

    """

    for cmd in cmds:
        # Make sure is actually a command and not "python3" or "python", which we don't need to handle.
        if not cmd[0] == '-':
            continue

        # Get the identifier of the command, not the argument of it.
        split_cmd = cmd.split('=')
        if not split_cmd[0] in valid_commands:
            return split_cmd[0]

    return False


def parse_commands(cmds):
    """

    Parse commands from command line into parameters for the simulation.

    :param cmds: list of commands from to be parsed into parameters.
    :return: return a SimulationParameters object of defaulted or parsed parameters.

    """

    simulation_settings = SimulationSettings()

    # If the user has requested '-help', display list of valid commands.
    if "-help" in cmds:
        display_commands()
        exit()

    # If an invalid command is detected, exit and let the user know.
    if cmd := identify_invalid_commands(cmds):
        raise AssertionError(f"Command '{cmd}' not found. Please use -help for list of valid commands.")

    # Loop through commands and parse them to assign their values to their respective parameters.
    for cmd in cmds:
        if not cmd[0] == '-':
            continue

        split_cmd = cmd.split('=')

        if split_cmd[0] == '-golang':
            simulation_settings.golang = True if split_cmd[1] == 'True' else False

        elif split_cmd[0] == '-optimize':
            if split_cmd[1] == 'distance' or split_cmd[1] == 'distance_travelled':
                simulation_settings.return_type = SimulationReturnType.distance_travelled
            elif split_cmd[1] == 'time_taken' or split_cmd[1] == 'time':
                simulation_settings.return_type = SimulationReturnType.time_taken
            else:
                raise AssertionError(f"Parameter '{split_cmd[1]}' not identifiable.")

        elif split_cmd[0] == '-iter':
            simulation_settings.optimization_iterations = int(split_cmd[1])

        elif split_cmd[0] == '-verbose':
            simulation_settings.verbose = True if split_cmd[1] == 'True' else False

        elif split_cmd[0] == '-route_visualization':
            simulation_settings.route_visualization = True if split_cmd[1] == 'True' else False

        elif split_cmd[0] == '-race_type':
            if not split_cmd[1] in ['ASC', 'FSGP']:
                raise AssertionError(f"Invalid race type {split_cmd[1]}. Please enter 'ASC' or 'FSGP'.")
            simulation_settings.race_type = split_cmd[1]

        elif split_cmd[0] == '-granularity':
            simulation_settings.granularity = split_cmd[1]

    return simulation_settings


def run_unoptimized_and_export(input_speed=None, values=None, race_type="ASC", granularity=1, golang=True):
    """

    Export simulation data.

    :param input_speed: defaulted to 30km/h, an array of speeds that the Simulation will use.
    :param values: defaulted to what was outputted by now-deprecated SimulationResults object, a tuple of strings that
    each correspond to a value or array that the Simulation will export. See Simulation.get_results() for valid keys.
    :param race_type: define the race type, either "ASC" or "FSGP"
    :param granularity: define the granularity of Simulation speed array
    :param golang: define whether GoLang
    implementations should be used.

    """

    #  ----- Load initial conditions ----- #

    if race_type == "ASC":
        initial_conditions_path = config_directory / "initial_conditions_ASC.json"
    else:
        initial_conditions_path = config_directory / "initial_conditions_FSGP.json"

    with open(initial_conditions_path) as f:
        initial_conditions = json.load(f)

    # ----- Load from settings_ASC.json -----

    if race_type == "ASC":
        config_path = config_directory / "settings_ASC.json"
    else:
        config_path = config_directory / "settings_FSGP.json"

    with open(config_path) as f:
        model_parameters = json.load(f)

    # Build simulation model
    simulation_builder = SimulationBuilder() \
        .set_initial_conditions(initial_conditions) \
        .set_model_parameters(model_parameters, race_type) \
        .set_golang(golang) \
        .set_return_type(SimulationReturnType.void) \
        .set_granularity(granularity)

    simulation_model = simulation_builder.get()

    driving_hours = simulation_model.get_driving_time_divisions()

    if input_speed is None:
        input_speed = np.array([30] * driving_hours)
    if values is None:
        values = ["default"]

    simulation_model.run_model(speed=input_speed, plot_results=False, verbose=False, route_visualization=False)
    results_array = simulation_model.get_results(values)

    return results_array


def parse_data(data_name: str, save: bool = True):
    # Load your CSV data into a DataFrame
    cwd = os.getcwd()
    data_path = os.path.join(cwd, f"data/{data_name}.csv")
    df = pd.read_csv(data_path, header=3)

    # Pivot the DataFrame to transform it into the desired format
    pivot_df = df.pivot(index='_time', columns='_field', values='_value')

    # Save the transformed data to a new CSV file
    if save:
        pivot_df.to_csv('transformed_data.csv')

    return pivot_df


def run_simulation_from_data():
    # Get the data collected from Daybreak as a dataframe
    data = parse_data('DAYBREAK_DATA', save=False)
    data.reset_index(inplace=True)
    times = data["_time"].to_numpy()
    velocity_ms = np.nan_to_num(data["vehicle_velocity"].to_numpy())
    velocity_kmh = np.abs(velocity_ms) * 3.6

    begin: datetime.datetime = datetime.datetime.fromisoformat(times[0])
    subsequent: datetime.datetime = datetime.datetime.fromisoformat(times[1])
    end: datetime.datetime = datetime.datetime.fromisoformat(times[-1])

    simulation_duration = int(end.timestamp()) - int(begin.timestamp())
    seconds_per_datapoint = int(subsequent.timestamp()) - int(begin.timestamp())

    print(f"Duration in seconds: {simulation_duration}")
    print(f"Granularity: {seconds_per_datapoint}")

    start_hour: int = begin.hour - 8  # subtraction is conversion from UTC to PST
    initial_battery_charge: float = 1.0  # Arbitrary

    # Acquired from placing pins on Google Maps
    origin_coord = [49.26157652975386, -123.2459024292226]
    current_coord = [49.26157652975386, -123.2459024292226]
    dest_coord = [49.26153504243344, -123.24598507238346]
    waypoints = [[49.261111869797844, -123.24558245177245], [49.26144238729593, -123.24620121606667]]

    tick: int = 1
    lvs_power_loss: float = 0.0  # Arbitrary

    gis_force_update: bool = False
    weather_force_update: bool = False

    granularity: float = 3600 / seconds_per_datapoint

    model_parameters = {
        "origin_coord": origin_coord,
        "dest_coord": dest_coord,
        "waypoints": waypoints,
        "lvs_power_loss": lvs_power_loss,
        "tick": tick,
        "simulation_duration": simulation_duration
    }

    initial_conditions = {
        "current_coord": current_coord,
        "start_hour": start_hour,
        "initial_battery_charge": initial_battery_charge,
        "gis_force_update": gis_force_update,
        "weather_force_update": weather_force_update
    }

    builder = SimulationBuilder().set_granularity(granularity).set_golang(True).\
        set_model_parameters(model_parameters, "FSGP").set_initial_conditions(initial_conditions).\
        set_return_type(SimulationReturnType.void)
    model = builder.get()

    driving_indices = model.get_driving_time_divisions()

    # We are missing about 7 minutes of data
    padding_amount = driving_indices - len(velocity_kmh)

    velocity_kmh_padded = np.append(velocity_kmh, np.zeros(padding_amount))

    model.run_model(speed=velocity_kmh_padded, plot_results=False, verbose=False, route_visualization=False)

    # Analysis
    simulated_motor_consumed_energy = model.get_results(["motor_consumed_energy"])[0]
    actual_motor_power = data["bus_current"].to_numpy() * data["bus_voltage"].to_numpy()
    actual_motor_power = np.append(actual_motor_power, np.zeros(padding_amount))
    actual_motor_consumed_energy = np.append(np.repeat(actual_motor_power, seconds_per_datapoint), 0)

    timestamps = np.arange(0, len(actual_motor_consumed_energy))

    plt.plot(timestamps, actual_motor_consumed_energy, label="Actual Energy")
    plt.plot(timestamps, simulated_motor_consumed_energy, label="Simulated Energy")
    plt.legend()
    plt.show()
    plt.savefig("Figure")

    print("Success!")


if __name__ == "__main__":
    main()
