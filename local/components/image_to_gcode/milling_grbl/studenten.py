from datetime import datetime
import serial.tools.list_ports
from pynput import keyboard
import time
import threading
import pika
import queue
from components.image_to_gcode.milling_grbl.controller import Controller
import time

class Application:
    
    def __init__(self):
        self.port_list = self.search_com_ports()
        self.file_path = 'test.tap'
        
    def search_com_ports(self) -> list:
        """Searches for all available com ports"""
        ports = [comport.device for comport in serial.tools.list_ports.comports()]

        if len(ports) == 0:
            print("Error: Device / Port can not be found or can not be configured")
            
        return ports
    
    def activate_gui(self, com_port) -> None:
        """Activates all Widgets after start from GUI and serial controller"""
        try:
            self.controller = Controller(com_port=com_port[0], baudrate=115200)
            self.controller.start_up()
            # self.calc_steps()
        except ConnectionError as ce:
            raise ConnectionError('No connection to the controller [GRBL] is possible.')
    


    def homing(self) -> None:
        """Triggers the homing function of the grbl controller"""
        self.controller.homing()
        
    def controller_send_cmd(self, cmd) -> None:
        self.controller.send_cmd(f"{cmd}")
        
    def set_nullpunkt_XY(self):
        """Triggers the setting of the zero"""
        self.controller.set_zero_point_XY()
        
    def set_nullpunkt_Z(self):
        """Triggers the setting of the zero"""
        self.controller.set_zero_point_Z()
        
    def set_nullpunkt_XYZ(self):
        """Triggers the setting of the zero"""
        self.controller.set_zero_point_XYZ()
    
        
    def start_file_execution(self, gcode) -> None:
        """Reads a file and iterates over it, sending each line individually to the controller"""

        # f = open(self.file_path,'r')
        f = gcode
        def loop():
   
            for line in f:
                self.controller.send_cmd(line)

        thread = threading.Thread(target=loop)
        thread.run()
        
        
        
def main() -> None:

    app = Application()    # Kickstart the main application
    app.activate_gui(com_port=app.port_list)
    app.controller_send_cmd('G0 X-300 Y-500')
    app.set_nullpunkt_XY()
    app.controller_send_cmd('G0 Z-129')
    app.set_nullpunkt_Z()
    
    app.start_file_execution()
    
    # time.sleep(1)
    app.controller_send_cmd('$H')


if __name__ == "__main__":
    main()
    
    