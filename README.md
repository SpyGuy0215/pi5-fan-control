# Pi5 Fan Control

The Pi5 Fan Control library wraps functions to read and control the fan curve of a Raspberry Pi 5 from a Python script. The main method of doing this is through editing the firmware config.txt. 

## Prerequisites
You will need a fan, like the official case fan or the Active Cooler fan, plugged into the fan port on your Pi 5. In addition, you will need some form of `sudo` access on your Pi, as the library requires it in order to access the configuration files. 

## Installation 
This library is available in PyPi. Simply install the library: 
```bash
pip install pi5_fan_control
```

## Getting Started
Example code files can be found under `src/pi5_fancontrol/examples` in the repository. In addition, unit tests for every function of the library can be found in the `tests` folder; read through these to get a comprehensive understanding of what the library can do. Features include:

- Updating the fan curve (requires a reboot to take effect)
- Reading the current fan curve config, if it exists
- Getting the live fan speed and CPU temperature
- Safety checks for bad configs, bad values

## Getting Help
If you need any help with this library, or if you've found an issue, please feel free to open up a new issue in this repository or email me at `shashankprasanna1@gmail.com`. 

If you're feeling up to the task, you can also update the code yourself and submit a pull request. 