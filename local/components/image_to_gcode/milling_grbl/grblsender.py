import serial
import re
import time
import threading
import csv

from typing import List

# TODO: Improvement - tracking of grbl buffer

class GRBLSender:

    def __init__(self, com_port: str, baudrate: int = 115200) -> None:
        """Creates a grbl sender consisting of a com_port and a baudrate. The default baudrate is 115200 in version > 0.8. If you use an older version you should use a baudrate of 9600.

        Args:
            com_port (str): Communication port (example: "COM3")
            baudrate (int, optional): Unit of communication technology and represents the step speed. Defaults to 115200.
        """
        self.serial = self.open_serial_port(com_port, baudrate)
        self.terminator_ok_or_error_regex = re.compile("^(ok|error|alarm|.msg:reset).*")
        self.error_alarm_messages = {line[0]: [line[1], line[2]] for line in csv.reader(open('error_alarm.csv', encoding='UTF8'), delimiter=";")}
        self.lock = threading.Lock()



    def open_serial_port(self, com_port, baudrate):

        try:
            return serial.Serial(com_port, baudrate)
        except ValueError as ve:
            print(f"Parameter are out of range, e.g. baudrate: {baudrate}")
            raise ValueError('Parameter are out of range, e.g. baudrate')
        except serial.SerialException as se:
            print(f"Device can not be found or can not be configured - port {com_port}")
            raise serial.SerialException('Device / Port can not be found or can not be configured')


    def start_up_process(self) -> None:
        """Wait for grbl to print the welcome message and resets the buffers"""

        time.sleep(3)

        self.reset_buffers()

        print(f"number of bytes in the input buffer: {self.serial.in_waiting}")
        print(f"number of bytes in the output buffer: {self.serial.out_waiting}")


    def reset_buffers(self):
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()
        self.serial.flush()


    def _exit(self) -> None:
        """Close port immediately"""
        self.serial.close()

        print(f"port is closed")


    def send_realtime_command(self, byte_cmd: bytes) -> None:
        self.serial.write(byte_cmd)


    def _readline(self) -> str:
        """Read a line from grbl and remove leading and trailing whitespaces"""

        s = self.serial.readline().decode().strip()

        print(f"<< {s} \n")
        return s.lower()
    

    def _send_command(self, cmd: str) -> None:
        """Send a command to grbl"""
        print(f">> {cmd.decode().rstrip()}")
        self.serial.write(cmd)

    

    def send_wait_command(self, cmd: str) -> List[str]:
        """Sends a command to the CNC mill and waits for reponse. 

        Args:
            cmd (str): Command to be executed by the cnc milling machine

        Returns:
            List[str]: A list will be returned, which contains the complete output of the cnc mill over the runtime of the command.
        """

        with self.lock:
            print("-----------------------------------------")
            print(f"Command: {cmd}")
            self._send_command(cmd)
            serial_answers = self._read_grbl_output()

            if serial_answers[0].startswith("error"):
                msg = [serial_answers[0]] + self.error_alarm_messages[serial_answers[0]]
                raise ValueError(cmd, msg)
            elif serial_answers[0].startswith("alarm"):
                msg = [serial_answers[0]] + self.error_alarm_messages[serial_answers[0]]
                raise ValueError(cmd, msg)
            
        return serial_answers
    

    def _read_grbl_output(self) -> List[str]:
        """Reads all ouput lines of the cnc mill until a termination criterion (in the form of an 'ok' message,  'error' message or 'alarm' message) is returned

        Returns:
            List[str]: Returns a list that contains all output information that was collected during the execution of the command. 
        """

        lines = []
        line = self._readline()
        while not self.terminator_ok_or_error_regex.match(line):
            print("run")
            lines.append(line)
            line = self._readline()
        
        self.serial.reset_input_buffer()

        lines.append(line)

        return lines