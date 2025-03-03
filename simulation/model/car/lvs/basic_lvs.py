from simulation.model.car.lvs.base_lvs import BaseLVS
from simulation.common import DayBreak


class BasicLVS(BaseLVS):

    def __init__(self, consumed_energy):
        super().__init__(consumed_energy)

    def get_consumed_energy(self, tick):
        """
            Get the energy consumption of the Low Voltage System (current * voltage * time)

            :param tick - (int) tick time passed
            :returns: consumed_energy - (number) value of energy consumed
        """

        # Constants for car are set in config > {car_name}.json
        self.consumed_energy = DayBreak.lvs_current * DayBreak.lvs_voltage * tick
        return self.consumed_energy
