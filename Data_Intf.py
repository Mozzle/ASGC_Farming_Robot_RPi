import time
import pigpio
import I2C_Packets
from subprocess import call

SDA_PIN=18
SCL_PIN=19

I2C_ADDR=9

C_FALSE=0
C_TRUE=1

pkt_rec_count = 0
pkt_success_count = 0

''' ------------------------------------------------------------------------
i2c_loop

   The main callback loop that is called whenever BSC (Broadcom Serial
   Controller) activity is detected. Handles receipt, processing, and
   responding to I2C packets from the Nucleo Board.
------------------------------------------------------------------------ '''
def i2c_loop(id, tick):
   global pkt_rec_count
   global pkt_success_count

   status, bytes_rec, data = pi.bsc_i2c(I2C_ADDR) #status, num bytes, data

   # If we received data
   if bytes_rec:
      #print(data[:-1])
      pkt_rec_count += 1

      # If the received data length does not match the expected packet size
      if bytes_rec is not I2C_Packets.RPI_PACKET_MAX_LENGTHS[data[I2C_Packets.PACKET_ID]]:
         # Error of some kind
         print("ERROR: Packet length mismatch! Len:" + str(bytes_rec))
         print(data)
         # Send back a 'data not received' pkt


      # Match the pkt_id
      # -------------------------- ERROR PKT ID ----------------------------
      if data[I2C_Packets.PACKET_ID] == I2C_Packets.RPI_ERR_PKT_ID:
         print("Yeah!")

      # -------------------------- GCODE PKT ID ----------------------------
      elif data[I2C_Packets.PACKET_ID] == I2C_Packets.RPI_GCODE_PKT_ID and bytes_rec >= (I2C_Packets.RPI_PACKET_MAX_LENGTHS[I2C_Packets.RPI_GCODE_PKT_ID] - I2C_Packets.RPI_PACKET_PAD_LENGTH):
         # Parse the data into the packet struct
         pkt = I2C_Packets.RPI_I2C_Packet_GCode(data)

         # If packet is valid
         if pkt.valid == C_TRUE:
            # Send the gcode to the SKR MINI E3 via the terminal
            call(["echo", pkt.gcode_str, ">>", "/tmp/printer/"])

            if pkt.gcode_str == "G28 0123456789012345678901234567890123":
               pkt_success_count += 1

            print("GCode [" + str(pkt_success_count) + "/" + str(pkt_rec_count) + "]: " + pkt.gcode_str)


      # ------------------------ AHT20 DATA PKT ID -------------------------
      elif data[I2C_Packets.PACKET_ID] == I2C_Packets.RPI_AHT20_PKT_ID:
         print("Else!")

      # ------------------------ WATER DATA PKT ID -------------------------
      elif data[I2C_Packets.PACKET_ID] == I2C_Packets.RPI_WATER_DATA_PKT_ID:
         pass

      # ----------------------- BUTTONS DATA PKT ID ------------------------
      elif data[I2C_Packets.PACKET_ID] == I2C_Packets.RPI_BUTTONS_PKT_ID:
         pass

      # ---------------------- NET POT STATUS PKT ID -----------------------
      elif data[I2C_Packets.PACKET_ID] == I2C_Packets.RPI_NET_POT_STATUS_PKT_ID:
         pass

      # ------------------ GET AXES DATA REQUEST PKT ID --------------------
      elif data[I2C_Packets.PACKET_ID] == I2C_Packets.RPI_GET_AXES_POS_PKT_ID:
         pass

      # -------------------------- DEFAULT CASE ----------------------------
      else:
         print("okay")



''' ------------------------------------------------------------------------
   Program Entry Point
   ------------------------------------------------------------------------ '''
# Start the interface
pi = pigpio.pi()

if not pi.connected:
   exit()

# Add pull-ups in case external pull-ups haven't been added
pi.set_pull_up_down(SDA_PIN, pigpio.PUD_UP)
pi.set_pull_up_down(SCL_PIN, pigpio.PUD_UP)

print("Starting I2C Data Interface...")

# Respond to BSC slave activity, registering the i2c_loop as callback function
e = pi.event_callback(pigpio.EVENT_BSC, i2c_loop)
pi.bsc_i2c(I2C_ADDR) # Configure BSC as I2C slave
time.sleep(800)

# If the interface exits, gracefully shut down
e.cancel()
pi.bsc_i2c(0) # Disable BSC peripheral
pi.stop()

