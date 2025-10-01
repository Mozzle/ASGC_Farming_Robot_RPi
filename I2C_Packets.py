import struct

''' ------------------------------------------------------------------------
I2C Packet IDs
------------------------------------------------------------------------ '''
RPI_ERR_PKT_ID				    = 0
RPI_GCODE_0_PKT_ID              = 1
RPI_GCODE_1_PKT_ID              = 2
RPI_GCODE_2_PKT_ID              = 3
RPI_GCODE_3_PKT_ID              = 4
RPI_GCODE_4_PKT_ID              = 5
RPI_AHT20_PKT_ID                = 6
RPI_SEN0169_PKT_ID              = 7
RPI_SEN0244_PKT_ID              = 8
RPI_AS7341_0_PKT_ID             = 9
RPI_AS7341_1_PKT_ID             = 10
RPI_BUTTONS_PKT_ID              = 11
RPI_NET_POT_STATUS_PKT_ID       = 12
RPI_GET_AXES_POS_PKT_ID         = 13
RPI_ACK_PKT_ID                  = 14
RPI_UNIX_TIME_REQUEST_PKT_ID    = 15
RPI_UNIX_TIME_PKT_ID            = 16

RPI_I2C_NUM_PKT_IDS	            = 17

RPI_PACKET_LENGTHS     = [
    0,  # RPI_ERR_PKT_ID
    16,   # RPI_GCODE_0_PKT_ID
    16,   # RPI_GCODE_1_PKT_ID
    16,   # RPI_GCODE_2_PKT_ID
    16,   # RPI_GCODE_3_PKT_ID
    16,   # RPI_GCODE_4_PKT_ID
    16,   # RPI_AHT20_PKT_ID
    16,   # RPI_SEN0169_PKT_ID
    16,   # RPI_SEN0244_PKT_ID
    15,   # RPI_AS7341_0_PKT_ID
    11,   # RPI_AS7341_1_PKT_ID
    0,    # RPI_BUTTONS_PKT_ID
    0,    # RPI_NET_POT_STATUS_PKT_ID
    0,    # RPI_GET_AXES_POS_PKT_ID
    2,    # RPI_ACK_PKT_ID
    1,    # RPI_UNIX_TIME_REQUEST_PKT_ID
    6,    # RPI_UNIX_TIME_PKT_ID
] 

PACKET_ID                   = 0
PACKET_VALID                = 1

RPI_ERR_PKT_LAST_VALID_BYTE     = 0
RPI_GCODE_PKT_LAST_VALID_BYTE   = 66

''' ------------------------------------------------------------------------
RPI_GCODE_PKT_ID - GCode Packet
Packet Elements:
packet_id
valid
gcode_str
------------------------------------------------------------------------ '''
class RPI_I2C_Packet_GCode_0:
    def __init__(self, data):

        # Get packet ID
        self.packet_id = data[PACKET_ID]

        # If the packet ID is not the gcode packet
        if self.packet_id is not RPI_GCODE_0_PKT_ID:
            self.valid = False
        else:
            # Get packet validity from data
            self.valid = data[PACKET_VALID]

        self.gcode_str = data[2:16].decode('UTF-8').strip()
        self.gcode_str = self.gcode_str.replace('\x00', '')

class RPI_I2C_Packet_GCode_1:
    def __init__(self, data):

        # Get packet ID
        self.packet_id = data[PACKET_ID]

        # If the packet ID is not the gcode packet
        if self.packet_id is not RPI_GCODE_1_PKT_ID:
            self.packet_id = RPI_ERR_PKT_ID

        self.gcode_str = data[1:16].decode('UTF-8').strip()
        self.gcode_str = self.gcode_str.replace('\x00', '')

class RPI_I2C_Packet_GCode_2:
    def __init__(self, data):

        # Get packet ID
        self.packet_id = data[PACKET_ID]

        # If the packet ID is not the gcode packet
        if self.packet_id is not RPI_GCODE_2_PKT_ID:
            self.packet_id = RPI_ERR_PKT_ID

        self.gcode_str = data[1:16].decode('UTF-8').strip()
        self.gcode_str = self.gcode_str.replace('\x00', '')

class RPI_I2C_Packet_GCode_3:
    def __init__(self, data):

        # Get packet ID
        self.packet_id = data[PACKET_ID]

        # If the packet ID is not the gcode packet
        if self.packet_id is not RPI_GCODE_3_PKT_ID:
            self.packet_id = RPI_ERR_PKT_ID

        self.gcode_str = data[1:16].decode('UTF-8').strip()
        self.gcode_str = self.gcode_str.replace('\x00', '')

