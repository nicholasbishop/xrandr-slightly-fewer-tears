#!/usr/bin/python3

# Licensed under the GNU GPLv3+

import math
import os
import subprocess

import gi
gi.require_version('Gtk', '3.0')
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
    temp = kelvin / 100.0
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
        green = 288.1221695283 * math.pow(green, -0.0755148492)

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
    def __init__(self, conf):
        Gtk.Window.__init__(self, title="xrandr-slightly-fewer-tears")
        self.set_default_size(640, -1)

        self.conf = conf

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, border_width=10)
        self.add(self.box)

        self.brightness_checkbutton = self.add_checkbutton(
            'Brightness', conf.brightness_enabled)
        self.brightness = self.add_hscale(20, 100, conf.brightness)

        self.temperature_checkbutton = self.add_checkbutton(
            'Temperature (K)', conf.temperature_enabled)
        self.temperature = self.add_hscale(2000, 10000, conf.temperature)

        # Update immediately so that saved values are loaded on startup
        self.update()

    def add_checkbutton(self, label, default):
        btn = Gtk.CheckButton(label)
        btn.set_active(default)
        btn.connect('toggled', lambda _: self.update())
        self.box.add(btn)
        return btn

    def add_hscale(self, min_val, max_val, def_val):
        scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, digits=0)
        scale.set_range(min_val, max_val)
        scale.set_value(def_val)
        scale.connect('value-changed', lambda _: self.update())
        self.box.add(scale)
        return scale

    def save_conf(self):
        self.conf.brightness_enabled = self.brightness_checkbutton.get_active()
        self.conf.temperature_enabled = self.temperature_checkbutton.get_active()
        self.conf.brightness = self.brightness.get_value()
        self.conf.temperature = self.temperature.get_value()
        self.conf.save()

    def update(self):
        if self.brightness_checkbutton.get_active():
            brightness = self.brightness.get_value() / 100.0
            if brightness < 0.2:
                brightness = 0.2
        else:
            brightness = 1.0

        if self.temperature_checkbutton.get_active():
            gamma = temperature_to_gamma(self.temperature.get_value())
        else:
            gamma = (1, 1, 1)

        set_brightness_and_gamma(get_connected_outputs(), brightness, gamma)

        self.save_conf()


class Config(object):
    def __init__(self):
        self.pardir = os.path.join(os.getenv('HOME'),
                                   '.config',
                                   'xrandr-slightly-fewer-tears')
        self.path = os.path.join(self.pardir, 'xsft.conf')

        # key:default
        self.items = {
            'brightness': 80.0,
            'brightness_enabled': True,
            'temperature': 5500.0,
            'temperature_enabled': True
        }

        # Set defaults
        for key in self.items:
            setattr(self, key, self.items[key])

        try:
            self.load()
        except IOError:
            pass

    def load(self):
        with open(self.path) as conf_file:
            for line in conf_file.readlines():
                parts = line.split('=')
                key = parts[0]
                val_str = parts[1]

                default = self.items.get(key)
                if default is not None:
                    if isinstance(default, bool):
                        val = bool(val_str)
                    else:
                        val = float(val_str)
                    setattr(self, key, val)

    def save(self):
        if not os.path.isdir(self.pardir):
            os.mkdir(self.pardir)
        with open(self.path, 'w') as conf_file:
            for key in self.items:
                val = getattr(self, key)
                conf_file.write('{}={}\n'.format(key, val))


def main():
    conf = Config()
    win = MyWindow(conf)
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == '__main__':
    main()
