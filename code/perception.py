import numpy as np
import matplotlib
import cv2

DEBBUGING_MODE = True

# Threshold using hsv values
def color_thresh(img,  nav_hi=(256,50,256),nav_lo=(0,0,190)):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(img[:, :, 0])

    # To account for unusual matplotlib HSV settings, use this hack(H and S are 0.0-1.0, but V is 0-255 )
    # because we use function in matplotlib that convert float rgb values (in the range [0, 1]), in a numpy array to hsv values.
    nav_hi = (nav_hi[0] / 255.0, nav_hi[1] / 255.0, nav_hi[2])
    nav_lo = (nav_lo[0] / 255.0, nav_lo[1] / 255.0, nav_lo[2])

    # Convert RGB image to HSV (using matplotlib function)
    hsv_img = matplotlib.colors.rgb_to_hsv(img)

    # Apply threshholding (Low and High) for nav channel 
 
    nav = (hsv_img[:, :, 0] >= nav_lo[0]) & (hsv_img[:, :, 0] <= nav_hi[0]) & \
          (hsv_img[:, :, 1] >= nav_lo[1]) & (hsv_img[:, :, 1] <= nav_hi[1]) & \
          (hsv_img[:, :, 2] >= nav_lo[2]) & (hsv_img[:, :, 2] <= nav_hi[2])
    # Index the array of zeros with the boolean array and set to 1
    color_select[nav] = 1
    # Return the binary image
    return color_select

def rock_thresh(img,  rock_hi=(40,256,256),rock_lo=(25,140,120)):

   color_select = np.zeros_like(img[:, :, 0])
   # To account for unusual matplotlib HSV settings, use this hack(H and S are 0.0-1.0, but V is 0-255 )
   # because we use function in matplotlib that convert float rgb values (in the range [0, 1]), in a numpy array to hsv values.
   rock_hi = (rock_hi[0] / 255.0, rock_hi[1] / 255.0, rock_hi[2])
   rock_lo = (rock_lo[0] / 255.0, rock_lo[1] / 255.0, rock_lo[2])

   # Convert RGB image to HSV (using matplotlib function)
   hsv_img = matplotlib.colors.rgb_to_hsv(img)

   rock = (hsv_img[:, :, 0] >= rock_lo[0]) & (hsv_img[:, :, 0] <= rock_hi[0]) & \
          (hsv_img[:, :, 1] >= rock_lo[1]) & (hsv_img[:, :, 1] <= rock_hi[1]) & \
          (hsv_img[:, :, 2] >= rock_lo[2]) & (hsv_img[:, :, 2] <= rock_hi[2])

   color_select[rock] = 1
   return color_select


def obstacle_thresh(img,  obs_hi=(256,256,90),obs_lo=(0,0,0)):
    # Create an array of zeros with the same xy size as img, but single channel
    color_select = np.zeros_like(img[:, :, 0])
    
    # To account for unusual matplotlib HSV settings, use this hack(H and S are 0.0-1.0, but V is 0-255 )
    # because we use function in matplotlib that convert float rgb values (in the range [0, 1]), in a numpy array to hsv values.
    obs_hi = (obs_hi[0] / 255.0, obs_hi[1] / 255.0, obs_hi[2])
    obs_lo = (obs_lo[0] / 255.0, obs_lo[1] / 255.0, obs_lo[2])
    
    # Convert RGB image to HSV (using matplotlib function)
    hsv_img = matplotlib.colors.rgb_to_hsv(img)

    #   Values below the threshold will now contain a boolean array with TRUE.
    # Apply threshholding (Low and High)
    obs = (hsv_img[:, :, 0] >= obs_lo[0]) & (hsv_img[:, :, 0] <= obs_hi[0]) & \
          (hsv_img[:, :, 1] >= obs_lo[1]) & (hsv_img[:, :, 1] <= obs_hi[1]) & \
          (hsv_img[:, :, 2] >= obs_lo[2]) & (hsv_img[:, :, 2] <= obs_hi[2])
    # Don't include  black pixels that not inditified by rover that is obstcales (just non-data from transform)
    obs_nonzero = (img[:, :, 0] != 0) \
                  | (img[:, :, 1] != 0) \
                  | (img[:, :, 2] != 0)
    obs = obs & obs_nonzero
    # Index the array of zeros with the boolean array and set to 1

    color_select[obs] = 1
    return color_select



