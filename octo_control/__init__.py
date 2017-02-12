# coding=utf-8
from __future__ import absolute_import

from octoprint.events import eventManager, Events
from octoprint.util import RepeatedTimer
from subprocess import Popen, PIPE
import octoprint.plugin
import RPi.GPIO as GPIO 
import flask
import sched
import time
import os

scheduler = sched.scheduler(time.time, time.sleep)

class ControllerGPIO():
    def __init__(self, pinNumber, label, activeLow, enable, autoShutDown,isOutput,timeDelay):
        self.pinNumber = pinNumber
        self.label = label
        self.activeLow = activeLow
        self.enable = enable
        self.autoShutDown = autoShutDown
        self.isOutput = isOutput
        self.timeDelay = timeDelay

    def configureGPIO(self):
        if self.isOutput:
            if self.activeLow:
                GPIO.setup(self.pinNumber, GPIO.OUT, initial=GPIO.HIGH)
            else:
                GPIO.setup(self.pinNumber, GPIO.OUT, initial=GPIO.LOW)
        else:
            GPIO.setup(self.pinNumber, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def write(self,active):
        if self.activeLow:
            active = not active

        GPIO.output(self.pinNumber, active)

class ControllerPlugin(octoprint.plugin.StartupPlugin,
            octoprint.plugin.TemplatePlugin,
            octoprint.plugin.SettingsPlugin,
            octoprint.plugin.AssetPlugin,
            octoprint.plugin.BlueprintPlugin,
            octoprint.plugin.EventHandlerPlugin):

    def startGPIO(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        self.io1 = ControllerGPIO(self._settings.get_int(["io1Pin"]),self._settings.get(["io1Label"]),self._settings.get(["io1ActiveLow"]),
            self._settings.get(["io1Enable"]),self._settings.get(["io1AutoShutDown"]),True,self._settings.get(["io1TimeDelay"]))

        self.io2 = ControllerGPIO(self._settings.get_int(["io2Pin"]),self._settings.get(["io2Label"]),self._settings.get(["io2ActiveLow"]),
            self._settings.get(["io2Enable"]),self._settings.get(["io2AutoShutDown"]),True,self._settings.get(["io2TimeDelay"]))

        self.io3 = ControllerGPIO(self._settings.get_int(["io3Pin"]),self._settings.get(["io3Label"]),self._settings.get(["io3ActiveLow"]),
            self._settings.get(["io3Enable"]),self._settings.get(["io3AutoShutDown"]),True,self._settings.get(["io3TimeDelay"]))

        self.io4 = ControllerGPIO(self._settings.get_int(["io4Pin"]),self._settings.get(["io4Label"]),self._settings.get(["io4ActiveLow"]),
            self._settings.get(["io4Enable"]),self._settings.get(["io4AutoShutDown"]),True,self._settings.get(["io4TimeDelay"]))

        self.io5 = ControllerGPIO(self._settings.get_int(["io5Pin"]),self._settings.get(["io5Label"]),self._settings.get(["io5ActiveLow"]),
            self._settings.get(["io5Enable"]),self._settings.get(["io5AutoShutDown"]),True,self._settings.get(["io5TimeDelay"]))

        self.io6 = ControllerGPIO(self._settings.get_int(["io6Pin"]),self._settings.get(["io6Label"]),self._settings.get(["io6ActiveLow"]),
            self._settings.get(["io6Enable"]),self._settings.get(["io6AutoShutDown"]),True,self._settings.get(["io6TimeDelay"]))

        self.io7 = ControllerGPIO(self._settings.get_int(["io7Pin"]),self._settings.get(["io7Label"]),self._settings.get(["io7ActiveLow"]),
            self._settings.get(["io7Enable"]),self._settings.get(["io7AutoShutDown"]),True,self._settings.get(["io7TimeDelay"]))

        self.io8 = ControllerGPIO(self._settings.get_int(["io8Pin"]),self._settings.get(["io8Label"]),self._settings.get(["io8ActiveLow"]),
            self._settings.get(["io8Enable"]),self._settings.get(["io8AutoShutDown"]),True,self._settings.get(["io8TimeDelay"]))

        self.io1.configureGPIO()
        self.io2.configureGPIO()
        self.io3.configureGPIO()
        self.io4.configureGPIO()
        self.io5.configureGPIO()
        self.io6.configureGPIO()
        self.io7.configureGPIO()
        self.io8.configureGPIO()

    def startTimer(self):
        self._checkTempTimer = RepeatedTimer(10, self.checkEnclosureTemp, None, None, True)
        self._checkTempTimer.start()

    def toFloat(self, value):
        try:
            val = float(value)
            return val
        except:
            self._logger.info("Failed to convert to float")
            return 0

    #~~ StartupPlugin mixin
    def on_after_startup(self):
        self.startTimer()
        self.startGPIO()
    #~~ Blueprintplugin mixin
    @octoprint.plugin.BlueprintPlugin.route("/setIO", methods=["GET"])
    def setIO(self):
        io = flask.request.values["io"]
        value = True if flask.request.values["status"] == "on" else False

        if io == "io1": 
            self.io1.write(value)
        elif io == "io2":
            self.io2.write(value)
        elif io == "io3":
            self.io3.write(value)
        elif io == "io4":
            self.io4.write(value)

        return flask.jsonify(success=True)

    #~~ SettingsPlugin mixin
    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        self.startGPIO()

    def get_settings_defaults(self):
        return dict(
            io1Pin=2,
            io2Pin=3,
            io3Pin=4,
            io4Pin=5,
            io5Pin=6,
            io6Pin=13,
            io7Pin=14,
            io8Pin=19,
            io1Label="IO1",
            io2Label="IO2",
            io3Label="IO3",
            io4Label="IO4",
            io1ActiveLow=True,
            io2ActiveLow=True,
            io3ActiveLow=True,
            io4ActiveLow=True,
            io1Enable=False,
            io2Enable=False,
            io3Enable=False,
            io4Enable=False,
        )
    #~~ TemplatePlugin
    def get_template_configs(self):
        return [dict(type="settings", custom_bindings=False)]

    ##~~ AssetPlugin mixin
    def get_assets(self):
        return dict(
            js=["js/control.js"]
        )

    ##~~ Softwareupdate hook
    def get_update_information(self):
        return dict(
            enclosure=dict(
                displayName="Octo Control",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="cdalio1",
                repo="OctoPrint-Enclosure",
                current=self._plugin_version,

                # update method: pip
                pip="https://github.com/cdalio1/octo_control/archive/{target_version}.zip"
            )
        )

__plugin_name__ = "Octo Control"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = ControllerPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }

