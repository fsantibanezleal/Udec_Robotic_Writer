# Arduino Firmware — Motor Control Protocol

## Overview

This document describes the serial protocol expected by the `ArduinoAdapter` for controlling stepper motors and a servo gripper via an Arduino board.

## Hardware Setup

- **Arduino Mega 2560** (recommended) or Arduino Uno
- **5x A4988 or DRV8825** stepper motor drivers (one per joint)
- **1x Servo motor** for the gripper
- **5x Stepper motors** (NEMA 17 recommended)
- **Power supply**: 12V for stepper drivers, 5V for servo

### Pin Mapping (Example)

| Motor | STEP Pin | DIR Pin | ENABLE Pin |
|-------|----------|---------|------------|
| 1 (Base) | 2 | 3 | 4 |
| 2 (Shoulder) | 5 | 6 | 7 |
| 3 (Elbow) | 8 | 9 | 10 |
| 4 (Pitch) | 11 | 12 | 13 |
| 5 (Roll) | 22 | 23 | 24 |
| Gripper (Servo) | 44 | - | - |

## Serial Protocol

**Baud rate**: 115200
**Line terminator**: `\n` (newline)

### Commands

| Command | Format | Example | Description |
|---------|--------|---------|-------------|
| Move | `M<id><dir><steps>` | `M1+500` | Move motor 1 forward 500 steps |
| Stop | `S<id>` | `S2` | Stop motor 2 |
| Home | `H` | `H` | Home all motors |
| Query | `Q<id>` | `Q3` | Query motor 3 position |
| Gripper | `G<angle>` | `G90` | Set gripper servo to 90° |
| Emergency | `E` | `E` | Stop all motors immediately |

### Responses

| Response | Format | Description |
|----------|--------|-------------|
| OK | `OK` | Command acknowledged |
| Position | `POS:<id>:<steps>` | Position query response |
| Error | `ERR:<message>` | Error description |

## Example Arduino Sketch

```cpp
#include <AccelStepper.h>
#include <Servo.h>

// Motor definitions
AccelStepper motors[5] = {
    AccelStepper(AccelStepper::DRIVER, 2, 3),   // Base
    AccelStepper(AccelStepper::DRIVER, 5, 6),   // Shoulder
    AccelStepper(AccelStepper::DRIVER, 8, 9),   // Elbow
    AccelStepper(AccelStepper::DRIVER, 11, 12), // Pitch
    AccelStepper(AccelStepper::DRIVER, 22, 23), // Roll
};

Servo gripper;
String inputBuffer = "";

void setup() {
    Serial.begin(115200);

    for (int i = 0; i < 5; i++) {
        motors[i].setMaxSpeed(1000);
        motors[i].setAcceleration(500);
    }

    gripper.attach(44);
    gripper.write(0);  // Closed

    Serial.println("OK");
}

void loop() {
    // Run all steppers
    for (int i = 0; i < 5; i++) {
        motors[i].run();
    }

    // Process serial commands
    while (Serial.available()) {
        char c = Serial.read();
        if (c == '\n') {
            processCommand(inputBuffer);
            inputBuffer = "";
        } else {
            inputBuffer += c;
        }
    }
}

void processCommand(String cmd) {
    if (cmd.length() == 0) return;

    char type = cmd.charAt(0);

    switch (type) {
        case 'M': {  // Move
            int id = cmd.charAt(1) - '0' - 1;
            char dir = cmd.charAt(2);
            long steps = cmd.substring(3).toInt();
            if (dir == '-') steps = -steps;

            if (id >= 0 && id < 5) {
                motors[id].move(steps);
                Serial.println("OK");
            } else {
                Serial.println("ERR:Invalid motor ID");
            }
            break;
        }
        case 'S': {  // Stop
            int id = cmd.charAt(1) - '0' - 1;
            if (id >= 0 && id < 5) {
                motors[id].stop();
                Serial.println("OK");
            }
            break;
        }
        case 'H': {  // Home
            for (int i = 0; i < 5; i++) {
                motors[i].moveTo(0);
            }
            Serial.println("OK");
            break;
        }
        case 'Q': {  // Query
            int id = cmd.charAt(1) - '0' - 1;
            if (id >= 0 && id < 5) {
                Serial.print("POS:");
                Serial.print(id + 1);
                Serial.print(":");
                Serial.println(motors[id].currentPosition());
            }
            break;
        }
        case 'G': {  // Gripper
            int angle = cmd.substring(1).toInt();
            angle = constrain(angle, 0, 180);
            gripper.write(angle);
            Serial.println("OK");
            break;
        }
        case 'E': {  // Emergency stop
            for (int i = 0; i < 5; i++) {
                motors[i].stop();
                motors[i].setCurrentPosition(motors[i].currentPosition());
            }
            Serial.println("OK");
            break;
        }
        default:
            Serial.println("ERR:Unknown command");
    }
}
```

## Wiring Diagram

See `docs/diagrams/` for hardware wiring schematics.
