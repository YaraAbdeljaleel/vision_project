import numpy as np


def decision_step(Rover):
    # There are three main modes of operation
    # Go to Edge (go)
    # Stay With Edge (stay)
    # Stop and Turn (stop)
    if Rover.mode == "go-rotate":
        print("go-rotate")
        # make the rover turn
        Rover.throttle = 0
        Rover.brake = 0
        Rover.steer = -15
        print(len(Rover.nav_angles))
        # stop turning when the rover is close to a wall
        if len(Rover.nav_angles) < 2000:
            Rover.steer = 0
            Rover.mode = "go"
    elif Rover.mode == "go":
        print("go")
        # go to the wall
        Rover.steer = 0
        Rover.throttle = Rover.throttle_set
        # if the rover is close to a wall go to sop mode
        if len(Rover.nav_angles) < Rover.go_forward:
            Rover.throttle = 0
            Rover.brake = Rover.brake_set
            Rover.mode = "stop"
    elif Rover.mode == "stay":
        print("Stay With Edge")
       
            
    elif Rover.mode == "stop":
        print("stop")
        # stop the Rover
        Rover.throttle = 0
        Rover.brake = Rover.brake_set
        # if the rover is not moving rotate
        if Rover.vel <= 0.2:
            Rover.steer = -15
            Rover.brake = 0
            if len(Rover.nav_angles) > Rover.go_forward:
                Rover.mode = "stay"
                Rover.steer = 0

       
    return Rover
