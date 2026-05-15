# BattleBot Teacher GUI

A graphical user interface for controlling BattleBot robots via the micro:bit teacher device.

## Features

- 🔌 Auto-detect and connect to micro:bit serial ports
- 🔇 Mute/unmute all robots
- 🛑 Stop/enable all robot motors
- ⚔️ Start battles between two players with custom names
- 🏆 Declare winners with victory animation
- 💾 Automatically saves and remembers player names

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

Or install pyserial directly:
```bash
pip install pyserial
```

## Usage

1. Connect your micro:bit teacher device via USB

2. Run the GUI:
```bash
python battlebot_gui.py
```

3. In the GUI:
   - Click "Refresh" to scan for serial ports
   - Select your micro:bit port from the dropdown
   - Click "Connect"
   - Use the control buttons to manage your BattleBot classroom!

## Controls

### Global Controls
- **Mute All** / **Unmute All** - Control sound on all robots
- **Stop All Motors** / **Enable All Motors** - Control movement of all robots

### Battle Setup
- Enter robot IDs (0-15) for two players
- Enter player names (optional - they're saved for next time!)
- Click "Start Battle" to begin - only these two robots will be active
- Use "Player 1 Wins!" or "Player 2 Wins!" to declare the winner

### Status Log
The bottom panel shows all commands sent and their status.

## Configuration

Player names are automatically saved to `battlebot_config.json` in the application directory.

## Troubleshooting

**"No serial ports found"**
- Make sure your micro:bit is connected via USB
- Try clicking "Refresh" after connecting the device

**"Not connected to serial port"**
- Click "Connect" after selecting the port
- Make sure no other program is using the serial port (like the Arduino IDE or MakeCode)

**Commands not working**
- Verify the micro:bit is running the BattleBot Teacher application
- Check the status log for error messages
- Try disconnecting and reconnecting

## Platform Notes

### Windows
Works out of the box. The micro:bit typically appears as `COM3` or similar.

### macOS
The micro:bit appears as `/dev/cu.usbmodem*`. You may need to install drivers for some systems.

### Linux
The micro:bit appears as `/dev/ttyACM*`. You may need to add your user to the `dialout` group:
```bash
sudo usermod -a -G dialout $USER
```
Then log out and back in.
