from pybricks.hubs import TechnicHub
from pybricks.parameters import Port
from pybricks.pupdevices import Motor

hub = TechnicHub()

motor = Motor(Port.A)
motor.run_time(500, 1000)
