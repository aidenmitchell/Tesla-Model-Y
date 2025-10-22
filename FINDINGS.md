# Tesla Model Y CAN Bus Access Findings

## Summary
Tesla Model Y accessed via OBD-II adapter uses **UDS Service 22 (ReadDataByIdentifier)** rather than passive CAN monitoring. The car responds to diagnostic requests but does not broadcast vehicle data passively on the OBD-II accessible bus.

## Hardware Setup
- **Adapter**: vLinker MS (STN2120 chipset)
- **Connection**: Center console 26-pin to OBD-II
- **App**: Sidecar
- **Bus Accessed**: CAN3 (Vehicle/Powertrain bus)

## Discovery Method
PID scanner found **121 responsive UDS extended PIDs** in range 0x203E - 0x2090+

### Sample Responding PIDs:
- 0x203E, 0x203F, 0x2040, 0x2041, 0x2042, 0x2044, 0x2045, 0x2047, 0x2048, etc.
- All respond from ECU ID **0x7E8** (likely Gateway or BMS)
- Request format: `7E0 03 22 [PID_HI] [PID_LO]`
- Response format: `7E8 [LEN] 62 [PID_HI] [PID_LO] [DATA...]`

## Key CAN Messages from Model3CAN.dbc

These are the actual vehicle data messages, but they're NOT broadcast on OBD-II bus - they must be requested via UDS:

### Battery Management System (BMS)
| CAN ID | Hex  | Name | Key Signals |
|--------|------|------|-------------|
| 530 | 0x212 | BMS_status | contactorState, hvState, isolationResistance, state, uiChargeStatus, chgPowerAvailable |
| 658 | 0x292 | BMS_SOC | SOCmin, SOCUI, SOCave, SOCmax, BattBeginningOfLifeEnergy, battTempPct |
| 850 | 0x352 | BMS_energyStatus | (energy data) |
| 594 | 0x252 | BMS_powerAvailable | (power limits) |
| 786 | 0x312 | BMSthermal | (thermal management) |
| 722 | 0x2D2 | BMSVAlimits | (voltage/amperage limits) |

### Drivetrain
| CAN ID | Hex  | Name | Key Signals |
|--------|------|------|-------------|
| 599 | 0x257 | DIspeed | vehicleSpeed, uiSpeed |
| 280 | 0x118 | DI_systemStatus | (drivetrain status) |

### Charging
| CAN ID | Hex  | Name | Key Signals |
|--------|------|------|-------------|
| 680 | 0x2A8 | CMPD_state | inputHVCurrent, inputHVPower, inputHVVoltage |

## Signal Decode Examples

### BMS_SOC (ID 0x292 / 658)
```
Byte layout (8 bytes):
  Bit 0-9:   SOCmin (scale: 0.1, unit: %)
  Bit 10-19: SOCUI (scale: 0.1, unit: %)
  Bit 20-29: SOCmax (scale: 0.1, unit: %)
  Bit 30-39: SOCave (scale: 0.1, unit: %)
  Bit 40-49: BattBeginningOfLifeEnergy (scale: 0.1, unit: kWh)
  Bit 50-57: BMS_battTempPct (scale: 0.4, unit: %)
```

### BMS_status (ID 0x212 / 530)
```
Byte layout (8 bytes):
  Bit 8-10:  contactorState (0-6 enum)
  Bit 11-13: uiChargeStatus (0-5 enum)
  Bit 16-18: hvState (0-6 enum)
  Bit 19-28: isolationResistance (scale: 10, unit: kOhm)
  Bit 32-35: state (0-10 enum)
  Bit 40-50: chgPowerAvailable (scale: 0.125, unit: kW)
```

### DI_vehicleSpeed (ID 0x257 / 599)
```
Byte layout (8 bytes):
  Bit 12-23: vehicleSpeed (scale: 0.08, offset: -40, unit: kph)
```

## Next Steps

1. **Map UDS PIDs to CAN messages**: Determine which Service 22 PID returns which CAN message data
2. **Test hypothesis**: Request a known PID and compare response to expected CAN message format
3. **Build signalset**: Create proper signal definitions with bit positions and scaling
4. **Decode all 121 PIDs**: Reverse engineer what each responding PID contains

## UDS Protocol Details

- **Request**: Send to 0x7E0
- **Response**: Receive from 0x7E8
- **Service**: 0x22 (ReadDataByIdentifier)
- **Format**: Request = `[LEN] 22 [DID_HI] [DID_LO]`
- **Format**: Response = `[LEN] 62 [DID_HI] [DID_LO] [DATA...]`

## References

- [Model3CAN.dbc](https://github.com/joshwardell/model3dbc) - Josh Wardell's reverse-engineered CAN database
- [Sidecar Documentation](https://sidecar.clutch.engineering/scanning/extended-pids/)
- Tesla Motors Club forums - CAN bus discussions
- Scan My Tesla app - Community reverse engineering

## License Note

Per Sidecar documentation: "All extended PIDs are licensed under a CC BY-SA 4.0 license"
