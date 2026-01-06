"""
Traffic light controller implemented with python-statemachine and RPi.GPIO.

States and transitions are defined in docs/traffic_light.puml:
  Red --(5s)--> Green --(5s)--> Yellow --(2s)--> Red

Transitions are automatically fired using timers when entering each state.
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


def setup_gpio() -> None:
    """Configure GPIO outputs for the three LEDs."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN_RED, GPIO.OUT)
    GPIO.setup(PIN_YELLOW, GPIO.OUT)
    GPIO.setup(PIN_GREEN, GPIO.OUT)


def set_lights(red: bool, yellow: bool, green: bool) -> None:
    """Drive the LED pins."""
    GPIO.output(PIN_RED, GPIO.HIGH if red else GPIO.LOW)
    GPIO.output(PIN_YELLOW, GPIO.HIGH if yellow else GPIO.LOW)
    GPIO.output(PIN_GREEN, GPIO.HIGH if green else GPIO.LOW)


class TrafficLightMachine(StateMachine):
    red = State("Red", initial=True)
    green = State("Green")
    yellow = State("Yellow")

    timer_5s = red.to(green) | green.to(yellow)
    timer_2s = yellow.to(red)

    def __init__(self) -> None:
        self._timer: Optional[threading.Timer] = None
        self._lock = threading.Lock()
        setup_gpio()
        super().__init__()  # This will trigger on_enter_red() which handles setup

    def _clear_timer(self) -> None:
        with self._lock:
            if self._timer:
                self._timer.cancel()
                self._timer = None

    def _schedule(self, delay: float, event_fn) -> None:
        """Schedule a transition event after `delay` seconds."""
        self._clear_timer()

        def fire():
            event_fn()

        timer = threading.Timer(delay, fire)
        timer.daemon = True
        with self._lock:
            self._timer = timer
        timer.start()

    def _apply_outputs_for_state(self, state_id: str) -> None:
        if state_id == "Red":
            set_lights(True, False, False)
        elif state_id == "Green":
            set_lights(False, False, True)
        elif state_id == "Yellow":
            set_lights(False, True, False)

    # State entry hooks
    def on_enter_red(self) -> None:
        self._apply_outputs_for_state("Red")
        self._schedule(5.0, self.timer_5s)

    def on_enter_green(self) -> None:
        self._apply_outputs_for_state("Green")
        self._schedule(5.0, self.timer_5s)

    def on_enter_yellow(self) -> None:
        self._apply_outputs_for_state("Yellow")
        self._schedule(2.0, self.timer_2s)

    def stop(self) -> None:
        """Cancel timers and clean up GPIO."""
        self._clear_timer()
        GPIO.cleanup()


def main() -> None:
    machine = TrafficLightMachine()

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