# Define a function to convert from image coords to rover coords
def rover_coords(binary_img):
    # Identify nonzero pixels
    ypos, xpos = binary_img.nonzero()
    # Calculate pixel positions with reference to the rover position being at the 
    # center bottom of the image.  
    x_pixel = -(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[1]/2 ).astype(np.float)
    return x_pixel, y_pixel


# Define a function to convert to radial coords in rover space
def to_polar_coords(x_pixel, y_pixel):
    # Convert (x_pixel, y_pixel) to (distance, angle) 
    # in polar coordinates in rover space
    # Calculate distance to each pixel
    dist = np.sqrt(x_pixel**2 + y_pixel**2)
    # Calculate angle away from vertical for each pixel
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles

# Define a function to map rover space pixels to world space
def rotate_pix(xpix, ypix, yaw):
    # Convert yaw to radians
    yaw_rad = yaw * np.pi / 180
    xpix_rotated = (xpix * np.cos(yaw_rad)) - (ypix * np.sin(yaw_rad))
                            
    ypix_rotated = (xpix * np.sin(yaw_rad)) + (ypix * np.cos(yaw_rad))
    # Return the result  
    return xpix_rotated, ypix_rotated

def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale): 
    # Apply a scaling and a translation
    xpix_translated = (xpix_rot / scale) + xpos
    ypix_translated = (ypix_rot / scale) + ypos
    # Return the result  
    return xpix_translated, ypix_translated


# Define a function to apply rotation and translation (and clipping)
# Once you define the two functions above this function should work
def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    # Apply rotation
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    # Apply translation
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    # Perform rotation, translation and clipping all at once
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    # Return the result
    return x_pix_world, y_pix_world

# Define a function to perform a perspective transform
def perspect_transform(img, src, dst):
           
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))# keep same size as input image
    
    return warped

