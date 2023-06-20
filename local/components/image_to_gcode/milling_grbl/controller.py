from components.image_to_gcode.milling_grbl.grblsender import GRBLSender

class Controller:
    # DT - Estimated execution time of a single jog command in seconds
    DISTANCE_TIME = 0.0336697212698413

    def __init__(self, com_port: str, baudrate: int = 115200) -> None:
        self.grbl = GRBLSender(com_port, baudrate)

   
    def start_up(self) -> None:
        """Activate startup process of the cnc milling machine"""
        self.grbl.start_up_process()
        self._write_grbl_settings()
        self.homing()
    
    def reset_buffers(self) -> None:
        """Resets all buffer"""
        self.grbl.reset_buffers()


    def _write_grbl_settings(self) -> None:
        """Sends all config information to grbl"""
        config = open("components/image_to_gcode/milling_grbl/grbl.config")

        for configuration in config:
            self.send_cmd(configuration)


    def homing(self) -> None:
        """Initiates the homing process"""
        self.send_cmd("$H")


    def kill_alarm(self, homing=False) -> None:
        """Sends grbl a kill alarm command to keep the router operational after an alarm. Likewise, an optional homing can be performed

        Args:
            homing (bool, optional): If an additional homing is to be performed. Defaults to False.
        """
        self.send_cmd("$X")

        if homing:
            self.reset_buffers()
            self.send_cmd("$H")


    def set_zero_point(self) -> None:
        """Set zero points for x and y axis"""
        self.send_cmd(f"G92 X0 Y0")
        
    def set_zero_point_XY(self) -> None:
        """Set zero points for x and y axis"""
        self.send_cmd(f"G92 X0 Y0")
        
    def set_zero_point_Z(self) -> None:
        """Set zero points for x and y axis"""
        self.send_cmd(f"G92 Z0")
        
    def set_zero_point_XYZ(self) -> None:
        """Set zero points for x and y axis"""
        self.send_cmd(f"G92 X0 Y0 Z0")
        
        


    def go_to_xy_zero_points(self) -> None:
        """Go to zero points [only x and y axis]"""
        self.send_cmd(f"G53 G0 Z-1")
        self.send_cmd(f"G21 G90")
        self.send_cmd(f"G1 X0 Y0 F1600")

    def stop_jog(self) -> None:
        """Jog Cancel"""
        self.realtime_command('\x85')


    def realtime_command(self, cmd) -> None:
        """Sends a realtime command to grbl -> does not wait for response [fire and forget]"""
        cmd = (cmd + "\r\n").encode()
        self.grbl.send_realtime_command(cmd)

    
    def send_cmd(self, cmd: str) -> None:
        """Remove spaces at the beginning and at the end of the string and 
            transforms gcode string into byte"""
        cmd = (cmd.strip()  + "\r\n").encode()

        return self.grbl.send_wait_command(cmd)


    def z_probe(self) -> None:
        """Performs an z-probe -> was taken from Candle"""
        self.send_cmd(f"G21 G91 G38.2Z-10F100")
        self.send_cmd(f"G0Z1")
        self.send_cmd(f"G38.2Z-2F10")
        self.send_cmd(f"G92Z1.6")
        self.send_cmd(f"G0Z3.4")
        self.send_cmd(f"G90")

    
    def calc_xy_distance(self, feed) -> float:
        """calculates the incremental distance of jog command for x and y

        Args:
            feed (int): feed of the cnc  mill

        Returns:
            float: distance [in mm] 
        """

        if feed > 2300:
            return (2300 / 60) *  Controller.DISTANCE_TIME

        return (feed / 60) *  Controller.DISTANCE_TIME


    def calc_z_distance(self, feed) -> float:
        """calculates the incremental distance of jog command for z

        Args:
            feed (int): feed of the cnc  mill

        Returns:
            float: distance [in mm] 
        """
        if feed >= 900:
            return (900/60) * Controller.DISTANCE_TIME
        
        return (feed/60) * Controller.DISTANCE_TIME


    def exit(self) -> None:
        """Disconnecting the connection to grbl"""
        self.grbl._exit()

