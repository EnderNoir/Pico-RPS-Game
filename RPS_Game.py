import network
import socket
from machine import Pin
import time

wifi_name = "name"
wifi_password = "password"

# Game choices
CHOICES = ['Rock', 'Paper', 'Scissors']
WINNING_SCORE = 3

# Player 2: 3 buttons (pins 14, 15, 16), 1 LED (pin 2)
buttons = [Pin(i, Pin.IN, Pin.PULL_UP) for i in range(14, 17)]
led = Pin(2, Pin.OUT)

# Scores
score_p1 = 0
score_p2 = 0
game_over = False

def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(wifi_name, wifi_password)
    while not wlan.isconnected():
        pass
    print("Network connected:", wlan.ifconfig())
    return wlan.ifconfig()[0]

def flicker_led(color, times=3):
    # Flicker LED: green (win) or red (lose)
    # Pico doesn't have color LEDs, so just flicker for win/lose
    for _ in range(times):
        led.on()
        time.sleep(0.2)
        led.off()
        time.sleep(0.2)

def get_player2_choice():
    # Wait for player 2 to press a button
    while True:
        for i, button in enumerate(buttons):
            if button.value() == 0:
                time.sleep(0.2)  # Debounce
                return i
        time.sleep(0.05)

def decide_winner(p1, p2):
    # Returns: 1 if player 1 wins, 2 if player 2 wins, 0 for tie
    if p1 == p2:
        return 0
    if (p1 == 0 and p2 == 2) or (p1 == 1 and p2 == 0) or (p1 == 2 and p2 == 1):
        return 1
    return 2

def webpage(score_p1, score_p2, last_result=None, game_over=False):
    color = "#fff"
    result_text = ""
    game_status_text = ""
    
    if game_over:
        if score_p1 >= WINNING_SCORE:
            result_text = "🎉 GAME OVER - Player 1 WINS! 🎉"
            color = "#8f8"  # Green
        else:
            result_text = "🎉 GAME OVER - Player 2 WINS! 🎉"
            color = "#f88"  # Red
        reset_button = '<a href="/?reset=1"><button class="btn" style="background: #88f;">RESET GAME</button></a>'
    else:
        reset_button = ""
    if last_result == 1:
        color = "#8f8"  # Green
        result_text = "You WON!"
    elif last_result == 2:
        color = "#f88"  # Red
        result_text = "You LOST!"
    elif last_result == 0:
        color = "#ff8"  # Yellow
        result_text = "It's a TIE!"

    buttons_html = ''.join(
        f'<a href="/?choice={i}"><button class="btn" {"disabled" if game_over else ""}>{CHOICES[i]}</button></a>'
        for i in range(3)
    )

    return f"""
    <html>
    <head>
        <title>Rock Paper Scissors - Player 1</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ background: #222; color: #fff; font-family: Arial; text-align: center; }}
            .controller {{ margin: 40px auto; display: inline-block; background: #444; border-radius: 20px; padding: 30px 40px; }}
            .btn {{ background: #333; color: #fff; border: 2px solid #888; border-radius: 10px; font-size: 28px; margin: 10px; padding: 20px 40px; cursor: pointer; }}
            .btn:disabled {{ background: #666; color: #999; cursor: not-allowed; opacity: 0.5; }}
            .score {{ font-size: 24px; margin: 20px; }}
            .result {{ font-size: 32px; margin: 20px; background: {color}; color: #222; border-radius: 10px; padding: 10px 20px; display: inline-block; }}
        </style>
    </head>
    <body>
        <h1>Player 1: Rock Paper Scissors</h1>
        <div class="controller">
            {buttons_html}
        </div>
        <div class="score">
            <b>Player 1 Score:</b> {score_p1} &nbsp;&nbsp; <b>Player 2 Score:</b> {score_p2}
        </div>
        <div class="result">{result_text}</div>
        {reset_button}
        <p>Player 2: Press a physical button to play!</p>
    </body>
    </html>
    """

ip = connect_to_wifi()
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 80))
server.listen(1)

last_result = None

while True:
    client, addr = server.accept()
    print("Connection from:", addr)
    request = client.recv(1024).decode()
    print("Request:", request)

    # Check if reset button was pressed
    if '/?reset=1' in request:
        score_p1 = 0
        score_p2 = 0
        game_over = False
        last_result = None
        print("Game reset!")

    # Check if player 1 made a choice
    choice_idx = None
    for i in range(3):
        if f'/?choice={i}' in request:
            choice_idx = i
            break

    if choice_idx is not None and not game_over:
        # Wait for player 2 to press a button
        p2_choice = get_player2_choice()
        print(f"Player 1: {CHOICES[choice_idx]}, Player 2: {CHOICES[p2_choice]}")
        result = decide_winner(choice_idx, p2_choice)
        last_result = result
        if result == 1:
            score_p1 += 1
            flicker_led('green')
        elif result == 2:
            score_p2 += 1
            flicker_led('red')
        else:
            flicker_led('tie')

        # Check if someone reached winning score
        if score_p1 >= WINNING_SCORE or score_p2 >= WINNING_SCORE:
            game_over = True

    response = webpage(score_p1, score_p2, last_result)
    http_response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n' + response
    client.send(http_response.encode('utf-8'))
    client.close()