import time
from datetime import datetime
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

   bytesCopiedToTransmit = int.from_bytes(status[0:5], byteorder='big', signed=False)
   bytesInRecFIFO = int.from_bytes(status[5:10], byteorder='big', signed=False)
   bytesInTxFIFO = int.from_bytes(status[10:15], byteorder='big', signed=False)
   receiveBusy = bool(status[15])
   transmitFifoEmpty = bool(status[16])
   rxFifoFull = bool(status[17])
   txFifoFull = bool(status[18])
   rxFifoEmpty = bool(status[19])
   txBusy = bool(status[20])

   print("Bytes copied to transmit: " + str(bytesCopiedToTransmit) + ", Bytes in RX FIFO: " + str(bytesInRecFIFO) + ", Bytes in TX FIFO: " + str(bytesInTxFIFO) + ", Receive Busy: " + str(receiveBusy) + ", Transmit FIFO Empty: " + str(transmitFifoEmpty) + ", RX FIFO Full: " + str(rxFifoFull) + ", TX FIFO Full: " + str(txFifoFull) + ", RX FIFO Empty: " + str(rxFifoEmpty) + ", TX Busy: " + str(txBusy))

   # If we received data
   if bytes_rec:
      #print(data[:-1])
      pkt_rec_count += 1

      if data[I2C_Packets.PACKET_ID] >= I2C_Packets.RPI_I2C_NUM_PKT_IDS:
         ack_pkt = I2C_Packets.RPI_I2C_Packet_ACK(C_FALSE)
         print("ERROR: Invalid packet ID received!")
         print("SENDING NACK PACKET")
         s, b, d = pi.bsc_i2c(I2C_ADDR, ack_pkt.raw)
         return


      # If the received data length does not match the expected packet size
      if bytes_rec is not I2C_Packets.RPI_PACKET_LENGTHS[data[I2C_Packets.PACKET_ID]]:
         # Error of some kind
         print("ERROR: Packet length mismatch! Len:" + str(bytes_rec))
         ack_pkt = I2C_Packets.RPI_I2C_Packet_ACK(C_FALSE)
         print("SENDING NACK PACKET")
         s, b, d = pi.bsc_i2c(I2C_ADDR, ack_pkt.raw)
         return


      # Match the pkt_id
      # -------------------------- ERROR PKT ID ----------------------------
      if data[I2C_Packets.PACKET_ID] == I2C_Packets.RPI_ERR_PKT_ID:
         print("Yeah!")

      # -------------------------- GCODE 0 PKT ID ----------------------------
      elif data[I2C_Packets.PACKET_ID] == I2C_Packets.RPI_GCODE_0_PKT_ID and bytes_rec == I2C_Packets.RPI_PACKET_LENGTHS[I2C_Packets.RPI_GCODE_0_PKT_ID]:
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
            last_rec_pkt_id = I2C_Packets.RPI_GCODE_0_PKT_ID

      # -------------------------- GCODE 1 PKT ID ----------------------------
      elif data[I2C_Packets.PACKET_ID] == I2C_Packets.RPI_GCODE_1_PKT_ID and bytes_rec == I2C_Packets.RPI_PACKET_LENGTHS[I2C_Packets.RPI_GCODE_1_PKT_ID]:
         # Parse the data into the packet struct

         if last_rec_pkt_id == I2C_Packets.RPI_GCODE_0_PKT_ID:
            pkt = I2C_Packets.RPI_I2C_Packet_GCode_1(data)
            gcode_full_str += pkt.gcode_str

            # Make and send the ACK packet
            ack_pkt = I2C_Packets.RPI_I2C_Packet_ACK(C_TRUE)
            s, b, d = pi.bsc_i2c(I2C_ADDR, ack_pkt.raw)
            # Set last received pkt ID, to know to expect a GCode 1 packet next
            last_rec_pkt_id = I2C_Packets.RPI_GCODE_1_PKT_ID

      # -------------------------- GCODE 2 PKT ID ----------------------------
      elif data[I2C_Packets.PACKET_ID] == I2C_Packets.RPI_GCODE_2_PKT_ID and bytes_rec == I2C_Packets.RPI_PACKET_LENGTHS[I2C_Packets.RPI_GCODE_2_PKT_ID]:
         # Parse the data into the packet struct

         if last_rec_pkt_id == I2C_Packets.RPI_GCODE_1_PKT_ID:
            pkt = I2C_Packets.RPI_I2C_Packet_GCode_2(data)
            gcode_full_str += pkt.gcode_str

            # Make and send the ACK packet
            ack_pkt = I2C_Packets.RPI_I2C_Packet_ACK(C_TRUE)
            s, b, d = pi.bsc_i2c(I2C_ADDR, ack_pkt.raw)
            # Set last received pkt ID, to know to expect a GCode 1 packet next
            last_rec_pkt_id = I2C_Packets.RPI_GCODE_2_PKT_ID

      # -------------------------- GCODE 3 PKT ID ----------------------------
      elif data[I2C_Packets.PACKET_ID] == I2C_Packets.RPI_GCODE_3_PKT_ID and bytes_rec == I2C_Packets.RPI_PACKET_LENGTHS[I2C_Packets.RPI_GCODE_3_PKT_ID]:
         # Parse the data into the packet struct

         if last_rec_pkt_id == I2C_Packets.RPI_GCODE_2_PKT_ID:
            pkt = I2C_Packets.RPI_I2C_Packet_GCode_3(data)
            gcode_full_str += pkt.gcode_str

            # Make and send the ACK packet
            ack_pkt = I2C_Packets.RPI_I2C_Packet_ACK(C_TRUE)
            s, b, d = pi.bsc_i2c(I2C_ADDR, ack_pkt.raw)
            # Set last received pkt ID, to know to expect a GCode 1 packet next
            last_rec_pkt_id = I2C_Packets.RPI_GCODE_3_PKT_ID

      # -------------------------- GCODE 4 PKT ID ----------------------------
      elif data[I2C_Packets.PACKET_ID] == I2C_Packets.RPI_GCODE_4_PKT_ID and bytes_rec == I2C_Packets.RPI_PACKET_LENGTHS[I2C_Packets.RPI_GCODE_4_PKT_ID]:
         # Parse the data into the packet struct

         if last_rec_pkt_id == I2C_Packets.RPI_GCODE_3_PKT_ID:
            pkt = I2C_Packets.RPI_I2C_Packet_GCode_4(data)
            pkt_success_count += 1
            gcode_full_str += pkt.gcode_str
            # Send the gcode to the SKR MINI E3 via the terminal
            call(["echo", gcode_full_str, ">>", "/tmp/printer/"])

            # Make and send the ACK packet
            ack_pkt = I2C_Packets.RPI_I2C_Packet_ACK(C_TRUE)
            s, b, d = pi.bsc_i2c(I2C_ADDR, ack_pkt.raw)
            # Set last received pkt ID, to know to expect a GCode 1 packet next
            last_rec_pkt_id = I2C_Packets.RPI_GCODE_4_PKT_ID

            print("[" + str(pkt_success_count) + "/" + str((pkt_rec_count/5)) + "]")


      # ------------------------ AHT20 DATA PKT ID -------------------------
      elif data[I2C_Packets.PACKET_ID] == I2C_Packets.RPI_AHT20_PKT_ID and bytes_rec == I2C_Packets.RPI_PACKET_LENGTHS[I2C_Packets.RPI_AHT20_PKT_ID]:
         pkt = I2C_Packets.RPI_I2C_Packet_AHT20(data)

         if pkt.valid == C_TRUE:
            # Make and send the ACK packet
            ack_pkt = I2C_Packets.RPI_I2C_Packet_ACK(C_TRUE)
            s, b, d = pi.bsc_i2c(I2C_ADDR, ack_pkt.raw)
            last_rec_pkt_id = I2C_Packets.RPI_AHT20_PKT_ID

            print("Temp: " + str(pkt.temperature) + "C, Humidity: " + str(pkt.humidity * 100) + "%")

            # FORWARD THE pkt.temperature and pkt.humidity VALUES TO WEB SERVER HERE

      # -------------------------- SEN0169 PKT ID --------------------------
      elif data[I2C_Packets.PACKET_ID] == I2C_Packets.RPI_SEN0169_PKT_ID and bytes_rec == I2C_Packets.RPI_PACKET_LENGTHS[I2C_Packets.RPI_SEN0169_PKT_ID]:
         pkt = I2C_Packets.RPI_I2C_Packet_SEN0169(data)

         if pkt.valid == C_TRUE:
            # Make and send the ACK packet
            ack_pkt = I2C_Packets.RPI_I2C_Packet_ACK(C_TRUE)
            s, b, d = pi.bsc_i2c(I2C_ADDR, ack_pkt.raw)
            last_rec_pkt_id = I2C_Packets.RPI_SEN0169_PKT_ID

            print("pH: " + str(pkt.pH))

            # FORWARD THE pkt.pH VALUE TO WEB SERVER HERE

      # -------------------------- SEN0244 PKT ID --------------------------
      elif data[I2C_Packets.PACKET_ID] == I2C_Packets.RPI_SEN0244_PKT_ID and bytes_rec == I2C_Packets.RPI_PACKET_LENGTHS[I2C_Packets.RPI_SEN0244_PKT_ID]:
         pkt = I2C_Packets.RPI_I2C_Packet_SEN0244(data)

         if pkt.valid == C_TRUE:
            # Make and send the ACK packet
            ack_pkt = I2C_Packets.RPI_I2C_Packet_ACK(C_TRUE)
            s, b, d = pi.bsc_i2c(I2C_ADDR, ack_pkt.raw)
            last_rec_pkt_id = I2C_Packets.RPI_SEN0244_PKT_ID

            print("TDS: " + str(pkt.tds) + " ppm")

            # FORWARD THE pkt.tds VALUE TO WEB SERVER HERE

      # -------------------------- AS7341 PKT 0 ID --------------------------
      elif data[I2C_Packets.PACKET_ID] == I2C_Packets.RPI_AS7341_0_PKT_ID and bytes_rec == I2C_Packets.RPI_PACKET_LENGTHS[I2C_Packets.RPI_AS7341_0_PKT_ID]:
         pkt = I2C_Packets.RPI_I2C_Packet_AS7341_0(data)

         if pkt.valid == C_TRUE:
            # Make and send the ACK packet
            ack_pkt = I2C_Packets.RPI_I2C_Packet_ACK(C_TRUE)
            s, b, d = pi.bsc_i2c(I2C_ADDR, ack_pkt.raw)
            last_rec_pkt_id = I2C_Packets.RPI_AS7341_0_PKT_ID

            print("AS7341 CH0: " + str(pkt.channel_0) + ", CH1: " + str(pkt.channel_1) + ", CH2: " + str(pkt.channel_2) + ", CH3: " + str(pkt.channel_3) + ", CH4: " + str(pkt.channel_4) + ", CH5: " + str(pkt.channel_5) + ", CH6: " + str(pkt.channel_6))

            # FORWARD THE pkt.channel_0 - pkt.channel_6 VALUES TO WEB SERVER HERE
            # OR STORE THEM IN GLOBAL VARIABLES TO BE SENT AFTER AS7341_1_PKT IS RECEIVED

      # -------------------------- AS7341 PKT 1 ID --------------------------
      elif data[I2C_Packets.PACKET_ID] == I2C_Packets.RPI_AS7341_1_PKT_ID and bytes_rec == I2C_Packets.RPI_PACKET_LENGTHS[I2C_Packets.RPI_AS7341_1_PKT_ID]:
         pkt = I2C_Packets.RPI_I2C_Packet_AS7341_1(data)

         if pkt.valid == C_TRUE and last_rec_pkt_id == I2C_Packets.RPI_AS7341_0_PKT_ID:
            # Make and send the ACK packet
            ack_pkt = I2C_Packets.RPI_I2C_Packet_ACK(C_TRUE)
            s, b, d = pi.bsc_i2c(I2C_ADDR, ack_pkt.raw)
            last_rec_pkt_id = I2C_Packets.RPI_AS7341_1_PKT_ID

            print("AS7341 CH7: " + str(pkt.channel_7) + ", CH8: " + str(pkt.channel_8) + ", CH9: " + str(pkt.channel_9) + ", CH10: " + str(pkt.channel_10))

            # FORWARD THE pkt.channel_7 - pkt.channel_10 VALUES TO WEB SERVER HERE
            # OR STORE THEM IN GLOBAL VARIABLES TO BE SENT AFTER AS7341_0_PKT IS RECEIVED

      # ----------------------- BUTTONS DATA PKT ID ------------------------
      elif data[I2C_Packets.PACKET_ID] == I2C_Packets.RPI_BUTTONS_PKT_ID and bytes_rec == I2C_Packets.RPI_PACKET_LENGTHS[I2C_Packets.RPI_BUTTONS_PKT_ID]:
         pass

      # ---------------------- NET POT STATUS PKT ID -----------------------
      elif data[I2C_Packets.PACKET_ID] == I2C_Packets.RPI_NET_POT_STATUS_PKT_ID and bytes_rec == I2C_Packets.RPI_PACKET_LENGTHS[I2C_Packets.RPI_NET_POT_STATUS_PKT_ID]:
         pass

      # ------------------ GET AXES DATA REQUEST PKT ID --------------------
      elif data[I2C_Packets.PACKET_ID] == I2C_Packets.RPI_GET_AXES_POS_PKT_ID and bytes_rec == I2C_Packets.RPI_PACKET_LENGTHS[I2C_Packets.RPI_GET_AXES_POS_PKT_ID]:
         pass

      # --------------------- UNIX TIME REQUEST PKT ID ---------------------
      elif data[I2C_Packets.PACKET_ID] == I2C_Packets.RPI_UNIX_TIME_REQUEST_PKT_ID and bytes_rec == I2C_Packets.RPI_PACKET_LENGTHS[I2C_Packets.RPI_UNIX_TIME_REQUEST_PKT_ID]:
         # Make the unix time packet
         current_unix_time = int(time.time())
         current_timezone = int(datetime.now().astimezone().strftime("%z") / 100)  # in hours

         print("Sending Unix Time: " + str(current_unix_time) + ", TZ: " + str(current_timezone))
         pkt = I2C_Packets.RPI_I2C_Packet_Unix_Time(current_unix_time, current_timezone)

         # Send the unix time packet
         s, b, d = pi.bsc_i2c(I2C_ADDR, pkt.raw)

         last_rec_pkt_id = I2C_Packets.RPI_UNIX_TIME_REQUEST_PKT_ID

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

