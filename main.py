# 3 guirlandes avec des leds pilotables (RGB)

import bt_hal

import time, neopixel, random
import _thread

from boot import np

gouttes_blanches = [
    (255, 255, 255),
    (200, 200, 200),
    (150, 150, 150),
    (100, 100, 100),
    (50, 50, 50),
    (25, 25, 25),
    (0, 0, 0)

]

gouttes_bleues = [
    (255, 255, 255),
    (200, 200, 255),
    (150, 150, 255),
    (100, 100, 255),
    (50, 50, 255),
    (25, 25, 255),
    (0, 0, 255),
    (0, 0, 180),
    (0, 0, 120),
    (0, 0, 60),
    (0, 0, 15),
]

gouttes_violettes = [
    (255, 255, 255),
    (255, 200, 255),
    (255, 150, 255),
    (255, 100, 255),
    (255, 50, 255),
    (255, 25, 255),
    (255, 0, 255),
    (180, 0, 180),
    (120, 0, 120),
    (60, 0, 60),
    (15, 0, 15),
]

gouttes_vertes = [
    (255, 255, 255 ),
    (200, 255, 200),
    (150, 255, 150),
    (100, 255, 100),
    (50, 255, 50),
    (25, 255, 25),
    (0, 255, 0),
    (0, 180, 0),
    (0, 120, 0),
    (0, 60, 0),
    (0, 15, 0),
]

gouttes_rv = [
    (255, 25, 25),
    (200, 50, 25),
    (150, 100, 25),
    (100, 150, 25),
    (50, 200, 25),
    (25, 255, 25),
    (18, 180, 18),
    (12, 120, 12),
    (6, 60, 6),
    (2, 15, 2),
]

couleurs = (
    gouttes_vertes,
    gouttes_violettes,
    gouttes_bleues,
    gouttes_blanches,
    gouttes_rv
)

def rainbow_cycle(np, wait):
    def wheel(pos, div=1):
        if pos < 0 or pos > 255:
            return (0, 0, 0)
        elif pos < 85:
            return ((255 - pos * 3)//div, (pos * 3)//div, 0)
        elif pos < 170:
            pos -= 85
            return (0, (255 - pos * 3)//div, (pos * 3)//div)
        pos -= 170
        return ((pos * 3)//div, 0, (255 - pos * 3)//div)


    # run the cycle
    for j in range(255):
        for i in range(np.n):
            rc_index = (i * 256 // np.n) + j
            np[i] = wheel(rc_index & 255)
        np.write()
        if wait != 0:
            time.sleep_ms(wait)
        
    # fade it out
    for div in range(1, 256, 32):
        for i in range(np.n):
            np[i] = (np[i][0]//div, np[i][1]//div, np[i][2]//div)
        np.write()
        if wait != 0:
            time.sleep_ms(wait)
    

@micropython.native
def pluie_step(np, step, pixels, couleur):    
    pixels[1:] = pixels[0:np.n -1]

    if step < len(couleur):
        pixels[0] = couleur[step]
    else:
        pixels[0] = (0,0,0)

    for j in range(np.n):
        np[j] = pixels[j]

    np.write()


# fade out
def pluie_fade_out(np, pixels, delai):
    while pixels[-1] != (0, 0, 0):
        pixels = [(0,0,0)] + pixels[0:-1]
        
        for j in range(np.n):
            np[j] = pixels[j]

        np.write()
        time.sleep_ms(int(random.random()*delai*2))


@micropython.native
def etoiles(np, couleur):
    for i in range(np.n//10):
        p= int(random.random()*np.n)
        np[p] = couleur[int(random.random()*len(couleur))]

        np.write()

def eteindre(np):
    for j in range(np.n):
        np[j] = (0,0,0)
    np.write()









class BleEcho:
    def __init__(self):
        self.uart = bt_hal.BLEUART(handler=self.on_command)
        self.uart.add_connection_handler(self.on_connection)
        self.is_active = True
        self.lock = _thread.allocate_lock()
        self.lock.acquire()


    def on_connection(self, is_connected: bool = False):
        if is_connected:
            print("Server connected")
        else:
            print("Server Disconnected")
 
    def on_command(self, message: str  =""):
        print("rx: ", message)
        command = message.split(' ')[0]
        option = message.split(' ')[1]
        if command == "set":
            response = option + ":" + "ok"
            if option == "on":
                self.is_active = True
            elif option == "off":
                self.is_active = False
            else: 
               response = option + ":" + "failed"
        elif command == "get":
            if option == "state":
                if self.is_active == True:
                    response = "on:ok"
                else:
                    response = "off:ok"
            else:
                response = "get:invalid"
        else:
            response = "command:invalid"
            
        self.uart.write(response)
        
    def led_thread(self):
        pixels = [[],[],[]]
        for index, sortie in enumerate(np):
            pixels[index] = [(0,0,0) for i in range(sortie.n)]
            
       
        couleur = couleurs[int(random.random()*len(couleurs))]
        for step in range(nombre_leds):
            for index, sortie in enumerate(np):
                pluie_step(sortie, step, pixels[index], couleur)
        
        for index, sortie in enumerate(np):
            pluie_fade_out(sortie, pixels[index], 2)
        
        
        
        for _ in range(4):
            time.sleep_ms(100)
            couleur = couleurs[int(random.random()*len(couleurs))]
            for _ in range(50):
                for index, sortie in enumerate(np):
                    etoiles(sortie, couleur)
                
                for index, sortie in enumerate(np):
                    eteindre(sortie)
        
        for index, sortie in enumerate(np):
            pixels[index] = [(0,0,0) for i in range(sortie.n)]
            
       
        for step in range(nombre_leds):
            pluie_step(np[0], min(step, 5), pixels[0], gouttes_violettes)
            pluie_step(np[1], min(step, 5), pixels[1], gouttes_blanches)
            pluie_step(np[2], min(step, 5), pixels[2], gouttes_rv)
        
        for index, sortie in enumerate(np):
            pluie_fade_out(sortie, pixels[index], 2)
        
        self.lock.release()
        _thread.exit()

    def service(self):
        try:
            while True:
                if self.is_active is False:
                    time.sleep(1)
                    continue
               
                _thread.start_new_thread(self.led_thread, ())
                self.lock.acquire()
                
        except KeyboardInterrupt:
            pass
        finally:
            self.uart.close()



if __name__ == "__main__":
    ble_echo = BleEcho()
    ble_echo.service()
    
    