class RPI_I2C_Packet_GCode_4:
    def __init__(self, data):

        # Get packet ID
        self.packet_id = data[PACKET_ID]

        # If the packet ID is not the gcode packet
        if self.packet_id is not RPI_GCODE_4_PKT_ID:
            self.packet_id = RPI_ERR_PKT_ID

        self.gcode_str = data[1:16].decode('UTF-8').strip()
        self.gcode_str = self.gcode_str.replace('\x00', '')

class RPI_I2C_Packet_AHT20:
    def __init__(self, data):

        # Get packet ID
        self.packet_id = data[PACKET_ID]

        # If the packet ID is not the AHT20 packet
        if self.packet_id is not RPI_AHT20_PKT_ID:
            self.valid = False
        else:
            # Get packet validity from data
            self.valid = data[PACKET_VALID]

        # extract the temperature and humidity values from the byte data
        self.temperature = struct.unpack('<f', data[4:8])[0]
        self.humidity = struct.unpack('<f', data[8:12])[0]

class RPI_I2C_Packet_ACK:
    def __init__(self, ack):
        # Pack packet
        self.packet_id = RPI_ACK_PKT_ID
        self.ack = ack
        # Get the raw byte representation of the packet
        self.raw = ((self.packet_id << 8) | self.ack)
        self.raw = self.raw.to_bytes(2, byteorder='big')

class RPI_I2C_Packet_SEN0169:
    def __init__(self, data):

        # Get packet ID
        self.packet_id = data[PACKET_ID]

        # If the packet ID is not the SEN0169 packet
        if self.packet_id is not RPI_SEN0169_PKT_ID:
            self.valid = False
        else:
            # Get packet validity from data
            self.valid = True

        # extract the pH value from the byte data
        self.pH = struct.unpack('<d', data[8:16])[0]

class RPI_I2C_Packet_SEN0244:
    def __init__(self, data):

        # Get packet ID
        self.packet_id = data[PACKET_ID]

        # If the packet ID is not the SEN0244 packet
        if self.packet_id is not RPI_SEN0244_PKT_ID:
            self.valid = False
        else:
            # Get packet validity from data
            self.valid = True

        # extract the TDS value from the byte data
        self.tds = struct.unpack('<d', data[8:16])[0]

class RPI_I2C_Packet_AS7341_0:
    def __init__(self, data):

        # Get packet ID
        self.packet_id = data[PACKET_ID]

        # If the packet ID is not the AS7341_0 packet
        if self.packet_id is not RPI_AS7341_0_PKT_ID:
            self.valid = False
        else:
            # Get packet validity from data
            self.valid = True

        # extract the AS7341 channel values from the byte data
        self.channel_0 = struct.unpack('>H', data[1:3])[0]
        self.channel_1 = struct.unpack('>H', data[3:5])[0]
        self.channel_2 = struct.unpack('>H', data[5:7])[0]
        self.channel_3 = struct.unpack('>H', data[7:9])[0]
        self.channel_4 = struct.unpack('>H', data[9:11])[0]
        self.channel_5 = struct.unpack('>H', data[11:13])[0]
        self.channel_6 = struct.unpack('>H', data[13:15])[0]

class RPI_I2C_Packet_AS7341_1:
    def __init__(self, data):

        # Get packet ID
        self.packet_id = data[PACKET_ID]

        # If the packet ID is not the AS7341_1 packet
        if self.packet_id is not RPI_AS7341_1_PKT_ID:
            self.valid = False
        else:
            # Get packet validity from data
            self.valid = True

        # extract the AS7341 channel values from the byte data
        self.channel_7 = struct.unpack('>H', data[1:3])[0]
        self.channel_8 = struct.unpack('>H', data[3:5])[0]
        self.channel_9 = struct.unpack('>H', data[5:7])[0]
        self.channel_10 = struct.unpack('>H', data[7:9])[0]

class RPI_I2C_Packet_Unix_Time_Request:
    def __init__(self, data):

        # Get packet ID
        self.packet_id = data[PACKET_ID]

        # If the packet ID is not the UNIX_TIME_REQUEST packet
        if self.packet_id is not RPI_UNIX_TIME_REQUEST_PKT_ID:
            self.valid = False
        else:
            # Get packet validity from data
            self.valid = True

class RPI_I2C_Packet_Unix_Time:
    def __init__(self, unixTimeSec: int, unixTimezone: int):
        # Pack packet
        self.packet_id = RPI_UNIX_TIME_PKT_ID
        self.unixTimeSec = unixTimeSec
        self.unixTimezone = unixTimezone
        # Get the raw byte representation of the packet
        self.raw = struct.pack('>BIB', self.packet_id, self.unixTimeSec, self.unixTimezone)