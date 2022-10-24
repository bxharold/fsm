#!/usr/bin/python3
"""
pi@mc21a:~/py/fsm.py  2/5/2022   
4-state FSM with button transition and LEDs indicating state.

Controller calls a state process which does its thing (turn on LEDs)
including polling to see if there was a state-change input.
State returns the reason it returned to the controller, 
and the controller does a simple lookup to determine the next state.
"if curState=X and input=Y, then nextState = Z."
Polling is done by checking a global vbl (msg). If it's been set
(in this version, by the button handler) then return to the controller.

                (start) <-------- (Blue) Snap
                  |       Long      ^|
                  |                 ||
                  |Short            ||Sh (will be null)
                  |               Sh||
                  v        Sh       |v
          Warm (Yellow) --------> (Red) Ready

see pirfsm.py for different state machine and PIR handling  

                (start) <-------- (Blue) Snap
                (~yellow)   Long*   |^          
                  |                 ||
                  |Short            ||Sh(will be motion detected)
                  |             auto||
                  v        Sh       |v
          Warm (Yellow) --------> (Red) Ready

    *Long from any state goes to start
"""

import time
from signal import pause
from gpiozero import LED, Button
ledb = LED(13)
ledy = LED(19)
ledr = LED(26)
button = Button(6)
shortPressTime, longPressTime, curState = 0.1, 1.2, "start"  # globals

states = ['start','warm','ready','snap']
messages = ['shortPress', 'longPress','null']

def setLED(ryb):
    ledr.on() if ryb[0]=="R" else ledr.off()
    ledy.on() if ryb[1]=="Y" else ledy.off()
    ledb.on() if ryb[2]=="B" else ledb.off()
        
def flashLED(ryb, ontime, offtime):
    setLED(ryb)
    time.sleep(ontime)
    setLED("ryb")
    time.sleep(offtime)
    
msg = ""  # incoming message from BGH
cur = ""  
def startState():
    global msg
    cur = "start"
    setLED("ryb")
    print(f"in {cur}, incoming={msg}")
    msg = ""
    while True:
        flashLED("rYb", 0.2, 0.0)
        if msg != "":
            print(f"{cur} got a message: {msg}")
            return [cur,msg]
        else:
            print(" s", end="")

def warmState():
    global msg
    cur = "warm"
    setLED("rYb")
    print(f"in {cur}, incoming={msg}")
    msg = "null"
    for i in range(6):
        flashLED("rYb", 0.35, 0.15)
    return[cur,msg]

def readyState():
    global msg
    cur = "ready"
    setLED("Ryb")
    print(f"in {cur}, incoming={msg}")
    msg = ""
    while True:
        time.sleep(0.3)
        if msg != "":
            print(f"{cur} got a message: {msg}")
            return [cur,msg]
        else:
            print(" r", end="")

def snapState():
    global msg
    cur = "snap"
    setLED("ryB")
    print(f"in {cur}, incoming={msg}")
    msg = "null"
    for i in range(5):
        flashLED("ryB", 0.15, 0.15)
    return[cur,msg]

b_t0, b_tf, b_downtime, msg = 0.0,0.0,0.0, "incoming message"
def buttonPressStart():
    global b_t0
    b_t0 = time.time()
    #print(f'Button was pressed at {(b_t0%1000):.2f}')

def buttonReleased():
    global b_t0, msg
    b_tf = time.time()
    b_downtime = b_tf - b_t0
    b_t0, b_tf = 0,0
    if b_downtime > longPressTime:     msg = 'longPress'
    elif b_downtime > shortPressTime:  msg = 'shortPress'
    else:                              msg = 'noPress'          
    print(msg)
    
button.when_pressed = buttonPressStart
button.when_released = buttonReleased

def jump(tpl):
    curState,message = tpl
    print (f"\njump from {curState}, message={message}")
    if   [curState, message] == ['start','START']:       tpl = startState()
    elif [curState, message] == ['start','shortPress']:  tpl = warmState()
    elif [curState, message] == ['start','longPress']:   tpl = startState()
    elif [curState, message] == ['warm','null']:         tpl = readyState()
    elif [curState, message] == ['warm','shortPress']:   tpl = startState()
    elif [curState, message] == ['warm','longPress']:    tpl = startState()
    elif [curState, message] == ['ready','shortPress']:  tpl = snapState()
    elif [curState, message] == ['ready','longPress']:   tpl = startState()
    elif [curState, message] == ['snap','null']:         tpl = readyState()
    elif [curState, message] == ['snap','longPress']:    tpl = startState()
    else:
        print(f"Unhandled {tpl} at {(time.time()%1000):.2f}")
        time.sleep(2)
        return ['start','START']
    return tpl  

def main():
    global msg
    setLED("ryb")
    time.sleep(1)
    cur = 'start'
    jump([cur,'START'])
    while True:    
        [cur,msg] = jump([cur,msg])
        
main()

