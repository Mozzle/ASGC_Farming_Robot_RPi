import struct

RPI_ERR_PKT_ID					= 0
RPI_GCODE_PKT_ID				= 1	
RPI_AHT20_PKT_ID				= 2
RPI_SEN0169_PKT_ID				= 3
RPI_SEN0244_PKT_ID				= 4
RPI_AS7341_PKT_ID				= 5
RPI_BUTTONS_PKT_ID				= 6
RPI_NET_POT_STATUS_PKT_ID		= 7
RPI_GET_AXES_POS_PKT_ID			= 8
RPI_ACK_PKT_ID					= 9
RPI_UNIX_TIME_REQUEST_PKT_ID	= 10
RPI_UNIX_TIME_PKT_ID			= 11

RPI_UART_NUM_PKT_IDS			= 12

RPI_PACKET_LENGTHS     = [
	0,  # RPI_ERR_PKT_ID
	102,# RPI_GCODE_PKT_ID
	14, # RPI_AHT20_PKT_ID
	9,  # RPI_SEN0169_PKT_ID
	9,  # RPI_SEN0244_PKT_ID
	25, # RPI_AS7341_PKT_ID
	0,  # RPI_BUTTONS_PKT_ID
	0,  # RPI_NET_POT_STATUS_PKT_ID
	0,  # RPI_GET_AXES_POS_PKT_ID
	2,  # RPI_ACK_PKT_ID
	1,  # RPI_UNIX_TIME_REQUEST_PKT_ID
	6,  # RPI_UNIX_TIME_PKT_ID
]

PACKET_ID				   = 0
PACKET_VALID			   = 1

class RPI_UART_Packet_GCode:
	def __init__(self, data):
		self.packet_id = data[0]
		if self.packet_id is not RPI_GCODE_PKT_ID:
			self.valid = 0
		else:
			self.valid = 1

		self.gcode_str = data[2:102].decode('utf-8').replace('\x00', '')

class RPI_UART_Packet_AHT20:
	def __init__(self, data):
		self.packet_id = data[0]
		if self.packet_id is not RPI_AHT20_PKT_ID:
			self.valid = 0
		else:
			self.valid = 1
		self.temperature = struct.unpack('<f', data[2:6])[0]
		self.humidity = struct.unpack('<f', data[6:10])[0]

class RPI_UART_Packet_ACK:
	def __init__(self, ack):
		self.packet_id = RPI_ACK_PKT_ID
		self.ack = ack
		# Get the raw byte representation of the packet
		self.raw = ((self.packet_id << 8) | self.ack)
		self.raw = self.raw.to_bytes(2, byteorder='big')

class RPI_UART_Packet_SEN0169:
	def __init__(self, data):
		self.packet_id = data[0]

		if self.packet_id is not RPI_SEN0169_PKT_ID:
			self.valid = 0
		else:
			self.valid = 1

		self.pH = struct.unpack('<d', data[1:9])[0]

class RPI_UART_Packet_SEN0244:
	def __init__(self, data):
		self.packet_id = data[0]

		if self.packet_id is not RPI_SEN0244_PKT_ID:
			self.valid = 0
		else:
			self.valid = 1
			
		self.tds = struct.unpack('<d', data[1:9])[0]

class RPI_UART_Packet_AS7341:
	def __init__(self, data):
		# Get packet ID
		self.packet_id = data[PACKET_ID]

    	# If the packet ID is not the AS7341_0 packet
		if self.packet_id is not RPI_AS7341_PKT_ID:
			self.valid = 0
		else:
			# Get packet validity from data
			self.valid = 1

		self.channel_0 = struct.unpack('<H', data[1:3])[0]
		self.channel_1 = struct.unpack('<H', data[3:5])[0]
		self.channel_2 = struct.unpack('<H', data[5:7])[0]
		self.channel_3 = struct.unpack('<H', data[7:9])[0]
		self.channel_4 = struct.unpack('<H', data[9:11])[0]
		self.channel_5 = struct.unpack('<H', data[11:13])[0]
		self.channel_6 = struct.unpack('<H', data[13:15])[0]
		self.channel_7 = struct.unpack('<H', data[15:17])[0]
		self.channel_8 = struct.unpack('<H', data[17:19])[0]
		self.channel_9 = struct.unpack('<H', data[19:21])[0]
		self.channel_10 = struct.unpack('<H', data[21:23])[0]

class RPI_UART_Packet_UNIX_TIME:
	def __init__(self, unixTimeSec: int, unixTimezone: int):
		self.packet_id = RPI_UNIX_TIME_PKT_ID
		self.unixTimeSec = unixTimeSec
		self.unixTimezone = unixTimezone

		# Get the raw byte representation of the packet
		self.raw = struct.pack('>BIB', self.packet_id, self.unixTimeSec, self.unixTimezone)

class RPI_UART_Packet_UNIX_TIME_Request:
	def __init__(self, data):
		# Get packet ID
		self.packet_id = data[PACKET_ID]

		# If the packet ID is not the UNIX_TIME_REQUEST packet
		if self.packet_id is not RPI_UNIX_TIME_REQUEST_PKT_ID:
			self.valid = False
		else:
			# Get packet validity from data
			self.valid = True