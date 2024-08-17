""" WaterFurnace Aurora ModBus interface

Based on Ruby code at https://github.com/ccutrer/waterfurnace_aurora

"""
# Aurora interface definition


# Conversion functions: parse list of register in specified data types

def to_bytes(regs):
	""" Converts register array to byte array

	Parameters:

		regs (list): List of 16-bit registers integer values
	"""
	return b''.join(r.to_bytes(2, 'big') for r in regs)

def to_uint16(regs):
	assert len(regs) == 1
	return regs[0]

def to_int16(regs):
	assert len(regs) == 1
	r = regs[0]
	return r - 0x10000 if (r & 0x8000) else r

def to_uint32(regs):
	assert len(regs) == 2
	return int.from_bytes(to_bytes(regs), 'big', signed=False)

def to_int32(regs):
	assert len(regs) == 2
	return int.from_bytes(to_bytes(regs), 'big', signed=True)

def to_uint16_div100(regs):
	return to_uint16(regs) / 100.0

def to_uint16_div10(regs):
	return to_uint16(regs) / 10.0

def to_int16_div10(regs):
	return to_int16(regs) / 10.0

def to_string(regs):
	return to_bytes(regs).decode('ascii')

  # NEGATABLE = ->(v) { (v & 0x8000 == 0x8000) ? v - 0x10000 : v }
  # TO_HUNDREDTHS = ->(v) { v.to_f / 100 }
  # TO_TENTHS = ->(v) { v.to_f / 10 }
  # TO_SIGNED_TENTHS = ->(v) { NEGATABLE.call(v).to_f / 10 }
  # TO_LAST_LOCKOUT = ->(v) { (v & 0x8000 == 0x8000) ? v & 0x7fff : nil }


BRINE_TYPES = {
    485 : "Antifreeze"
}

def to_brine_type(regs):
	return BRINE_TYPES.get(regs[0], 'Unknown')


DATA_TYPES = { # type_name: (n_words, conversion_func)
	'int16': (1, to_uint16), 
	'uint16': (1, to_uint16), 
	'uint32': (2, to_uint32), 
	'int32': (2, to_int32), 
	'uint16_div100': (1, to_uint16_div100), 
	'uint16_div10': (1, to_uint16_div10), 
	'int16_div10': (1, to_int16_div10), 

	'str4': (4, to_string), 
	'str5': (5, to_string),
	'str8': (8, to_string),
	'str12': (12, to_string), 
	'str13': (13, to_string), 
	'brine_type' : (1, to_brine_type)
}


