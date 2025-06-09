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
   CONNECTION: serial.Serial = None
   PORT = "COM3"
   BAUD_RATE = 115200
   MAGIC_BYTE_A = 0x32
   MAGIC_BYTE_B = 0xAC

   def __init__(self, matrix, port: str = None):
     if port: self.PORT = port

     self.matrix = matrix

   def is_connected(self):
      if not self.CONNECTION:
         return False
      return self.CONNECTION.is_open
     
   def connect(self, port: str = None):
      self.CONNECTION = serial.Serial(
           port if port != None else self.PORT,
           self.BAUD_RATE
      )
    
   def close(self):
      self.CONNECTION.close()

   def send_command(self, command_id, parameters, with_response=False, length: int = 32):

      self.CONNECTION.write([self.MAGIC_BYTE_A, self.MAGIC_BYTE_B, command_id] + parameters)

      

      if with_response:
         if length == None:
            res = self.CONNECTION.read_all()
         else:
            res = self.CONNECTION.read(length)
         return res
    
   def eval_boolean_returned(self, command_response: bytes) -> bool:
      return bool(command_response[0])
    
   """
   Set the LED Matrix overall brightness, from 0 to 255
   """
   def set_brightness(self, brightness: int):
      assert 0 <= brightness <= 255
      self.send_command(COMMANDS["brightness"], [brightness])

   def set_pattern(self, pattern: bytes, percentage: int = None):
      assert (
         pattern != PATTERNS["percentage"] and percentage == None or
         pattern == PATTERNS["percentage"] and 0 <= percentage <= 100
      )
      if percentage: args = [pattern, percentage]
      else: args = [pattern]
      self.send_command(COMMANDS["pattern"], args)

   def bootloader(self):
      self.send_command(COMMANDS["bootloader"], [])

   def set_sleep(self, asleep: bool = False):
      self.send_command(COMMANDS["sleep"], [asleep])
   
   """
   Get whether the LED Matrix is sleeping. This seems to have freaky behavior, don't use it probably.
   """
   def get_sleep(self) -> bool:
      return self.eval_boolean_returned(self.send_command(COMMANDS["sleep"], [], True))
   
   def set_is_animating(self, animating: bool):
      self.send_command(COMMANDS["animate"], [animating])

   def get_is_animating(self):
      return self.eval_boolean_returned(self.send_command(COMMANDS["animate"], [], True))
   
   def panic(self):
      self.send_command(COMMANDS["panic"], [])
   
   def draw_bw_image(self, image: list[bytes]):
      self.send_command(COMMANDS["drawbw"], image)

   def stage_column(self, column: int, values: list[int]):
      args = [column]
      args.extend(values)
      self.send_command(COMMANDS["stagecol"], args)

   def flush_columns(self):
      self.send_command(COMMANDS["flushcols"], [])

   def start_game(self, game: int):
      
      self.send_command(COMMANDS["startgame"], [game])

   def send_game_command(self, command: int):
      self.send_command(COMMANDS["gamecontrol"], [command])

   def get_game_status(self):
      return self.send_command(COMMANDS["gamestatus"], [], True, None)
   
   def decode_game_status(self, status: bytes):
      status_str = status.decode("ascii").splitlines()
      status_str.reverse()

      game_state = None
      current_game = None

      for message in status_str:
         if "step" in message:
            current_game = message.replace(" Game step", "").lower()
         else:
            print(message)
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
      return self.send_command(COMMANDS["version"], [], True)
   
   def _stage_matrix_column(self, column):
      self.stage_column(column, self.matrix.get_column_values(column))

   def _stage_whole_matrix(self):
      for column in range(0, 9):
         self._stage_matrix_column(column)
   
   def flush_matrix(self):
      #self.matrix.log_state()
      self._stage_whole_matrix()
      self.flush_columns()
   

# Go to sleep and check the status
if __name__ == "__main__":
   matrix = MatrixConnector()

      
