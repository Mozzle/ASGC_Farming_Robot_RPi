import serial
import UART_Packets

from datetime import datetime
import time
from subprocess import call
import re
import os

from historical_logger import log_packet_csv

os.makedirs('historical-data/', exist_ok=True)

C_FALSE = 0
C_TRUE = 1

def UART_LOOP():
   global port
   if port.in_waiting > 0:
      pkt_id = port.read(1)
      pkt_id = int.from_bytes(pkt_id, "big")
      #print ("Packet ID: " + str(pkt_id))
   else:
      return

   if pkt_id >= len(UART_Packets.UARTPackets):
      print("Invalid Packet ID: " + str(pkt_id))
      return

   # ---------------------------- GCODE PKT ID ----------------------------
   if pkt_id == UART_Packets.UARTPackets.RPI_GCODE_PKT_ID:
      bytes_rec = port.read(UART_Packets.RPI_PACKET_LENGTHS[UART_Packets.UARTPackets.RPI_GCODE_PKT_ID])
      if len(bytes_rec) == UART_Packets.RPI_PACKET_LENGTHS[UART_Packets.UARTPackets.RPI_GCODE_PKT_ID]:
         pkt = UART_Packets.RPI_UART_Packet_GCode(bytes_rec)

         if pkt.valid == C_TRUE:
            gcode_full_str = pkt.gcode_str

            # Send the gcode to the SKR MINI E3 via the terminal
            call(["echo", gcode_full_str, ">>", "/tmp/printer/"])

            # Make and send the ACK packet
            ack_pkt = UART_Packets.RPI_UART_Packet_ACK(C_TRUE)
            port.write(ack_pkt.raw)
            
            # Log GCODE to CSV
            try:
               log_packet_csv('GCODE', ['gcode'], [gcode_full_str])
            except Exception:
               # don't let logging break serial handling
               pass

      else:
         print("Error: Incomplete GCode Packet")

   # ------------------------ AHT20 DATA PKT ID -------------------------
   elif pkt_id == UART_Packets.UARTPackets.RPI_AHT20_PKT_ID:
      bytes_rec = port.read(UART_Packets.RPI_PACKET_LENGTHS[UART_Packets.UARTPackets.RPI_AHT20_PKT_ID])
      if len(bytes_rec) == UART_Packets.RPI_PACKET_LENGTHS[UART_Packets.UARTPackets.RPI_AHT20_PKT_ID]:
         pkt = UART_Packets.RPI_UART_Packet_AHT20(bytes_rec)

         if pkt.valid == C_TRUE:
            print("AHT20 Temp: " + str(pkt.temperature) + " C  Humidity: " + str(pkt.humidity * 100) + " %")

            # DO SOMETHING WITH THE AHT20 DATA HERE
            # Log AHT20 readings
            try:
               log_packet_csv('AHT20', ['temperature_C', 'humidity_percent'], [pkt.temperature, pkt.humidity * 100])
            except Exception:
               pass

            # Make and send the ACK packet
            ack_pkt = UART_Packets.RPI_UART_Packet_ACK(C_TRUE)
            port.write(ack_pkt.raw)
      else:
         print("Error: Incomplete AHT20 Packet")

   # -------------------------- SEN0169 PKT ID --------------------------
   elif pkt_id == UART_Packets.UARTPackets.RPI_SEN0169_PKT_ID:
      bytes_rec = port.read(UART_Packets.RPI_PACKET_LENGTHS[UART_Packets.UARTPackets.RPI_SEN0169_PKT_ID])

      if len(bytes_rec) == UART_Packets.RPI_PACKET_LENGTHS[UART_Packets.UARTPackets.RPI_SEN0169_PKT_ID]:

         pkt = UART_Packets.RPI_UART_Packet_SEN0169(bytes_rec)

         if pkt.valid == C_TRUE:
            print("SEN0169 pH: " + str(pkt.pH))

            # DO SOMETHING WITH THE SEN0169 DATA HERE
            # Log pH
            try:
               log_packet_csv('SEN0169', ['pH'], [pkt.pH])
            except Exception:
               pass

            # Make and send the ACK packet
            ack_pkt = UART_Packets.RPI_UART_Packet_ACK(C_TRUE)
            port.write(ack_pkt.raw)
      else:
         print("Error: Incomplete SEN0169 Packet")

   # -------------------------- SEN0244 PKT ID --------------------------
   elif pkt_id == UART_Packets.UARTPackets.RPI_SEN0244_PKT_ID:
      bytes_rec = port.read(UART_Packets.RPI_PACKET_LENGTHS[UART_Packets.UARTPackets.RPI_SEN0244_PKT_ID])
      if len(bytes_rec) == UART_Packets.RPI_PACKET_LENGTHS[UART_Packets.UARTPackets.RPI_SEN0244_PKT_ID]:
         pkt = UART_Packets.RPI_UART_Packet_SEN0244(bytes_rec)

         if pkt.valid == C_TRUE:
            print("SEN0244 TDS: " + str(pkt.tds) + " ppm")

            # DO SOMETHING WITH THE SEN0244 DATA HERE
            # Log TDS
            try:
               log_packet_csv('SEN0244', ['TDS_ppm'], [pkt.tds])
            except Exception:
               pass

            # Make and send the ACK packet
            ack_pkt = UART_Packets.RPI_UART_Packet_ACK(C_TRUE)
            port.write(ack_pkt.raw)
      else:
         print("Error: Incomplete SEN0244 Packet")

   # -------------------------- AS7341 PKT ID ----------------------------
   elif pkt_id == UART_Packets.UARTPackets.RPI_AS7341_PKT_ID:
      bytes_rec = port.read(UART_Packets.RPI_PACKET_LENGTHS[UART_Packets.UARTPackets.RPI_AS7341_PKT_ID])
      if len(bytes_rec) == UART_Packets.RPI_PACKET_LENGTHS[UART_Packets.UARTPackets.RPI_AS7341_PKT_ID]:
         pkt = UART_Packets.RPI_UART_Packet_AS7341(bytes_rec)

         if pkt.valid == C_TRUE:
            print("AS7341 CH0: " + str(pkt.channel_0) + " CH1: " + str(pkt.channel_1) + " CH2: " + str(pkt.channel_2) + " CH3: " + str(pkt.channel_3) + " CH4: " + str(pkt.channel_4) + " CH5: " + str(pkt.channel_5) + " CH6: " + str(pkt.channel_6) + " CH7: " + str(pkt.channel_7) + " CH8: " + str(pkt.channel_8) + " CH9: " + str(pkt.channel_9) + " CH10: " + str(pkt.channel_10))
            # DO SOMETHING WITH THE AS7341 DATA HERE
            # Log AS7341 channels
            try:
               headers = [f'channel_{i}' for i in range(0, 11)]
               values = [pkt.channel_0, pkt.channel_1, pkt.channel_2, pkt.channel_3, pkt.channel_4, pkt.channel_5, pkt.channel_6, pkt.channel_7, pkt.channel_8, pkt.channel_9, pkt.channel_10]
               log_packet_csv('AS7341', headers, values)
            except Exception:
               pass

            # Make and send the ACK packet
            ack_pkt = UART_Packets.RPI_UART_Packet_ACK(C_TRUE)
            port.write(ack_pkt.raw)
      else:
         print("Error: Incomplete AS7341 Packet")

   # --------------------- UNIX TIME REQUEST PKT ID ---------------------
   elif pkt_id == UART_Packets.UARTPackets.RPI_UNIX_TIME_REQUEST_PKT_ID:
      # Get the current UNIX time
      unix_time = int(time.time())
      timezone = int(datetime.now().astimezone().strftime("%z")) / 100  # in hours
      print("Sending Unix Time: " + str(unix_time) + ", TZ: " + str(timezone))

      # Send the UNIX time packet back to the RPi
      unix_time_pkt = UART_Packets.RPI_UART_Packet_UNIX_TIME(unix_time, timezone)
      port.write(unix_time_pkt.raw)
      # Log the time request/response
      try:
         log_packet_csv('UNIX_TIME_REQUEST', ['sent_unix_time', 'timezone_hours'], [unix_time, timezone])
      except Exception:
         pass

   # --------------------- GET AXES REQUEST PKT ID -----------------------
   elif pkt_id == UART_Packets.UARTPackets.RPI_GET_AXES_POS_PKT_ID:
      # Send M114
      call(["echo", "M114", ">>", "/tmp/printer"])

      # Read response
      serial_log_path = "~/.octoprint/logs/serial.log"

      with open(serial_log_path, 'r') as file:
         log_lines = file.readlines()

      # only search the last 100 lines
      x, y, z, e = None, None, None, None
      p = re.compile(r'Recv: X:(\d+.\d+) Y:(\d+.\d+) Z:(\d+.\d+) E:(\d+.\d+)')
      for line in list(reversed(log_lines))[:100]:
         if s := p.search(line):
            x = float(s.group(0))
            y = float(s.group(1))
            z = float(s.group(2))
            e = float(s.group(3))

         # Pretty sure this should do something else

   else:
      print("Unhandled Packet ID: " + str(pkt_id))


''' ------------------------------------------------------------------------
   Program Entry Point
   ------------------------------------------------------------------------ '''

port = serial.Serial("/dev/ttyAMA0", baudrate=115200, timeout=0.5)
print("Opening Serial Interface with Nucleo Microcontroller...")

while True:
    UART_LOOP()