REGISTER_NAMES = { # register_address: (register_name, conversion_func, formatting_func)
    0: ("Test Mode Flag", None, None), # 0x100 for enabled; this might have other flags None, None),
    1: ("Random Start Delay", None, None),
    2: ("ABC Program Version", 'uint16_div100', None),
    3: ("??? Version?", 'uint16_div100', None),
    4: ("DIP Switch Override", None, None),
    6: ("Compressor Anti-Short Cycle Delay", None, None),
    8: ("ABC Program Revision", None, None),
    9: ("Compressor Minimum Run Time", None, None),
    15: ("Blower Off Delay", None, None),
    16: ("Line Voltage", 'uint16', 'V'),
    17: ("Aux/E Heat Staging Delay", None, None), # this is how long aux/eheat have been requested in seconds 
    # when in eheat mode (explicit on the thermostat), it will stage up to eh2 after 130s
    # when in aux mode (thermostat set to heat; compressor at full capacity), it will stage up to eh2 after 310s
    19: ("Cooling Liquid Line Temperature (FP1)", 'int16_div10', None),
    20: ("Air Coil Temperature (FP2)", 'int16_div10', None),
    21: ("Condensate", None, None),# >= 270 normal, otherwise fault 
    25: ("Last Fault Number", None, None),# high bit set if locked out 
    26: ("Last Lockout", None, None),
    27: ("System Outputs (At Last Lockout)", None, None),
    28: ("System Inputs (At Last Lockout)", None, None),
    30: ("System Outputs", None, None),
    31: ("Status", None, None),
    32: ("Thermostat Input Override", None, None),
    33: ("DIP Switch Status", None, None),
    36: ("ABC Board Rev", None, None),
    45: ("Test Mode (write)", None, None), # 1 to enable 
    47: ("Clear Fault History", None, None), # 0x5555 to clear 
    50: ("ECM Speed Low (== 5)", None, None),
    51: ("ECM Speed Med (== 5)", None, None),
    52: ("ECM Speed High (== 5)", None, None),
    54: ("ECM Speed Actual", None, None),
    84: ("Slow Opening Water Valve Delay", None, None),
    85: ("Test Mode Timer", None, None),
    88: ("ABC Program", 'str4', None),
    92: ("Model Number", 'str12', None),
    105: ("Serial Number", 'str5', None),
    110: ("Reheat Delay", None, None),
    112: ("Line Voltage Setting", 'uint16', 'V'),
    201: ("Discharge Pressure", None, None), # I can't figure out how this number is represented; 
    203: ("Suction Pressure", None, None),
    205: ("Discharge Temperature", None, None),
    207: ("Loop Entering Water Temperature", None, None),
    209: ("Compressor Ambient Temperature", None, None),
    211: ("VS Drive Details (General 1)", None, None),
    212: ("VS Drive Details (General 2)", None, None),
    213: ("VS Drive Details (Derate 1)", None, None),
    214: ("VS Drive Details (Derate 2)", None, None),
    215: ("VS Drive Details (Safemode 1)", None, None),
    216: ("VS Drive Details (Safemode 2)", None, None),
    217: ("VS Drive Details (Alarm 1)", None, None),
    218: ("VS Drive Details (Alarm 2)", None, None),
    280: ("EEV2 Ctl", None, None),
    281: ("EEV Superheat", None, None), # ?? data format 
    282: ("EEV Open %", None, None),
    283: ("Suction Temperature", None, None),  ## ?? data format 
    284: ("Saturated Suction Temperature", None, None), ## ?? data format 
    321: ("VS Pump Min", None, None),
    322: ("VS Pump Max", None, None),
    323: ("VS Pump Speed Manual Control", None, None),
    325: ("VS Pump Output", None, None),
    326: ("VS Pump Fault", None, None),
    340: ("Blower Only Speed", None, None),
    341: ("Lo Compressor ECM Speed", None, None),
    342: ("Hi Compressor ECM Speed", None, None),
    344: ("ECM Speed", None, None),
    346: ("Cooling Airflow Adjustment", 'int16', None),
    347: ("Aux Heat ECM Speed", None, None),
    362: ("Active Dehumidify", None, None), # any value is true 
    400: ("DHW Enabled", None, None),
    401: ("DHW Setpoint", 'uint16_div10', None),
    402: ("Brine Type", 'brine_type', None) ,
    403: ("Flow Meter Type", None, None),
    404: ("Blower Type", None, None),
    405: ("SmartGrid Trigger", None, None),
    406: ("SmartGrid Action", None, None), # 0/1 for 1/2; see 414 
    407: ("Off Time Length", None, None),
    408: ("HA Alarm 1 Trigger", None, None),
    409: ("HA Alarm 1 Action", None, None),
    410: ("HA Alarm 2 Trigger", None, None),
    411: ("HA Alarm 2 Action", None, None),
    412: ("Energy Monitor", None, None), # 0 none, 1 compressor monitor, 2 energy monitor 
    413: ("Pump Type", None, None),
    414: ("On Peak/SmartGrid", None, None), # 0x0001 only 
    416: ("Energy Phase Type", None, None),
    417: ("Power Adjustment Factor L", 'uint16_div100', None),
    418: ("Power Adjustment Factor H", 'uint16_div100', None),
    419: ("Loop Pressure Trip", 'uint16_div10', None),
    460: ("IZ2 Heartbeat?", None, None),
    461: ("IZ2 Heartbeat?", None, None),
    462: ("IZ2 Status", None, None), # 5 when online; 1 when in setup mode 
    483: ("Number of IZ2 Zones", None, None),
    501: ("Set Point", 'int16_div10', None), # only read by AID tool? this is _not_ heating/cooling set point 
    502: ("Ambient Temperature", 'int16_div10', None),
    564: ("IZ2 Compressor Speed Desired", None, None),
    565: ("IZ2 Blower % Desired", None, None),
    567: ("Entering Air", 'int16_div10', None),
    710: ("Fault Description", None, None),
    740: ("Entering Air", 'int16_div10', None),
    741: ("Relative Humidity", None, None),
    745: ("Heating Set Point", 'uint16_div10', None),
    746: ("Cooling Set Point", 'uint16_div10', None),
    747: ("Ambient Temperature", 'int16_div10', None), # from communicating thermostat? but set to 0 when mode is off? 
    800: ("Thermostat Installed", None, None),
    801: ("Thermostat Version", 'uint16_div100', None),
    802: ("Thermostat Revision", None, None),
    803:( "??? Installed", None, None),
    804:( "??? Version", 'uint16_div100', None),
    805:( "??? Revision", None, None),
    806: ("AXB Installed", None, None),
    807: ("AXB Version", 'uint16_div100', None),
    808: ("AXB Revision", None, None),
    809: ("AHB Installed", None, None),
    810: ("AHB Version", None, None),
    811: ("AHB Revision", None, None),
    812: ("IZ2 Installed", None, None),
    813: ("IZ2 Version", 'uint16_div100', None),
    814: ("IZ2 Revision", None, None),
    815: ("AOC Installed", None, None),
    816: ("AOC Version", 'uint16_div100', None),
    817: ("AOC Revision", 'uint16_div100', None),
    818: ("MOC Installed", None, None),
    819: ("MOC Version", 'uint16_div100', None),
    820: ("MOC Revision", 'uint16_div100', None),
    824: ("EEV2 Installed", None, None),
    825: ("EEV2 Version", 'uint16_div100', None),
    826: ("EEV2 Revision", None, None),
    827: ("AWL Installed", None, None),
    828: ("AWL Version", 'uint16_div100', None),
    829: ("AWL Revision", None, None),
    900: ("Leaving Air", 'int16_div10', None),
    901: ("Suction Pressure", 'uint16_div10', None),
    903: ("SuperHeat Temperature", 'int16_div10', None),
    908: ("EEV Open %", None, None),
    909: ("SubCooling (Cooling)", None, None),
    1103: ("AXB Inputs", None, None),
    1104: ("AXB Outputs", None, None),
    1105: ("Blower Amps", 'uint16_div10', 'A'),
    1106: ("Aux Amps", 'uint16_div10', 'A'),
    1107: ("Compressor 1 Amps", 'uint16_div10', 'A'),
    1108: ("Compressor 2 Amps", 'uint16_div10', 'A'),
    1109: ("Heating Liquid Line Temperature", 'int16_div10', None),
    1110: ("Leaving Water", 'int16_div10', None),
    1111: ("Entering Water", 'int16_div10', None),
    1112: ("Leaving Air Temperature", 'int16_div10', None),
    1113: ("Suction Temperature", 'int16_div10', None),
    1114: ("DHW Temperature", 'int16_div10', None),
    1115: ("Discharge Pressure", 'uint16_div10', None),
    1116: ("Suction Pressure", 'uint16_div10', None),
    1117: ("Waterflow", 'uint16_div10', None),
    1119: ("Loop Pressure", 'uint16_div10', None), # only valid < 1000psi 
    1124: ("Saturated Evaporator Temperature", 'int16_div10', None),
    1125: ("SuperHeat", 'int16_div10', None),
    1126: ("Vaport Injector Open %", None, None),
    1134: ("Saturated Condensor Discharge Temperature", 'int16_div10', None),
    1135: ("SubCooling (Heating)", 'int16_div10', None),
    1136: ("SubCooling (Cooling)", 'int16_div10', None),
    1146: ("Compressor Watts", 'uint32', 'W'),
    1148: ("Blower Watts", 'uint32', 'W'),
    1150: ("Aux Watts", 'uint32', 'W'),
    1152: ("Total Watts", 'uint32', 'W'),
    1154: ("Heat of Extraction", 'int32', 'W'),
    1156: ("Heat of Rejection", 'int32', 'W'),
    1164: ("Pump Watts", 'uint32', 'W'),
    # this combines thermostat/iz2 desired speed with manual operation override
    3000: ("Compressor Speed Desired", None, None),
    # this shows the actual speed
    # it can differ from desired during a ramp to the desired speed, or
    # the periodic ramp up to speed 6 that's not visible in the desired speed
    3001: ("Compressor Speed Actual", None, None),
    3002: ("Manual Operation", None, None),
    3027: ("Compressor Speed", None, None),
    3220: ("VS Drive Details (General 1)", None, None),
    3221: ("VS Drive Details (General 2)", None, None),
    3222: ("VS Drive Details (Derate 1)", None, None),
    3223: ("VS Drive Details (Derate 2)", None, None),
    3224: ("VS Drive Details (Safemode 1)", None, None),
    3225: ("VS Drive Details (Safemode 2)", None, None),
    3226: ("VS Drive Details (Alarm 1)", None, None),
    3227: ("VS Drive Details (Alarm 2)", None, None),
    3322: ("VS Drive Discharge Pressure", 'uint16_div10', None),
    3323: ("VS Drive Suction Pressure", 'uint16_div10', None),
    3325: ("VS Drive Discharge Temperature", 'int16_div10', None),
    3326: ("VS Drive Compressor Ambient Temperature", 'int16_div10', None),
    3327: ("VS Drive Temperature", 'int16_div10', None),
    3330: ("VS Drive Entering Water Temperature", 'int16_div10', None),
    3331: ("VS Drive Line Voltage", None, None),
    3332: ("VS Drive Thermo Power", None, None),
    3422: ("VS Drive Compressor Power", 'uint32', None),
    3424: ("VS Drive Supply Voltage", 'uint32', None),
    3522: ("VS Drive Inverter Temperature", 'int16_div10', None),
    3523: ("VS Drive UDC Voltage", None, None),
    3524: ("VS Drive Fan Speed", None, None),
    3804: ("VS Drive Details (EEV2 Ctl)", None, None),
    3808: ("VS Drive EEV2 % Open", None, None),
    3903: ("VS Drive Suction Temperature", 'int16_div10', None),
    3904: ("VS Drive Leaving Air Temperature?", None, None),
    3905: ("VS Drive Saturated Evaporator Discharge Temperature", 'int16_div10', None),
    3906: ("VS Drive SuperHeat Temperature", 'int16_div10', None),
    12_005: ("Fan Configuration", None, None),
    12_006: ("Heating Mode", None, None),
    12_309: ("De/Humidifier Mode", None, None),
    12_310: ("De/Humidifier Setpoints", None, None),
    12_606: ("Heating Mode (write)", None, None),
    12_619: ("Heating Setpoint (write)", 'uint16_div10', None),
    12_620: ("Cooling Setpoint (write)", 'uint16_div10', None),
    12_621: ("Fan Mode (write)", None, None),
    12_622: ("Intermittent Fan On Time (write)", None, None),
    12_623: ("Intermittent Fan Off Time (write)", None, None),
    21_114: ("IZ2 De/Humidifier Mode (write)", None, None),
    21_115: ("IZ2 De/Humidifier Setpoints (write)", None, None),
    31_003: ("Outdoor Temp", 'int16_div10', None),
    31_005: ("IZ2 Demand", None, None),
    31_109: ("De/Humidifier Mode", None, None),
    31_110: ("Manual De/Humidification Setpoints", None, None),
    31_400: ("Dealer Name", 'str13', None),
    31_413: ("Dealer Phone", 'str8', None),
    31_421: ("Dealer Address 1", 'str13', None),
    31_434: ("Dealer Address 2", 'str13', None),
    31_447: ("Dealer Email", 'str13', None),
    31_460: ("Dealer Website", 'str13', None),
  }

  # .merge(ignore(89..91))
  #                  .merge(ignore(93..104))
  #                  .merge(ignore(106..109))
  #                  .merge(faults(601..699))
  #                  .merge(ignore(711..717))
  #                  .merge(zone_registers)
  #                  .merge(ignore(1147, 1149, 1151, 1153, 1155, 1157, 1165))
  #                  .merge(ignore(3423, 3425))
  #                  .merge(ignore(31_401..31_412))
  #                  .merge(ignore(31_414..31_420))
  #                  .merge(ignore(31_422..31_433))
  #                  .merge(ignore(31_435..31_446))
  #                  .merge(ignore(31_447..31_459))
  #                  .merge(ignore(31_461..31_472))

