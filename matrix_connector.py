import serial
from matrix import Matrix

COMMANDS = {
   "brightness": 0x00,
   "pattern": 0x01,
   "bootloader": 0x02,
   "sleep": 0x03,
   "animate": 0x04,
   "panic": 0x05,
   "drawbw": 0x06,
   "stagecol": 0x07,
   "flushcols": 0x08,
   "startgame": 0x10,
   "gamecontrol": 0x11,
   "gamestatus": 0x12,
   "version": 0x20
}

PATTERNS = {
   "percentage": 0x00,
   "gradient": 0x01,
   "doublegradient": 0x02,
   "lotush": 0x03,
   "zigzag": 0x04,
   "full": 0x05,
   "panic": 0x06,
   "lotusv": 0x07
}

GAMES = {
   "snake": 0,
   "pong": 1,
}

GAME_CONTROLS = {
   "pong": {
      "far_player": {
         "left": 2,
         "right": 3
      },
      "close_player": {
         "left": 5,
         "right": 6,
      },

      "stop": 4
   },

   "snake": {
      "up": 0,
      "down": 1,
      "left": 2,
      "right": 3,
      "stop": 4
   }
}

class MatrixConnector:
   """Represents a connection to the LED matrix, essentially forming an API for interacting with it without directly using serial."""
   CONNECTION: serial.Serial
   PORT = "COM3"
   BAUD_RATE = 115200
   MAGIC_BYTE_A = 0x32
   MAGIC_BYTE_B = 0xAC

   def __init__(self, matrix, port: str|None = None):
     if port: self.PORT = port

     self.matrix = matrix

   def is_connected(self): 
      """Returns whether we are connected to the LED matrix"""
      try:
         if not self.CONNECTION:
            return False
         return self.CONNECTION.is_open
      except AttributeError: return False
     
   def connect(self, port: str|None = None):
      """Connect to the LED matrix given a port"""
      self.CONNECTION = serial.Serial(
           port if port != None else self.PORT,
           self.BAUD_RATE
      )
    
   def close(self):
      """Disconnect from the LED matrix"""
      self.CONNECTION.close()

   def send_command(self, command_id, parameters) -> None:
      """Send a particular command to the LED matrix"""
      succeeded = False
      while not succeeded:
         try: 
            if self.CONNECTION: self.CONNECTION.write([self.MAGIC_BYTE_A, self.MAGIC_BYTE_B, command_id] + parameters)
            succeeded = True
         except serial.SerialTimeoutException: 
            print("Failed to write")
   
   def send_command_with_response(self, command_id, parameters, length: int|None = 32) -> bytes:
      """Send a particular command to the LED matrix and read a response from the matrix"""
      succeeded = False
      while not succeeded:
         try: 
            if self.CONNECTION: self.CONNECTION.write([self.MAGIC_BYTE_A, self.MAGIC_BYTE_B, command_id] + parameters)
            succeeded = True
         except serial.SerialTimeoutException: 
            print("Failed to write")

      if length == None:
         res = self.CONNECTION.read_all()
      else:
         res = self.CONNECTION.read(length)
      if res:
         return res
      return b''
    
   def eval_boolean_returned(self, command_response: bytes) -> bool:
      """Convert a command response to a boolean value"""
      return bool(command_response[0])
    
   def set_brightness(self, brightness: int):
      """Set the LED matrix's overall brightness, from 0 to 255"""
      assert 0 <= brightness <= 255
      self.send_command(COMMANDS["brightness"], [brightness])

   def set_pattern(self, pattern: bytes, percentage: int = 100):
      """Set the pattern displayed on the LED matrix"""
      assert (
         pattern != PATTERNS["percentage"] and percentage == None or
         pattern == PATTERNS["percentage"] and 0 <= percentage <= 100
      )
      if percentage: args = [pattern, percentage]
      else: args = [pattern]
      self.send_command(COMMANDS["pattern"], args)

   def bootloader(self):
      """Place the LED matrix into bootloader mode, for flashing a new image"""
      self.send_command(COMMANDS["bootloader"], [])

   def set_sleep(self, asleep: bool = False):
      """Set the matrix to either be sleeping or not"""
      self.send_command(COMMANDS["sleep"], [asleep])
   
   def get_sleep(self) -> bool:
      """Get whether the LED Matrix is sleeping. This seems to have freaky behavior, so ideally refrain from using it."""
      return self.eval_boolean_returned(self.send_command_with_response(COMMANDS["sleep"], [], True))
   
   def set_is_animating(self, animating: bool):
      """Set the matrix's animation to either be playing or not"""
      self.send_command(COMMANDS["animate"], [animating])

   def get_is_animating(self):
      """Return whether the matrix is set to play the current animation"""
      return self.eval_boolean_returned(self.send_command_with_response(COMMANDS["animate"], [], True))
   
   def panic(self):
      """Raise an LED matrix firmware panic for debug purposes"""
      self.send_command(COMMANDS["panic"], [])
   
   def draw_bw_image(self, image: list[bytes]):
      """Draw a given black and white image to the matrix"""
      self.send_command(COMMANDS["drawbw"], image)

   def stage_column(self, column: int, values: list[int]):
      """Blit a column of values to the LED matrix. This will display nothing until the columns are flushed with flush_columns"""
      args = [column]
      args.extend(values)
      self.send_command(COMMANDS["stagecol"], args)

   def flush_columns(self):
      """Flush all of the columns blitted with stage_column"""
      self.send_command(COMMANDS["flushcols"], [])

   def start_game(self, game: int):
      """Start a game with a given ID"""
      self.send_command(COMMANDS["startgame"], [game])

   def send_game_command(self, command: int):
      """Send a command to the currently running game"""
      self.send_command(COMMANDS["gamecontrol"], [command])

   def get_game_status(self):
      """Get the status of the currently running game"""
      return self.send_command_with_response(COMMANDS["gamestatus"], [], None)
   
   def decode_game_status(self, status: bytes):
      """Decode the value returned from get_game_status"""
      status_str = status.decode("ascii").splitlines()
      status_str.reverse()

      game_state = None
      current_game = None

      for message in status_str:
         if "step" in message:
            current_game = message.replace(" Game step", "").lower()
         else:
            message_segments = message.split(" ")
            game_state = {}
            i = 0
            while i < len(message_segments):
               game_state[message_segments[i]] = message_segments[i+1].removesuffix(",")
               i += 2
         if current_game == "pong" or current_game and game_state:
            break

      return current_game, game_state
   
   def get_fw_version(self):
      """Get the LED matrix firmware version"""
      return self.send_command(COMMANDS["version"], [], True)
   
   def _stage_matrix_column(self, column):
      """Blit a column from the internal matrix representation to the actual matrix"""
      self.stage_column(column, self.matrix.get_column_values(column))

   def _stage_whole_matrix(self):
      """Blit all columns from the internal matrix representation to the actual matrix"""
      for column in range(0, 9):
         self._stage_matrix_column(column)
   
   def flush_matrix(self):
      """Flush every column on the LED matrix"""
      self._stage_whole_matrix()
      self.flush_columns()
   
if __name__ == "__main__":
   # Create a basic matrix connector instance
   matrix = MatrixConnector(Matrix())