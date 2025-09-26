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
last_rec_pkt_id = -1
gcode_full_str = ""

''' ------------------------------------------------------------------------
i2c_loop

   The main callback loop that is called whenever BSC (Broadcom Serial
   Controller) activity is detected. Handles receipt, processing, and
   responding to I2C packets from the Nucleo Board.
------------------------------------------------------------------------ '''
def i2c_loop(id, tick):
   global pkt_rec_count
   global pkt_success_count
   global last_rec_pkt_id
   global gcode_full_str

   status, bytes_rec, data = pi.bsc_i2c(I2C_ADDR) #status, num bytes, data

   # If we received data
   if bytes_rec:
      #print(data[:-1])
      pkt_rec_count += 1

      if data[I2C_Packets.PACKET_ID] >= I2C_Packets.I2CPackets.RPI_I2C_NUM_PKT_IDS:
         ack_pkt = I2C_Packets.RPI_I2C_Packet_ACK(C_FALSE)
         print("ERROR: Invalid packet ID received!")
         print("SENDING NACK PACKET")
         s, b, d = pi.bsc_i2c(I2C_ADDR, ack_pkt.raw)
         return


      # If the received data length does not match the expected packet size
      if bytes_rec is not I2C_Packets.RPI_PACKET_MAX_LENGTHS[data[I2C_Packets.PACKET_ID]]:
         # Error of some kind
         print("ERROR: Packet length mismatch! Len:" + str(bytes_rec))
         ack_pkt = I2C_Packets.RPI_I2C_Packet_ACK(C_FALSE)
         print("SENDING NACK PACKET")
         s, b, d = pi.bsc_i2c(I2C_ADDR, ack_pkt.raw)
         return


      # Match the pkt_id
      # -------------------------- ERROR PKT ID ----------------------------
      if data[I2C_Packets.PACKET_ID] == I2C_Packets.I2CPackets.RPI_ERR_PKT_ID:
         print("Yeah!")

      # -------------------------- GCODE 0 PKT ID ----------------------------
      elif data[I2C_Packets.PACKET_ID] == I2C_Packets.I2CPackets.RPI_GCODE_0_PKT_ID and bytes_rec == I2C_Packets.RPI_PACKET_MAX_LENGTHS[I2C_Packets.I2CPackets.RPI_GCODE_0_PKT_ID]:
         # Parse the data into the packet struct
         pkt = I2C_Packets.RPI_I2C_Packet_GCode_0(data)

         # If packet is valid
         if pkt.valid == C_TRUE:
            # Send the gcode to the SKR MINI E3 via the terminal
            gcode_full_str = pkt.gcode_str

            # Make and send the ACK packet
            ack_pkt = I2C_Packets.RPI_I2C_Packet_ACK(C_TRUE)
            s, b, d = pi.bsc_i2c(I2C_ADDR, ack_pkt.raw)
            # Set last received pkt ID, to know to expect a GCode 1 packet next
            last_rec_pkt_id = I2C_Packets.I2CPackets.RPI_GCODE_0_PKT_ID

      # -------------------------- GCODE 1 PKT ID ----------------------------
      elif data[I2C_Packets.PACKET_ID] == I2C_Packets.I2CPackets.RPI_GCODE_1_PKT_ID and bytes_rec == I2C_Packets.RPI_PACKET_MAX_LENGTHS[I2C_Packets.I2CPackets.RPI_GCODE_1_PKT_ID]:
         # Parse the data into the packet struct

         if last_rec_pkt_id == I2C_Packets.I2CPackets.RPI_GCODE_0_PKT_ID:
            pkt = I2C_Packets.RPI_I2C_Packet_GCode_1(data)
            gcode_full_str += pkt.gcode_str

            # Make and send the ACK packet
            ack_pkt = I2C_Packets.RPI_I2C_Packet_ACK(C_TRUE)
            s, b, d = pi.bsc_i2c(I2C_ADDR, ack_pkt.raw)
            # Set last received pkt ID, to know to expect a GCode 1 packet next
            last_rec_pkt_id = I2C_Packets.I2CPackets.RPI_GCODE_1_PKT_ID

      # -------------------------- GCODE 2 PKT ID ----------------------------
      elif data[I2C_Packets.PACKET_ID] == I2C_Packets.I2CPackets.RPI_GCODE_2_PKT_ID and bytes_rec == I2C_Packets.RPI_PACKET_MAX_LENGTHS[I2C_Packets.I2CPackets.RPI_GCODE_2_PKT_ID]:
         # Parse the data into the packet struct

         if last_rec_pkt_id == I2C_Packets.I2CPackets.RPI_GCODE_1_PKT_ID:
            pkt = I2C_Packets.RPI_I2C_Packet_GCode_2(data)
            gcode_full_str += pkt.gcode_str

            # Make and send the ACK packet
            ack_pkt = I2C_Packets.RPI_I2C_Packet_ACK(C_TRUE)
            s, b, d = pi.bsc_i2c(I2C_ADDR, ack_pkt.raw)
            # Set last received pkt ID, to know to expect a GCode 1 packet next
            last_rec_pkt_id = I2C_Packets.I2CPackets.RPI_GCODE_2_PKT_ID

      # -------------------------- GCODE 3 PKT ID ----------------------------
      elif data[I2C_Packets.PACKET_ID] == I2C_Packets.I2CPackets.RPI_GCODE_3_PKT_ID and bytes_rec == I2C_Packets.RPI_PACKET_MAX_LENGTHS[I2C_Packets.I2CPackets.RPI_GCODE_3_PKT_ID]:
         # Parse the data into the packet struct

         if last_rec_pkt_id == I2C_Packets.I2CPackets.RPI_GCODE_2_PKT_ID:
            pkt = I2C_Packets.RPI_I2C_Packet_GCode_3(data)
            gcode_full_str += pkt.gcode_str

            # Make and send the ACK packet
            ack_pkt = I2C_Packets.RPI_I2C_Packet_ACK(C_TRUE)
            s, b, d = pi.bsc_i2c(I2C_ADDR, ack_pkt.raw)
            # Set last received pkt ID, to know to expect a GCode 1 packet next
            last_rec_pkt_id = I2C_Packets.I2CPackets.RPI_GCODE_3_PKT_ID

      # -------------------------- GCODE 4 PKT ID ----------------------------
      elif data[I2C_Packets.PACKET_ID] == I2C_Packets.I2CPackets.RPI_GCODE_4_PKT_ID and bytes_rec == I2C_Packets.RPI_PACKET_MAX_LENGTHS[I2C_Packets.I2CPackets.RPI_GCODE_4_PKT_ID]:
         # Parse the data into the packet struct

         if last_rec_pkt_id == I2C_Packets.I2CPackets.RPI_GCODE_3_PKT_ID:
            pkt = I2C_Packets.RPI_I2C_Packet_GCode_4(data)
            pkt_success_count += 1
            gcode_full_str += pkt.gcode_str
            # Send the gcode to the SKR MINI E3 via the terminal
            call(["echo", gcode_full_str, ">>", "/tmp/printer/"])

            # Make and send the ACK packet
            ack_pkt = I2C_Packets.RPI_I2C_Packet_ACK(C_TRUE)
            s, b, d = pi.bsc_i2c(I2C_ADDR, ack_pkt.raw)
            # Set last received pkt ID, to know to expect a GCode 1 packet next
            last_rec_pkt_id = I2C_Packets.I2CPackets.RPI_GCODE_4_PKT_ID

            print("[" + str(pkt_success_count) + "/" + str((pkt_rec_count/5)) + "]")


      # ------------------------ AHT20 DATA PKT ID -------------------------
      elif data[I2C_Packets.PACKET_ID] == I2C_Packets.I2CPackets.RPI_AHT20_PKT_ID:
         print("Else!")

      # ------------------------ WATER DATA PKT ID -------------------------
      # elif data[I2C_Packets.PACKET_ID] == I2C_Packets.I2CPackets.RPI_WATER_DATA_PKT_ID:
      #    pass

      # ----------------------- BUTTONS DATA PKT ID ------------------------
      elif data[I2C_Packets.PACKET_ID] == I2C_Packets.I2CPackets.RPI_BUTTONS_PKT_ID:
         pass

      # ---------------------- NET POT STATUS PKT ID -----------------------
      elif data[I2C_Packets.PACKET_ID] == I2C_Packets.I2CPackets.RPI_NET_POT_STATUS_PKT_ID:
         pass

      # ------------------ GET AXES DATA REQUEST PKT ID --------------------
      elif data[I2C_Packets.PACKET_ID] == I2C_Packets.I2CPackets.RPI_GET_AXES_POS_PKT_ID:
         pass

      elif data[I2C_Packets.PACKET_ID] == I2C_Packets.I2CPackets.RPI_I2C_UNIX_TIME:
         pkt = I2C_Packets.RPI_I2C_PACKET_UNIX_TIME()

         s, b, d = pi.bsc_i2c(I2C_ADDR, pkt.raw)

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
while pi.connected:
   time.sleep(0.1)

# If the interface exits, gracefully shut down
e.cancel()
pi.bsc_i2c(0) # Disable BSC peripheral
pi.stop()
print("Exiting")