# these are the valid ranges (i.e. the ABC will return _some_ value)
# * means 6 sequential ranges of equal size (i.e. must be repeated for each
# IZ2 zone)
# ==================================================================
REGISTER_RANGES = (  # (start_register, end_register)
    (0, 155),
    (170, 253),
    (260, 260),
    (280, 288),
    (300, 301),
    (320, 326),
    (340, 348),
    (360, 368),
    (400, 419),
    (440, 516),
    (550, 573),
    (600, 749),
    (800, 913),
    (1090, 1165),
    (1200, 1263),
    (2000, 2026),
    (2100, 2129),
    (2800, 2849),
    (2900, 2915),
    (2950, 2959),
    (3000, 3003),
    (3020, 3030),
    (3040, 3049),
    (3060, 3063),
    (3100, 3105),
    (3108, 3115),
    (3118, 3119),
    (3200, 3253),
    (3300, 3332),
    (3400, 3431),
    (3500, 3524),
    (3600, 3609),
    (3618, 3634),
    (3700, 3714),
    (3800, 3809),
    (3818, 3834),
    (3900, 3914),
    (12_000, 12_019),
    (12_098, 12_099),
    (12_100, 12_119),
    (12_200, 12_239),
    (12_300, 12_319),
    (12_400, 12_569),
    (12_600, 12_639),
    (12_700, 12_799),
    (20_000, 20_099),
    (21_100, 21_136),
    (21_200, 21_265),
    (21_400, 21_472),
    (21_500, 21_589),
    (22_100, 22_162), # *
    (22_200, 22_262), # *
    (22_300, 22_362), # *
    (22_400, 22_462), # *
    (22_500, 22_562), # *
    (22_600, 22_662), # *
    (30_000, 30_099),
    (31_000, 31_034),
    (31_100, 31_129),
    (31_200, 31_229),
    (31_300, 31_329),
    (31_400, 31_472),
    (32_100, 32_162), # *
    (32_200, 32_262), # *
    (32_300, 32_362), # *
    (32_400, 32_462), # *
    (32_500, 32_562), # *
    (32_600, 32_662), # *
    (60_050, 60_053),
    (60_100, 60_109),
    (60_200, 60_200),
    (61_000, 61_009)
    )
