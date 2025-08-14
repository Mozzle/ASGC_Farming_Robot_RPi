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
currently_receiving_packet = False
packet_being_received = 0
pkt = None
pkt_chunk_index = 0

''' ------------------------------------------------------------------------
i2c_loop

   The main callback loop that is called whenever BSC (Broadcom Serial
   Controller) activity is detected. Handles receipt, processing, and
   responding to I2C packets from the Nucleo Board.
------------------------------------------------------------------------ '''
def i2c_loop(id, tick):
   global pkt_rec_count
   global pkt_success_count
   global currently_receiving_packet
   global packet_being_received
   global pkt

   status, bytes_rec, data = pi.bsc_i2c(I2C_ADDR) #status, num bytes, data

   # If we are in the process of receiving the chunks of a packet
   if currently_receiving_packet:
      if bytes_rec:
         if bytes_rec is not I2C_Packets.NUM_CHUNKS_PER_PACKET:
            # Error of some kind
            # Maybe send back a 'data not received' pkt
            print("ERROR: Packet length mismatch! Len:" + str(bytes_rec))
            print(data)
            # Need to reset and ignore the rest of the chunks

         # append the chunk to the packet we're receiving
         pkt.append(data)
         pkt_chunk_index += 1

         # If we have received all the chunks of the packet
         if pkt_chunk_index >= I2C_Packets.NUM_CHUNKS_PER_PACKET:
            # Process the completed packet
            parse_completed_packet(pkt)

            currently_receiving_packet = False
            pkt_chunk_index = 0
            pkt.clear()


         
         

   # If we are now receiving a new packet
   else:
      # If we received data
      if bytes_rec:
         #print(data[:-1])
         pkt_rec_count += 1
         pkt.append(data)
         currently_receiving_packet = True
         pkt_chunk_index += 1


def parse_completed_packet(pkt):
   if len(pkt) is not I2C_Packets.RPI_I2C_PACKET_SIZE:
      # Error of some kind
      # Maybe send back a 'data not received' pkt
      print("ERROR: Total Packet length mismatch! Len:" + str(len(pkt)))
      print(pkt)
      return
   
   # Match the pkt_id
   # -------------------------- ERROR PKT ID ----------------------------
   if pkt[I2C_Packets.PACKET_ID] == I2C_Packets.RPI_ERR_PKT_ID:
      print("Error Packet ID received!")

   # -------------------------- GCODE PKT ID ----------------------------
   elif pkt[I2C_Packets.PACKET_ID] == I2C_Packets.RPI_GCODE_PKT_ID and bytes_rec >= I2C_Packets.RPI_GCODE_PKT_LAST_VALID_BYTE:
      # Parse the data into the packet struct
      pkt = I2C_Packets.RPI_I2C_Packet_GCode(pkt)

      # If packet is valid
      if pkt.valid == C_TRUE:
         # Send the gcode to the SKR MINI E3 via the terminal
         call(["echo", pkt.gcode_str, ">>", "/tmp/printer/"])

         if pkt.gcode_str == "G28":
            pkt_success_count += 1

         print("GCode [" + str(pkt_success_count) + "/" + str(pkt_rec_count) + "]: " + pkt.gcode_str)


   # ------------------------ AHT20 DATA PKT ID -------------------------
   elif pkt[I2C_Packets.PACKET_ID] == I2C_Packets.RPI_AHT20_PKT_ID:
      print("Else!")

   # ------------------------ WATER DATA PKT ID -------------------------
   elif pkt[I2C_Packets.PACKET_ID] == I2C_Packets.RPI_WATER_DATA_PKT_ID:
      pass

   # ----------------------- BUTTONS DATA PKT ID ------------------------
   elif pkt[I2C_Packets.PACKET_ID] == I2C_Packets.RPI_BUTTONS_PKT_ID:
      pass

   # ---------------------- NET POT STATUS PKT ID -----------------------
   elif pkt[I2C_Packets.PACKET_ID] == I2C_Packets.RPI_NET_POT_STATUS_PKT_ID:
      pass

   # ------------------ GET AXES DATA REQUEST PKT ID --------------------
   elif pkt[I2C_Packets.PACKET_ID] == I2C_Packets.RPI_GET_AXES_POS_PKT_ID:
      pass

   # -------------------------- DEFAULT CASE ----------------------------
   else:
      print("ERROR: Unknown packet ID received!")

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

