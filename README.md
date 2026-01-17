# Pico-RPS-Game

A two-player Rock-Paper-Scissors game running on a Raspberry Pi Pico W with WiFi connectivity. Player 1 plays through a web interface, and Player 2 uses physical buttons.

## Setup Instructions

### WiFi Configuration

Before running the game, you must configure your WiFi credentials:

1. Open `RPS_Game.py`
2. Find these lines at the top of the file:
   ```python
   wifi_name = "name"
   wifi_password = "password"
   ```
3. Replace `"name"` with your WiFi network SSID
4. Replace `"password"` with your WiFi network password
5. Save the file

Example:

```python
wifi_name = "MyHomeNetwork"
wifi_password = "MySecurePassword123"
```

### Hardware Setup - Player 2 Connections

#### Buttons (Input)

Player 2 uses 3 buttons connected to the following GPIO pins:

- **GPIO 14**: Rock button
- **GPIO 15**: Paper button
- **GPIO 16**: Scissors button

Each button should connect between the GPIO pin and GND, with internal pull-up resistors enabled.

#### LED (Output)

- **GPIO 2**: Status LED
  - Flickers on win (Player 1 wins)
  - Flickers on lose (Player 2 loses)
  - Flickers on tie

## How to Play

1. Upload `RPS_Game.py` to your Raspberry Pi Pico W
2. The device connects to WiFi and starts the server
3. **Player 1**: Open a web browser and navigate to the Pico's IP address (displayed in the console)
4. **Player 2**: After Player 1 makes a choice, press one of the three physical buttons:
   - Button on GPIO 14 = Rock
   - Button on GPIO 15 = Paper
   - Button on GPIO 16 = Scissors
5. The LED flickers to indicate the result
6. Scores are displayed on the web page

## Game Rules

- Rock beats Scissors
- Scissors beats Paper
- Paper beats Rock
- Same choice = Tie
