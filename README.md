# AI-Aided Systems Engineering Demo - Traffic Light Controller

A Raspberry Pi-based traffic light controller demonstration project showcasing state machine design and implementation using Python. This project demonstrates how formal state machine specifications can be translated into working hardware implementations.

## 🌟 Features

- **Automatic Traffic Light Cycle** (`main.py`): Continuously cycles through Red → Green → Yellow states with automatic timer-based transitions
- **Button-Triggered Traffic Light** (`main_button.py`): Waits for button press to initiate a complete traffic light cycle through all states
- **State Machine Implementation**: Uses the `python-statemachine` library for clean, maintainable state management
- **PlantUML Documentation**: Visual state machine diagrams and hardware internal block diagrams
- **GPIO Control**: Direct hardware control using RPi.GPIO library

## 📋 Hardware Requirements

- Raspberry Pi (any model with GPIO pins)
- 3 LEDs (Red, Yellow, Green)
- 3 Resistors (220-330Ω recommended)
- Push button (for button-triggered version)
- Breadboard and jumper wires

## 🔌 Hardware Connections

### LED Connections (Both Versions)
- **Red LED**: Anode → 220-330Ω resistor → GPIO 18 (BCM); Cathode → GND
- **Yellow LED**: Anode → 220-330Ω resistor → GPIO 23 (BCM); Cathode → GND
- **Green LED**: Anode → 220-330Ω resistor → GPIO 24 (BCM); Cathode → GND

### Button Connection (Button-Triggered Version Only)
- **Push Button**: One leg → GPIO 25 (BCM); Other leg → 3.3V
- Internal pull-down resistor is configured in software

> **Note**: GPIO pin numbers refer to BCM (Broadcom) numbering, not physical pin numbers. Use `pinout` command on Raspberry Pi to find the correct physical pins.

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai_aided_sys_eng_demo
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or with system-wide installation (requires sudo):
   ```bash
   sudo pip3 install -r requirements.txt --break-system-packages
   ```

## 💻 Usage

### Automatic Traffic Light (`main.py`)

Runs continuously, automatically cycling through traffic light states:

```bash
sudo python3 src/main.py
```

**State Cycle**: Red (5s) → Green (5s) → Yellow (2s) → Red (repeats)

Press `Ctrl+C` to stop.

### Button-Triggered Traffic Light (`main_button.py`)

Waits for button press to start the traffic light cycle:

```bash
sudo python3 src/main_button.py
```

**State Cycle**: 
- **Idle**: All LEDs on, waiting for button press
- **Button Press** → Red → Red+Yellow → Green → Yellow → Red → Idle

Each traffic light state lasts 2 seconds. The cycle returns to idle after completion.

Press `Ctrl+C` to stop.

> **Note**: `sudo` may be required for GPIO access depending on your Raspberry Pi configuration.

## 📁 Project Structure

```
ai_aided_sys_eng_demo/
├── docs/
│   ├── traffic_light.puml              # Automatic traffic light state machine
│   ├── traffic_light_button.puml       # Button-triggered state machine
│   └── traffic_light_ibd.puml          # Hardware internal block diagram
├── src/
│   ├── main.py                         # Automatic traffic light implementation
│   └── main_button.py                  # Button-triggered traffic light implementation
├── requirements.txt                    # Python dependencies
└── README.md                           # This file
```

## 📊 State Machine Diagrams

The project includes PlantUML state machine diagrams that define the system behavior:

- **`traffic_light.puml`**: Defines the automatic cycling state machine
- **`traffic_light_button.puml`**: Defines the button-triggered state machine with idle state
- **`traffic_light_ibd.puml`**: Hardware architecture diagram showing GPIO connections and LED circuits

These diagrams can be viewed using any PlantUML renderer or IDE plugin.

## 🔧 Technical Details

### State Machine Library
The project uses [`python-statemachine`](https://github.com/fgmacedo/python-statemachine) for state management, providing:
- Clean state definitions
- Automatic transition handling
- State entry/exit hooks
- Thread-safe operations

### GPIO Configuration
- **Mode**: BCM (Broadcom) pin numbering
- **LEDs**: Configured as outputs
- **Button**: Configured as input with internal pull-down resistor
- **Warnings**: Suppressed for clean console output

### Timer Implementation
- Uses Python's `threading.Timer` for non-blocking state transitions
- Timer threads are daemon threads that automatically clean up on exit

## 🎓 Educational Value

This project demonstrates:
- **Systems Engineering**: From PlantUML specifications to working hardware
- **State Machine Design**: Formal state definitions and transitions
- **Hardware Integration**: Raspberry Pi GPIO control
- **Software Architecture**: Clean separation of state logic and hardware control
- **Embedded Systems**: Real-time behavior with timer-based state transitions

## 📝 License

This is a demonstration project for educational purposes.

## 🤝 Contributing

Feel free to fork this project and experiment with:
- Different timer durations
- Additional states (e.g., flashing states)
- Sensor integration
- Network control
- Multiple traffic lights

---

**Happy Tinkering! 🚦**
