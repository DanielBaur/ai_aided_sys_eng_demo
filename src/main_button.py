"""
Traffic light controller with button trigger implemented with python-statemachine and RPi.GPIO.

States and transitions are defined in docs/traffic_light_button.puml:
  idle --(button_pressed)--> red1 --(timer)--> red_yellow --(timer)--> green
  --(timer)--> yellow --(timer)--> red2 --(timer)--> idle

Transitions are triggered by button press (idle) or timers (traffic light states).
"""

import signal
import threading
import time
from typing import Optional

import RPi.GPIO as GPIO
from statemachine import State, StateMachine


# GPIO pin mapping
PIN_RED = 18
PIN_YELLOW = 23
PIN_GREEN = 24
PIN_BUTTON = 25  # Button input pin

# Timer duration for all traffic light states (seconds)
TIMER_DURATION = 2.0


def setup_gpio() -> None:
    """Configure GPIO outputs for LEDs and input for button."""
    GPIO.setwarnings(False)  # Suppress warnings about channel reuse and cleanup
    GPIO.cleanup()  # Clean up any previous GPIO state
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN_RED, GPIO.OUT)
    GPIO.setup(PIN_YELLOW, GPIO.OUT)
    GPIO.setup(PIN_GREEN, GPIO.OUT)
    GPIO.setup(PIN_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Button with pull-down


def print_current_state(state_name: str) -> None:
    """Print the current state to the console."""
    print(f"Current state: {state_name}")


def turn_on_leds(state_name: str) -> None:
    """Turn on or off LEDs based on the current state."""
    if state_name == "idle":
        # All three LEDs on
        GPIO.output(PIN_RED, GPIO.HIGH)
        GPIO.output(PIN_YELLOW, GPIO.HIGH)
        GPIO.output(PIN_GREEN, GPIO.HIGH)
    elif state_name == "red1":
        # Red LED only
        GPIO.output(PIN_RED, GPIO.HIGH)
        GPIO.output(PIN_YELLOW, GPIO.LOW)
        GPIO.output(PIN_GREEN, GPIO.LOW)
    elif state_name == "red_yellow":
        # Red and Yellow LEDs on
        GPIO.output(PIN_RED, GPIO.HIGH)
        GPIO.output(PIN_YELLOW, GPIO.HIGH)
        GPIO.output(PIN_GREEN, GPIO.LOW)
    elif state_name == "green":
        # Green LED only
        GPIO.output(PIN_RED, GPIO.LOW)
        GPIO.output(PIN_YELLOW, GPIO.LOW)
        GPIO.output(PIN_GREEN, GPIO.HIGH)
    elif state_name == "yellow":
        # Yellow LED only
        GPIO.output(PIN_RED, GPIO.LOW)
        GPIO.output(PIN_YELLOW, GPIO.HIGH)
        GPIO.output(PIN_GREEN, GPIO.LOW)
    elif state_name == "red2":
        # Red LED only
        GPIO.output(PIN_RED, GPIO.HIGH)
        GPIO.output(PIN_YELLOW, GPIO.LOW)
        GPIO.output(PIN_GREEN, GPIO.LOW)


class TrafficLightButtonMachine(StateMachine):
    idle = State("idle", initial=True)
    red1 = State("red1")
    red_yellow = State("red_yellow")
    green = State("green")
    yellow = State("yellow")
    red2 = State("red2")

    # Transitions
    button_pressed = idle.to(red1)
    timer_red1_elapsed = red1.to(red_yellow)
    timer_red_yellow_elapsed = red_yellow.to(green)
    timer_green_elapsed = green.to(yellow)
    timer_yellow_elapsed = yellow.to(red2)
    timer_red2_elapsed = red2.to(idle)

    def __init__(self) -> None:
        self._timer: Optional[threading.Timer] = None
        self._button_thread: Optional[threading.Thread] = None
        self._button_state_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._stop_button_monitoring = threading.Event()
        setup_gpio()
        super().__init__()  # This will trigger on_enter_idle()

    def _clear_timer(self) -> None:
        """Cancel any active timer."""
        with self._lock:
            if self._timer:
                self._timer.cancel()
                self._timer = None

    def _stop_button_monitoring_thread(self) -> None:
        """Stop the button monitoring thread."""
        self._stop_button_monitoring.set()
        # Don't join threads here - they're daemon threads and will exit when stop event is set
        # Trying to join from within the thread itself causes a deadlock

    def start_timer(self, duration: float, transition_event) -> None:
        """Start a timer that triggers the transition event after duration seconds."""
        self._clear_timer()

        def fire():
            transition_event()

        timer = threading.Timer(duration, fire)
        timer.daemon = True
        with self._lock:
            self._timer = timer
        timer.start()

    def wait_for_button_press(self, transition_event) -> None:
        """Continuously check for button press and trigger transition when pressed."""
        self._stop_button_monitoring_thread()  # Stop any existing button thread
        self._stop_button_monitoring.clear()  # Clear the flag after stopping

        def monitor_button():
            while not self._stop_button_monitoring.is_set():
                # Check if button is pressed (HIGH when pressed, assuming active-high)
                button_state = GPIO.input(PIN_BUTTON)
                if button_state == GPIO.HIGH:
                    time.sleep(0.05)  # Debounce
                    if GPIO.input(PIN_BUTTON) == GPIO.HIGH:
                        print(f"Button pressed detected! Triggering transition...")
                        # Set stop event before triggering transition to signal thread exit
                        self._stop_button_monitoring.set()
                        transition_event()
                        break
                time.sleep(0.1)  # Poll every 100ms

        self._button_thread = threading.Thread(target=monitor_button, daemon=True)
        self._button_thread.start()
        
        # Start a separate thread to print button state every second for debugging
        def print_button_state():
            while not self._stop_button_monitoring.is_set():
                button_state = GPIO.input(PIN_BUTTON)
                print(f"Button pin (GPIO {PIN_BUTTON}) state: {'HIGH (pressed)' if button_state == GPIO.HIGH else 'LOW (not pressed)'}")
                time.sleep(1.0)  # Print every second
        
        self._button_state_thread = threading.Thread(target=print_button_state, daemon=True)
        self._button_state_thread.start()

    # State entry hooks
    def on_enter_idle(self) -> None:
        """Entry behavior for idle state."""
        state_name = "idle"
        print_current_state(state_name)
        turn_on_leds(state_name)
        self.wait_for_button_press(self.button_pressed)

    def on_enter_red1(self) -> None:
        """Entry behavior for red1 state."""
        self._stop_button_monitoring_thread()  # Stop button monitoring when leaving idle
        state_name = "red1"
        print_current_state(state_name)
        turn_on_leds(state_name)
        self.start_timer(TIMER_DURATION, self.timer_red1_elapsed)

    def on_enter_red_yellow(self) -> None:
        """Entry behavior for red_yellow state."""
        state_name = "red_yellow"
        print_current_state(state_name)
        turn_on_leds(state_name)
        self.start_timer(TIMER_DURATION, self.timer_red_yellow_elapsed)

    def on_enter_green(self) -> None:
        """Entry behavior for green state."""
        state_name = "green"
        print_current_state(state_name)
        turn_on_leds(state_name)
        self.start_timer(TIMER_DURATION, self.timer_green_elapsed)

    def on_enter_yellow(self) -> None:
        """Entry behavior for yellow state."""
        state_name = "yellow"
        print_current_state(state_name)
        turn_on_leds(state_name)
        self.start_timer(TIMER_DURATION, self.timer_yellow_elapsed)

    def on_enter_red2(self) -> None:
        """Entry behavior for red2 state."""
        state_name = "red2"
        print_current_state(state_name)
        turn_on_leds(state_name)
        self.start_timer(TIMER_DURATION, self.timer_red2_elapsed)

    def stop(self) -> None:
        """Cancel timers, stop button monitoring, and clean up GPIO."""
        self._clear_timer()
        self._stop_button_monitoring_thread()
        GPIO.cleanup()


def main() -> None:
    machine = TrafficLightButtonMachine()

    # Support Ctrl+C to exit cleanly
    stop_event = threading.Event()

    def handle_signal(signum, frame):
        stop_event.set()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    try:
        while not stop_event.is_set():
            time.sleep(0.1)
    finally:
        machine.stop()


if __name__ == "__main__":
    main()
