#!/usr/bin/python3

import math
import subprocess

from gi.repository import Gtk


def xrandr(args):
    cmd = ['xrandr'] + args
    return subprocess.check_output(cmd).decode('utf-8')


def get_connected_outputs():
    for line in xrandr([]).splitlines():
        if line.startswith(' '):
            continue
        words = line.split()
        if words[1] == 'connected':
            yield words[0]


def set_brightness_and_gamma(outputs, brightness, gamma):
    args = []
    for output in outputs:
        args += ['--output', output,
                 '--brightness', str(brightness),
                 '--gamma', '{}:{}:{}'.format(gamma[0], gamma[1], gamma[2])]
    print(' '.join(args))
    xrandr(args)


def color_temperature_to_rgb(kelvin):
    """Adapted from tannerhelland.com/4435."""
    temp = kelvin / 100.0;

    if temp <= 66:
        red = 255

        green = temp
        green = 99.4708025861 * math.log(green) - 161.1195681661

        if temp <= 19:
            blue = 0
        else:
            blue = temp-10
            blue = 138.5177312231 * math.log(blue) - 305.0447927307
    else:
        red = temp - 60
        red = 329.698727446 * math.pow(red, -0.1332047592)

        green = temp - 60
        green = 288.1221695283 * math.pow(green, -0.0755148492 )

        blue = 255

    def clamp(val):
        if val < 0:
            return 0
        elif val > 255:
            return 255
        else:
            return val

    return [clamp(red), clamp(green), clamp(blue)]


def temperature_to_gamma(kelvin):
    rgb = color_temperature_to_rgb(kelvin)
    fac = sum(rgb) / 3

    for i in range(3):
        rgb[i] /= (fac)

    return rgb


class MyWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="xrandr-slightly-fewer-tears")
        self.set_default_size(640, -1)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, border_width=10)
        self.add(self.box)

        self.box.add(Gtk.Label('Brightness'))
        self.brightness = self.add_hscale(20, 100)
        self.box.add(Gtk.Label('Temperature (K)'))
        self.temperature = self.add_hscale(1000, 40000)

    def add_hscale(self, min_val, max_val):
        scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, digits=0)
        scale.set_range(min_val, max_val)
        scale.connect('value-changed', lambda _: self.update())
        self.box.add(scale)
        return scale

    def update(self):
        brightness = self.brightness.get_value() / 100.0
        if brightness < 0.2:
            brightness = 0.2

        set_brightness_and_gamma(get_connected_outputs(),
                                 brightness,
                                 temperature_to_gamma(self.temperature.get_value()))


win = MyWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
