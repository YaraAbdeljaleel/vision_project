import numpy as np
# Rover.mode
# Rover.throttle
# Rover.brake
# Rover.steer
# Rover.nav_angles
# Rover.stop_forward
# Rover.go_forward


def getLeftDistance(nav_angles, nav_distance):
    left_indeces = nav_angles > np.deg2rad(33)
    if np.any(left_indeces):
        return np.mean(nav_distance[left_indeces]) / 10
    else:
        return 0


def getRightDistance(nav_angles, nav_distance):
    right_indeces = nav_angles < np.deg2rad(-33)
    if np.any(right_indeces):
        return np.mean(nav_distance[right_indeces]) / 10
    else:
        return 0


def decision_step(Rover):
    if Rover.nav_angles is not None:
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
            if len(Rover.nav_dists) > 0 and len(Rover.nav_angles) > 0:
                Rover.throttle = Rover.throttle_set
                left_distance = getLeftDistance(Rover.nav_angles, Rover.nav_dists)
                right_distance = getRightDistance(Rover.nav_angles, Rover.nav_dists)
                target_distance = np.min([1.5, (left_distance + right_distance) / 2.0])
                steerDif = left_distance - target_distance 
                print("steer")
                print(steerDif)
                if(steerDif > 0):
                        Rover.steer = np.clip(10*steerDif, -15, 10)
                else:
                        Rover.steer = np.clip(30*steerDif, -15, 10)
                if len(Rover.nav_angles) < Rover.go_forward:
                    Rover.brake = Rover.brake_set
                    Rover.throttle = 0
                    Rover.mode = "stop"
                
        elif Rover.mode == "stop":
            print("stop")
            # stop the Rover
            Rover.throttle = 0
            Rover.brake = Rover.brake_set
            # if the rover is not moving rotate
            if Rover.vel <= 0.2:
                Rover.steer = -20
                Rover.brake = 0
                if len(Rover.nav_angles) > Rover.go_forward:
                    Rover.mode = "stay"
                    Rover.steer = 0
        #if a rock is detected 
        elif Rover.mode == "rock":
            print("Rock")
            print("\n")
            steerterrain=0
            if(Rover.nav_angles .any()):
                steerterrain=np.clip(np.mean(Rover.nav_angles * 180/np.pi),-8,8)
            dist_to_rock = min(Rover.navrock_dists) 
            print(Rover.near_sample)
            if (Rover.near_sample==0) or (dist_to_rock>9):
                # Check the extent of navigable terrain
                # If mode is forward, navigable terrain looks good 
                # and velocity is below max, then throttle 
                if Rover.vel < Rover.max_vel:
                    # Set throttle value to throttle setting
                    Rover.throttle = Rover.throttle_set
                    Rover.brake = 0
                else: # Else coast
                    print("ana hena")
                    Rover.throttle = 0
                    Rover.brake = 1
                    Rover.mode = "stop"
                # Set steering to average angle clipped to the range +/- 15
                
                Rover.steer = np.clip(np.mean(Rover.navrock_angles * 180/np.pi),-15,15) +steerterrain

                
            else: #rock is in position to be picked use brakes to stop to be able to pick it
                    print("el else l tanya")
                    if Rover.vel > 0:
                        Rover.throttle = 0
                        Rover.brake = Rover.brake_set
                        Rover.steer = 0
                        #code for steering angle to move to pick rock and reach initial position
        elif Rover.mode == "stuck":
             print("stuck")
             stuck_time = Rover.total_time - Rover.first_stuck
             
             if (stuck_time%4.0 < 2.0):
               Rover.throttle = 0
               Rover.steer = -15
               Rover.brake = 0 # Try turn leftwards in place
               
             else:
               Rover.throttle = Rover.throttle_set * 2
               Rover.steer =0
               Rover.brake = 0 #  If able to move now, consider unstuck
               
             if( Rover.vel > 0.2):
                Rover.mode = "stay"
                Rover.first_stuck = None
                
        if((Rover.throttle > 0) & (abs(Rover.vel) < 0.09) & (Rover.mode == 'stay')):
                if Rover.first_stuck is None:
                   Rover.first_stuck = Rover.total_time
        # once 9 seconds are up go to stuck mode (the rover isn't doing so well)
                elif (Rover.total_time - Rover.first_stuck) > 9.0:
                    Rover.mode = "stuck"

        if Rover.near_sample and Rover.vel == 0 and not Rover.picking_up:
            print("none")
            Rover.steer = 0
            Rover.brake = 0
            Rover.send_pickup = True
            Rover.mode == 'stuck'
    return Rover
