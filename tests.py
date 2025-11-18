import UART_Packets

import struct


# AHT20 Valid Packet

humidity = 8.5
temperature = 73.26

h_bytes = struct.pack("<f", humidity)
t_bytes = struct.pack("<f", temperature)
id_bytes = struct.pack("<i", UART_Packets.UARTPackets.RPI_AHT20_PKT_ID)[:1]

data = id_bytes + t_bytes + h_bytes
print(data)

p = UART_Packets.RPI_UART_Packet_AHT20(data)

print(f'Id: {p.packet_id}')
assert p.packet_id == UART_Packets.UARTPackets.RPI_AHT20_PKT_ID

print(f'Valid: {bool(p.valid)}')
assert p.valid == 1

# Needs to be rounded because of some floating point error
print(round(p.temperature, 2))
assert round(p.temperature, 2) == temperature

print(p.humidity)
assert p.humidity == humidity


# --- Additional packet tests ---

print('\nTesting GCode packet unpacking')
# Build a 102-byte packet: [id][flag?][gcode bytes (100)]
gcode = 'G28 X0 Y0'
gcode_bytes = gcode.encode('utf-8')
# pad to 100 bytes
gcode_payload = gcode_bytes + b'\x00' * (100 - len(gcode_bytes))
data_gcode = bytes([UART_Packets.UARTPackets.RPI_GCODE_PKT_ID]) + b'\x00' + gcode_payload
pg = UART_Packets.RPI_UART_Packet_GCode(data_gcode)
print(f'GCode Id: {pg.packet_id}, valid: {pg.valid}, gcode: "{pg.gcode_str}"')
assert pg.packet_id == UART_Packets.UARTPackets.RPI_GCODE_PKT_ID
assert pg.valid == 1
assert pg.gcode_str == gcode


print('\nTesting ACK packet')
ack_val = 5
p_ack = UART_Packets.RPI_UART_Packet_ACK(ack_val)
print(f'ACK packet_id: {p_ack.packet_id}, ack: {p_ack.ack}, raw: {p_ack.raw}')
assert p_ack.packet_id == UART_Packets.UARTPackets.RPI_ACK_PKT_ID
assert p_ack.ack == ack_val
# raw is 2 bytes big-endian
expected_raw = ((p_ack.packet_id << 8) | ack_val).to_bytes(2, byteorder='big')
assert p_ack.raw == expected_raw


print('\nTesting SEN0169 (pH) packet unpacking')
ph = 7.25
data_ph = bytes([UART_Packets.UARTPackets.RPI_SEN0169_PKT_ID]) + struct.pack('<d', ph)
pph = UART_Packets.RPI_UART_Packet_SEN0169(data_ph)
print(f'pH Id: {pph.packet_id}, valid: {pph.valid}, pH: {pph.pH}')
assert pph.packet_id == UART_Packets.UARTPackets.RPI_SEN0169_PKT_ID
assert pph.valid == 1
assert abs(pph.pH - ph) < 1e-12


print('\nTesting SEN0244 (TDS) packet unpacking')
tds_val = 123.456
data_tds = bytes([UART_Packets.UARTPackets.RPI_SEN0244_PKT_ID]) + struct.pack('<d', tds_val)
ptds = UART_Packets.RPI_UART_Packet_SEN0244(data_tds)
print(f'TDS Id: {ptds.packet_id}, valid: {ptds.valid}, tds: {ptds.tds}')
assert ptds.packet_id == UART_Packets.UARTPackets.RPI_SEN0244_PKT_ID
assert ptds.valid == 1
assert abs(ptds.tds - tds_val) < 1e-12


print('\nTesting AS7341 packet unpacking')
# Create 11 channel 16-bit values
channels = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100]
as_bytes = b''.join(struct.pack('<H', c) for c in channels)
data_as = bytes([UART_Packets.UARTPackets.RPI_AS7341_PKT_ID]) + as_bytes
pas = UART_Packets.RPI_UART_Packet_AS7341(data_as)
print(f'AS7341 Id: {pas.packet_id}, valid: {pas.valid}')
for i in range(11):
	val = getattr(pas, f'channel_{i}')
	print(f' channel_{i}: {val}')
	assert val == channels[i]


print('\nTesting UNIX_TIME packet builder/unpack (raw)')
unix_sec = 1637020000
unix_tz = -5
p_unix = UART_Packets.RPI_UART_Packet_UNIX_TIME(unix_sec, unix_tz)
print(f'UNIX_TIME packet_id: {p_unix.packet_id}, unixSec: {p_unix.unixTimeSec}, tz: {p_unix.unixTimezone}, raw: {p_unix.raw}')
assert p_unix.packet_id == UART_Packets.UARTPackets.RPI_UNIX_TIME_PKT_ID
# raw should match struct.pack('<BIb', packet_id, unix_sec, unix_tz)
expected_unix_raw = struct.pack('<BIb', int(p_unix.packet_id), p_unix.unixTimeSec, int(p_unix.unixTimezone))
assert p_unix.raw == expected_unix_raw


print('\nTesting UNIX_TIME_Request packet unpacking')
data_unix_req = bytes([UART_Packets.UARTPackets.RPI_UNIX_TIME_REQUEST_PKT_ID])
punreq = UART_Packets.RPI_UART_Packet_UNIX_TIME_Request(data_unix_req)
print(f'UNIX_REQ Id: {punreq.packet_id}, valid: {punreq.valid}')
assert punreq.packet_id == UART_Packets.UARTPackets.RPI_UNIX_TIME_REQUEST_PKT_ID
assert punreq.valid is True

print('\nAll packet unpacking tests passed.')
