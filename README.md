## This is the Raspberry Pi Submodule for the ASGC Farming Robot. This repository contains the code necessary to run on the Raspberry Pi. The Raspberry Pi in our automated farming system acts as a web server and a communications hub between the STM32 NUCLEO-H755ZI board (sensors, data processing, command logic) and the SKR-MINI-E3 CNC Control Board.

# Raspberry Pi Setup:

### **OS: OctoKlipperPi**

## Required Software (Not bundled w/ OctoKlipperPi):

### **1) pigpio daemon** 
The pigpio daemon is a service that allows direct control over the Raspberry Pi's GPIO pins
```
sudo apt-get install pigpio
```

### **2) pigpio python module**
Python module for accessing pigpio
```
sudo apt-get install python3-pigpio
```

### **2.1) Check Python Version**
The Raspberry Pi data interface requires Python >=3.10
```
python3 --version
```

### **3) Clone the Project's Raspberry Pi Submodule**
```
git clone https://github.com/Mozzle/ASGC_Farming_Robot_RPi.git
```

### **4) Add pigpio daemon to the root crontab**
This change will start the pigpio daemon on startup every time the Raspberry Pi is turned on.

```
sudo crontab -e
```
Navigate to the bottom of the file and add the following line:
```
@reboot              /usr/local/bin/pigpiod
```

### **5) Make the Data Interface Python script run on startup**
Open the raspberry pi config:
```
sudo raspi-config
```

Navigate to 'Boot/Auto-Login', set the console to automatically log in the default pi user. Save and do not reboot yet.

Now edit the bashrc:
```
nano ~/.bashrc
```
Add the following line to the bottom:
```
python3 /full/path/to/ASGC_Farming_Robot_RPi/Data_Intf.py
```

### **6) Reboot and confirm the Data Interface is running properly on startup**