# Apply the above functions in succession and update the Rover state accordingly
def perception_step(Rover):
    # Perform perception steps to update Rover()
    # TODO: 
    # NOTE: camera image is coming to you in Rover.img
    # 1) Define source and destination points for perspective transform
    image = Rover.img
    clipping_value=90
    dst_size=5
    bottom_offset = 6
    source = np.float32([[14, 140], [301 ,140],[200, 96], [118, 96]])  
    destination = np.float32([[image.shape[1]/2 - dst_size, image.shape[0] - bottom_offset],
                  [image.shape[1]/2 + dst_size, image.shape[0] - bottom_offset],
                  [image.shape[1]/2 + dst_size, image.shape[0] - 2*dst_size - bottom_offset], 
                  [image.shape[1]/2 - dst_size, image.shape[0] - 2*dst_size - bottom_offset],
                  ])



    nav_hi = (256, 50, 256)
    nav_lo = (0, 0, 190)
    intentional_black = False
    if Rover.pitch > 1:
        intentional_black = True
        nav_hi= (255, 255, 255)
        nav_lo = (255, 255, 255)
    
    
    # 2) Apply perspective transform
    bird_eye = perspect_transform(image, source, destination)
    bird_eye[0:100, :, :] = np.zeros_like(bird_eye[0:100, :, :].shape)
    # 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
    navigable_threshhold = color_thresh(bird_eye,nav_hi,nav_lo)
    rock_threshhold = rock_thresh(bird_eye)
    obstacles = obstacle_thresh(bird_eye)


    # 4) Convert map image pixel values to rover-centric coords
    nav_rov_x, nav_rov_y = rover_coords(navigable_threshhold)
    rock_rov_x, rock_rov_y = rover_coords(rock_threshhold)
    obs_xpix, obs_ypix = rover_coords(obstacles)
    # 5) Convert rover-centric pixel values to world coordinates
    nav_x, nav_y = pix_to_world(nav_rov_x, nav_rov_y, Rover.pos[0], Rover.pos[1], Rover.yaw, Rover.worldmap.shape[0], dst_size * 2)
    rock_x, rock_y = pix_to_world(rock_rov_x, rock_rov_y, Rover.pos[0], Rover.pos[1], Rover.yaw, Rover.worldmap.shape[0], dst_size * 2)
    obstacles_x, obstacles_y = pix_to_world(obs_xpix, obs_ypix, Rover.pos[0], Rover.pos[1], Rover.yaw, Rover.worldmap.shape[0], dst_size * 2)
    # 6) Update Rover worldmap (to be displayed on right side of screen)
        # Example: Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
        #          Rover.worldmap[rock_y_world, rock_x_world, 1] += 1
        #          Rover.worldmap[navigable_y_world, navigable_x_world, 2] += 1
    step = 10
    if Rover.roll > 1:
        step = 1
    Rover.worldmap[nav_y, nav_x, 2] += step
    Rover.worldmap[rock_y, rock_x, 1] += 1
    Rover.worldmap[obstacles_y, obstacles_x, 0] += 1
    # 7) Convert rover-centric pixel positions to polar coordinates
    # Update Rover pixel distances and angles
        # Rover.nav_dists = rover_centric_pixel_distances
        # Rover.nav_angles = rover_centric_angles
    Rover.nav_dists, Rover.nav_angles = to_polar_coords(nav_rov_x, nav_rov_y)
    if intentional_black:
        Rover.nav_angles = Rover.last_thetas

    # 8) Update both bird eye and n1(navigable_terrain) images which are both need to be translated and scaled 
    if DEBBUGING_MODE:
        var1 = int(Rover.vision_image.shape[0]/2)
        var2 = int(Rover.vision_image.shape[1]/2)
        
        dim = (var2,var1)
        bird_eye1 = cv2.resize(bird_eye,dim, cv2.INTER_CUBIC)
        n1= cv2.resize(navigable_threshhold,dim, cv2.INTER_CUBIC)
        r1= cv2.resize(rock_threshhold,dim, cv2.INTER_CUBIC)
        o1= cv2.resize(obstacles,dim, cv2.INTER_CUBIC)
        rov_img = np.zeros((321, 161 , 3))
        for idx, i in np.ndenumerate(nav_rov_x):
            x = int(160 - nav_rov_y[idx])
            y = int(nav_rov_x[idx])
            rov_img[x, y, :] = [255,255,255]
    # 9) Define a square which show the mean direction of the rover also scaled and translated
        if Rover.nav_angles is not None and len(Rover.nav_angles) > 0:
            mean_dir = np.mean(Rover.nav_angles)
            mean_x = 50 * np.cos(mean_dir)
            mean_y = 50 * np.sin(mean_dir)
            mean_x_img = int(160 - mean_y)
            mean_y_img = int(mean_x)
            for i in range(20):
                for j in range(20):
                    rov_img[mean_x_img + i, mean_y_img + j, :] = [255,0,0]
        rov_img_resized = cv2.resize(rov_img,(80, 160), cv2.INTER_CUBIC)
        Rover.vision_image[0:var1,0:var2, :] =  bird_eye1 
        Rover.vision_image[var1:Rover.vision_image.shape[0],0:var2,2] =  n1 * 255
        Rover.vision_image[var1:Rover.vision_image.shape[0],0:var2,1] =  r1 * 255
        Rover.vision_image[var1:Rover.vision_image.shape[0],0:var2,0] =  o1 * 255
        Rover.vision_image[:, var2:var2+80, :] = rov_img_resized
    else:
    # 10) Update Rover.vision_image (this will be displayed on left side of screen)
        # Example: Rover.vision_image[:,:,0] = obstacle color-thresholded binary image
        #          Rover.vision_image[:,:,1] = rock_sample color-thresholded binary image
        #          Rover.vision_image[:,:,2] = navigable terrain color-thresholded binary image
        Rover.vision_image[:,:,2] =  navigable_threshhold * 255
        Rover.vision_image[:,:,1] =  rock_threshhold * 255
        Rover.vision_image[:, :, 0] = obstacles * 255
    return Rover
