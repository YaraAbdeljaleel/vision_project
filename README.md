# Computer Vision Project (Mars Rover NASA)
—-
This is a computer vision project senior 1 level done for Ain Shams University Fall 2022,
it is assumed to have the simulator running on linux.
This file aids with setting up an anaconda environment to run the code provided in this repo.

The README shows how to:

   1. set up the conda environment
   2. run the code
   
# Anaconda setup
—-
    1. Install anaconda from this link: https://www.anaconda.com/products/distribution\
   Now you have the base enviroment, clone the base enviroment anything you like ex:(vision).
    2. run conda create --name vision --clone base 
   Now you have the enviroment of conda's default packages
    3. Run conda activate vision
    4. Install the following packeges:
   conda install -c <source> <package-name> to check the conda package source use anaconda.org list of needed packages:

    - opencv
    - python-socketio (version 4.6.1)
    - python-engineio (version 3.13.2)
    - eventlet
# Running the code
—-
open the terminal in the code folder and run the python file drive_rover.py <python3 drive_rover.py>

#Code Logic while running
   
   
   -First we receives a Rover object as input, which contains various variables and parameters related to the rover's current state and environment.
   -It uses a series of if-elif statements to check the rover's mode and the extent of navigable terrain.
   -If the rover is in "forward" mode and there is sufficient navigable terrain, it sets the throttle to a certain value and the steering to the average angle of the         navigable terrain.
   -If there is any rock is located then go to rock mode to start navigate the rock.
   -If there is not sufficient navigable terrain, it switches to "stop" mode and applies the brakes.
   -If the rover is in "stop" mode, it first checks if it is still moving. If it is, it continues braking.
   -If the rover is not moving, it checks if there is sufficient navigable terrain in front of the rover. If there is, it switches back to "forward" mode and sets the       throttle and steering values.
   -If there is not sufficient navigable terrain, it turns in place by setting the steering value to -15 degrees.
   -Then also includes a condition to send a pickup command to the rover if it is near a sample and not already picking one up.
   -Then returns the updated Rover object, with the new throttle, brake, and steering values.
   -Finally uses various parameters and variables stored in the Rover object, such as Rover.nav_angles, Rover.vel, Rover.max_vel, Rover.throttle_set, 
   Rover.brake_set, Rover.stop_forward, Rover.go_forward, and Rover.near_sample. These values influence the behavior of the rover and can be modified to change its          behavior.
   
   #Perception Step Function
   

