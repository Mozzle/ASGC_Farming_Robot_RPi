''' ------------------------------------------------------------------------
I2C Packet IDs
------------------------------------------------------------------------ '''
RPI_ERR_PKT_ID				= 0
RPI_GCODE_0_PKT_ID          = 1
RPI_GCODE_1_PKT_ID          = 2
RPI_GCODE_2_PKT_ID          = 3
RPI_GCODE_3_PKT_ID          = 4
RPI_GCODE_4_PKT_ID          = 5
RPI_AHT20_PKT_ID            = 6
RPI_WATER_DATA_PKT_ID       = 7
RPI_BUTTONS_PKT_ID          = 8
RPI_NET_POT_STATUS_PKT_ID   = 9
RPI_GET_AXES_POS_PKT_ID     = 10
RPI_ACK_PKT_ID              = 11

RPI_I2C_NUM_PKT_IDS         = 12

RPI_PACKET_MAX_LENGTHS     = [
    128,  # RPI_ERR_PKT_ID
    16,   # RPI_GCODE_0_PKT_ID
    16,   # RPI_GCODE_1_PKT_ID
    16,   # RPI_GCODE_2_PKT_ID
    16,   # RPI_GCODE_3_PKT_ID
    16,   # RPI_GCODE_4_PKT_ID
    16,   # RPI_AHT20_PKT_ID
    128,  # RPI_WATER_DATA_PKT_ID
    128,  # RPI_BUTTONS_PKT_ID
    128,  # RPI_NET_POT_STATUS_PKT_ID
    128   # RPI_GET_AXES_POS_PKT_ID
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

class RPI_I2C_Packet_ACK:
    def __init__(self, ack):
        # Pack packet
        self.packet_id = RPI_ACK_PKT_ID
        self.ack = ack
        # Get the raw byte representation of the packet
        self.raw = ((self.packet_id << 8) | self.ack)
        self.raw = self.raw.to_bytes(2, byteorder='big')


