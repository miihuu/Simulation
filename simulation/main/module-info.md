# Main

## Table of Contents
1. [Overview](#module-overview)
2. [Classes](#classes)
   1. [Simulation](#simulation)
      1. init()
      2. run_model()
      3. get_results()
      4. was_successful()
      5. get_distance_before_exhaustion()
      6. get_driving_time_divisions()
   2. [Model](#model)
      1. init()
      2. run_simulation_calculations()
      3. get_results()
3. [Additional Notes](#additional-notes)

## Module Overview

The main module brings together all the components and environment data to simulate
our solar-powered vehicles. Another primary objective of this module is to expose
an interface for clients to extract data from Simulation instances. 

## Classes

### Simulation
The Simulation class is the core of Simulation. This class instantiates the car components and acquires 
environment data.

#### init()
Do not directly instantiate a Simulation object. Use the SimulationBuilder class instead. See [SimulationBuilder](../utils/module-info#SimulationBuilder) for details and configuration of a Simulation instance.

#### run_model()
Simulate the car for the entire duration of the race given a `speed` input. This function is mostly a wrapper around
`Model.run_simulation_calculations`, which performs the actual calculations, that handles the considerable input and 
output processing that is required.
It accepts the following parameters:
- `speed` of type `NumPy.ndarray`: array of driving speeds in km/h that is the primary dependent variable to Simulation. Must be of length equal to `get_driving_time_divisions()`.
- `plot_results=False` of type `bool`: flag that controls whether results will be plotted.
- `verbose=False` of type `bool`: flag that controls whether verbose plotting and printing is used.
- `route_visualization=False` of type `bool`: flag that controls whether the route should be plotted.
- `plot_portion=(0.0, 1.0)` of type `tuple[float, float]`: Define the portion of the simulation that should be plotted through beginning and end percentages. Does nothing if `plot_results=False`.
- `is_optimizer=False` of type `bool`: flag that is used by optimizers to reduce verbosity.
Returns either the `tine_taken`, `distance_travelled`, both, or nothing depending on the `SimulationReturnType` configured.

#### get_results()
Use this method to extract simulation data.

It accepts the following parameters:
- `values` of type `NumPy.ndarray | list | tuple | set | str`: either a single string, or an iterable of keys (strings) defining which values to be extracted. See [additional notes](#additional-notes) for valid keys. Also accepts `"default"` to return the values that were previously contained within the now-deprecated `SimulationResults` object. 
It returns the following values:
- `results` of type `list | NumPy.ndarray | float`: either a single array or value, if a single key was provided in `values`, or a list of values corresponding to the provided keys in `values`, in the order that they were provided.

Example:
`get_results(["solar_irradiances", "delta_energy"])` will return a `list` with length `2` where the first element is value corresponding to `solar_irradiances`, and the second element is the value corresponding to `delta_energy`.

#### was_successful()
Return whether the simulation was physically consistent. Currently, the metric that is verified is whether
state of charge did not fall below `0%`, indicating that the speed input is physically achievable.

#### get_distance_before_exhaustion()
Return the distance travelled in km before state of charge falls below `0%`. Can be chained with
`was_successful()` to verify whether this happens, as this method is not well-defined if this does not occur.

#### get_driving_time_divisions()
Returns the number of time divisions (length of a time division is based on granularity) that the car is permitted to 
be driving. Dependent on granularity and rules in competition configuration files. 

---

### Model
The Model class executes the simulation calculations and stores the result. This class should be considered to
be a mutable container owned by a Simulation instance, and not accessed directly nor instantiated otherwise.
#### init() 
Do not instantiate a Model.
#### run_simulation_calculations()
Perform all simulation calculations in order to fully simulate the car for the entire simulation duration.
#### get_results()
Do not call `get_results` on a Model, instead call it on the Simulation instance which owns it.

## Additional Notes

When reading "Array of `x`", interpret as shorthand for "array containing the value of `x` at every tick/moment simulated".

**Valid Keys:**
1. `speed_kmh`: Array of the car's speed in km/h.
2. `distances`: Array of the car's distance travelled in km. 
3. `state_of_charge`: Array of the battery's state of charge as a decimal (between 0 and 1).
4. `delta_energy`: Array of delta energy processed by the battery in Joules.
5. `solar_irradiances`: Array of solar irradiances experienced by the solar arrays in W/m^2.
6. `wind_speeds`: Array of wind speeds experienced by the car in the direction opposite to the bearing of the vehicle in m/s.
7. `gis_route_elevations_at_each_tick`: Array of elevations of the car in m.
8. `cloud_covers`: Array of cloud cover as a percentage (as a decimal).
9. `distance`: Array of distances travelled between each tick in meters.
10. `route_length`: Length of the route that will be simulated in km.
11. `time_taken`: Time taken to reach the finish line (or simulation duration, if the finish line was not reached) in seconds.
12. `tick_array`: Array of tick indices.
13. `timestamps`: Array of timestamps in UNIX time.
14. `time_zones`: Array of time zones experienced by the car as integers corresponding to the difference in hours from UTC.
15. `cumulative_distances`: Array of cumulative distance in meters, effectively the distance travelled at the current point.
16. `closest_gis_indices`: Array of indices corresponding to the GIS coordinate that the car is at.
17. `closest_weather_indices`: Array of indices corresponding to the weather forecast that the car is at.
18. `path_distances`: Array of distances between path coordinates.
19. `max_route_distance`: Length of the route that will be simulated in meters.
20. `gis_vehicle_bearings`: Array of the azimuth angle of the vehicle at every location.
21. `gradients`: Array of road gradient as an angle in degrees of the vehicle at every location.
22. `absolute_wind_speeds`: Array of wind speeds in m/s experienced by the car. 
23. `wind_directions`: Array of wind directions in degrees (meteorological standard).
24. `lvs_consumed_energy`: Array of consumed energy by our low-voltage systems in Joules.
25. `motor_consumed_energy`: Array of energy consumed by our motor in Joules.
26. `array_produced_energy`: Array of energy produced by our solar arrays in Joules.
27. `regen_produced_energy`: Array produced by our regenerative braking in Joules.
28. `not_charge`: Boolean array indicating when we are not able to charge. 
29. `consumed_energy`: Array of total energy consumption in Joules.
30. `produced_energy`: Array of total produced energy in Joules.
31. `time_in_motion`: Time the car spent in motion in seconds.
32. `final_soc`: The final state of charge at the end of simulation, or when the car reaches the finish line, as a decimal percentage.
33. `distance_travelled`: Distance travelled by the car during the course of simulation in km.
34. `map_data_indices`: Array of indices corresponding to a map coordinate.
35. `path_coordinates`: Array of coordinates (latitude, longitude) of the car at every point, formatted as a two-dimensional NumPy array.
36. `raw_soc`: Array of the car's state of charge before clipped to be a valid percentage.
