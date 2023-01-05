import numpy as np

# function to calculate the avalible left distance to move 

def getLeftDistance(nav_angles, nav_distance):
    left_indeces = nav_angles > np.deg2rad(33)
    if np.any(left_indeces):
        return np.mean(nav_distance[left_indeces]) / 10
    else:
        return 0

# function to calculate the avalible right distance to move 
def getRightDistance(nav_angles, nav_distance):
    right_indeces = nav_angles < np.deg2rad(-33)
    if np.any(right_indeces):
        return np.mean(nav_distance[right_indeces]) / 10
    else:
        return 0


def decision_step(Rover):

        # There are 4 main modes of operation and two edge cases mode 
        # Go to Edge (go)
        # Stay With Edge (stay)
        # Stop and Turn (stop)
        # stuck and rock (edge cases)

        #begining mode that was traying to reach wall 
        if Rover.mode == "go-rotate":
            print("go-rotate")
            # make the rover turn
            Rover.throttle = 0
            Rover.brake = 0
            Rover.steer = -15
            print(len(Rover.nav_angles))

            # stop turning when the rover is close to a wall and go to it 
            if len(Rover.nav_angles) < 2000:
                Rover.steer = 0
                Rover.mode = "go"
                
                
        # this mode responsabile to make the rover go toward wall        
        elif Rover.mode == "go":
            print("go")
            # go to the wall
            Rover.steer = 0
            Rover.throttle = Rover.throttle_set
            # if the rover is close to a wall go to sop mode
            print(Rover.nav_angles)
            if len(Rover.nav_angles) < Rover.stop_forward:            
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.mode = "stop"
                
         # this mode make the rover to stay moving beside the wall       
        elif Rover.mode == "stay":
            print("Stay With Edge")
            if len(Rover.nav_dists) > 0 and len(Rover.nav_angles) > 0:
                Rover.brake = 0
                Rover.throttle = Rover.throttle_set

                # get the averge distance from right and left the rover 
                left_distance = getLeftDistance(Rover.nav_angles, Rover.nav_dists)
                right_distance = getRightDistance(Rover.nav_angles, Rover.nav_dists)
                
                # here we choose minumum between 1.5 that indicate the minu value sey to be away from wall 
                target_distance = np.min([1.5, (left_distance + right_distance) / 2.0])
                steerDif = left_distance - target_distance 
                print("steer")
                print(steerDif)
            # checking the value of steer diff
                if(steerDif > 0):
                    # here mean that the rover has more space to move at his left because it move away from wall then make him back near wall
                        Rover.steer = np.clip(10*steerDif, -15, 10)
                else:

                    # here mean that the rover id getting close to the wall and doesn"t have enough space to move at left so it steer to right 
                        Rover.steer = np.clip(30*steerDif, -15, 10)
                if len(Rover.nav_angles) < Rover.stop_forward:
                    Rover.brake = Rover.brake_set
                    Rover.throttle = 0
                    Rover.mode = "stop"
            # if rock found and the distace to it is more than 0 also the mean of distances is less than 220 go to rock mood       
            if Rover.rock_found and len(Rover.rock_dists) > 0 and np.mean(Rover.rock_dists) < 220:
                Rover.brake = Rover.brake_set
                Rover.throttle = 0
                Rover.steer = 0
                Rover.prev_mode = Rover.mode
                Rover.mode = "rock"  

            if((Rover.throttle > 0) & (abs(Rover.vel) < 0.09) ):
                if Rover.first_stuck is None:
                   Rover.first_stuck = Rover.total_time
        # once 9 seconds are up go to stuck mode (the rover isn't doing so well)
                elif (Rover.total_time - Rover.first_stuck) > 9.0:
                    Rover.mode = "stuck"

        # this mode is when the rover is in front of wall so it shhould steer till see number of pixels to make him go to the stay mode agan 
        elif Rover.mode == "stop":
            print("stop")
            # stop the Rover
            Rover.throttle = 0
            Rover.brake = Rover.brake_set
            # if the rover is not moving rotate
            if Rover.vel <= 0.2:
                Rover.steer = -30
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

            dist_to_rock = min(Rover.rock_dists) 
            print(Rover.near_sample)
            if (Rover.near_sample==0) or (dist_to_rock>9):

                # Check the extent of navigable terrain
                # If mode is forward, navigable terrain looks good 
                # and velocity is below max, then throttle
                print(Rover.vel)
                if Rover.vel < Rover.max_vel:
                    # Set throttle value to throttle setting
                    Rover.throttle = Rover.throttle_set
                    Rover.steer = np.clip(np.mean(Rover.rock_angles * 180/np.pi),-8,8)
                    Rover.brake = 0
                    print(dist_to_rock)
                    if (dist_to_rock < 12):
                        Rover.throttle = 0
                        Rover.brake = Rover.brake_set
                        Rover.steer = 0

            else: # Else coast
                    print("ana hena")
                    Rover.throttle = 0
                    Rover.brake = brake_set
                    Rover.mode = "stop"
                    
     
                        
     # this mode is when the rover stuck ethis on rock or in narrow place                    
        elif Rover.mode == "stuck":
             print("stuck")
             stuck_time = Rover.total_time - Rover.first_stuck
             
             if (stuck_time%4.0 < 2.0):
               Rover.throttle = 0
               Rover.steer = -10
               Rover.brake = 0 # Try turn leftwards in place
               
             else:
               Rover.throttle = Rover.throttle_set * 2
               Rover.steer = 0
               Rover.brake = 0 #  If able to move now, consider unstuck
               print (Rover.vel)
             if(( Rover.vel > 0.05) & len(Rover.nav_angles) > Rover.go_forward):
                Rover.mode = "stay"
                Rover.first_stuck = None
                

    # if the rover is near a rock and stopped pickup the rock
        if Rover.near_sample and Rover.vel == 0 and not Rover.picking_up:
               Rover.send_pickup = True
               Rover.mode = "stop"
            
      
        return Rover
