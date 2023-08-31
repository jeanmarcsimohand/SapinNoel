import neopixel
import machine

sorties_rubans = (4, 16, 17)
#sorties_rubans = (4,)

nombre_leds = 120

machine.freq(240000000)

np = []

for pin in sorties_rubans:
    np.append(neopixel.NeoPixel(machine.Pin(pin), nombre_leds))

for sortie in np:
    sortie.fill((0, 0, 0))
    sortie.write()