"""
REGISTER_CONVERTERS = {
    # TO_HUNDREDTHS => [2, 3, 417, 418, 801, 804, 807, 813, 816, 817, 819, 820, 825, 828],
    method(:dipswitch_settings) => [4, 33],
    # TO_TENTHS => [401, 419, 745, 746, 901,
    #               1105, 1106, 1107, 1108, 1115, 1116, 1117, 1119,
    #               3322, 3323,
    #               12_619, 12_620,
                  21_203, 21_204,
                  21_212, 21_213,
                  21_221, 21_222,
                  21_230, 22_131,
                  21_239, 21_240,
                  21_248, 21_249],
    # TO_SIGNED_TENTHS => [19, 20, 501, 502, 567, 740, 747, 900, 903,
    #                      1109, 1110, 1111, 1112, 1113, 1114, 1124, 1125, 1134, 1135, 1136,
    #                      3325, 3326, 3327, 3330, 3522, 3903, 3905, 3906,
                         31_003, 31_007, 31_010, 31_013, 31_016, 31_019, 31_022],
    TO_LAST_LOCKOUT => [26],
    ->(v) { from_bitmask(v, SYSTEM_OUTPUTS) } => [27, 30],
    ->(v) { from_bitmask(v, SYSTEM_INPUTS) } => [28],
    method(:status) => [31],
    method(:thermostat_override) => [32],
    ->(v) { !v.zero? } => [45, 362, 400],
    # ->(registers, idx) { to_string(registers, idx, 4) } => [88],
    # ->(registers, idx) { to_string(registers, idx, 12) } => [92],
    # ->(registers, idx) { to_string(registers, idx, 5) } => [105],
    ->(v) { from_bitmask(v, VS_DRIVE_DERATE) } => [214, 3223],
    ->(v) { from_bitmask(v, VS_SAFE_MODE) } => [216, 3225],
    ->(v) { from_bitmask(v, VS_ALARM1) } => [217, 3226],
    ->(v) { from_bitmask(v, VS_ALARM2) } => [218, 3227],
    ->(v) { from_bitmask(v, VS_EEV2) } => [280, 3804],
    method(:vs_manual_control) => [323],
    NEGATABLE => [346],
    ->(v) { BRINE_TYPE[v] } => [402],
    ->(v) { FLOW_METER_TYPE[v] } => [403],
    ->(v) { BLOWER_TYPE[v] } => [404],
    ->(v) { v.zero? ? :closed : :open } => [405, 408, 410],
    ->(v) { SMARTGRID_ACTION[v] } => [406],
    ->(v) { HA_ALARM[v] } => [409, 411],
    ->(v) { ENERGY_MONITOR_TYPE[v] } => [412],
    ->(v) { PUMP_TYPE[v] } => [413],
    ->(v) { PHASE_TYPE[v] } => [416],
    method(:iz2_fan_desired) => [565],
    ->(registers, idx) { to_string(registers, idx, 8) } => [710],
    ->(v) { COMPONENT_STATUS[v] } => [800, 803, 806, 812, 815, 818, 824, 827],
    method(:axb_inputs) => [1103],
    ->(v) { from_bitmask(v, AXB_OUTPUTS) } => [1104],
    # method(:to_uint32) => [1146, 1148, 1150, 1152, 1164, 3422, 3424],
    # method(:to_int32) => [1154, 1156],
    method(:manual_operation) => [3002],
    method(:thermostat_configuration2) => [12_006],
    ->(v) { HEATING_MODE[v] } => [12_606, 21_202, 21_211, 21_220, 21_229, 21_238, 21_247],
    ->(v) { FAN_MODE[v] } => [12_621, 21_205, 21_214, 21_223, 21_232, 21_241, 21_250],
    ->(v) { from_bitmask(v, HUMIDIFIER_SETTINGS) } => [12_309, 21_114, 31_109],
    ->(v) { { humidification_target: v >> 8, dehumidification_target: v & 0xff } } => [12_310, 21_115, 31_110],
    method(:iz2_demand) => [31_005],
    method(:zone_configuration1) => [12_005, 31_008, 31_011, 31_014, 31_017, 31_020, 31_023],
    method(:zone_configuration2) => [31_009, 31_012, 31_015, 31_018, 31_021, 31_024],
    method(:zone_configuration3) => [31_200, 31_203, 31_206, 31_209, 31_212, 31_215],
    ->(registers, idx) { to_string(registers, idx, 13) } => [31_400],
    ->(registers, idx) { to_string(registers, idx, 8) } => [31_413],
    ->(registers, idx) { to_string(registers, idx, 13) } => [31_421],
    ->(registers, idx) { to_string(registers, idx, 13) } => [31_434],
    ->(registers, idx) { to_string(registers, idx, 13) } => [31_447],
    ->(registers, idx) { to_string(registers, idx, 13) } => [31_460]
  }.freeze
"""


class Aurora:
	def __init__(port='/dev/ttyUSB0'):
		pass