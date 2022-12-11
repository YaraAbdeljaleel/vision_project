import numpy as np
import cv2




# Identify pixels above the threshold
# Threshold of RGB > 160 does a nice job of identifying ground pixels only
def color_thresh(img, rgb_thresh=(160, 160, 160)):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(img[:, :, 0])
    # Require that each pixel be above all three threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
    above_thresh = (img[:, :, 0] > rgb_thresh[0]) \
                   & (img[:, :, 1] > rgb_thresh[1]) \
                   & (img[:, :, 2] > rgb_thresh[2])
    # Index the array of zeros with the boolean array and set to 1
    color_select[above_thresh] = 1
    # Return the binary image
    return color_select

def obstacle_thresh(img, rgb_thresh=(160, 160, 160)):
    # Create an array of zeros with the same xy size as img, but single channel
    color_select = np.zeros_like(img[:,:,0])
    # Require that each pixel be below all three threshold values in rbg_thresh.
    #   Values below the threshold will now contain a boolean array with TRUE.
    below_thresh = ((img[:,:,0] < rgb_thresh[0]) &
                    (img[:,:,1] < rgb_thresh[1]) &
                    (img[:,:,2] < rgb_thresh[2]))
    # Index the array of zeros with the boolean array and set to 1
    color_select[below_thresh] = 1
    return color_select
def rock_thresh(img):
    not_mountain = color_thresh(img, (100,100,0))
    not_nav = 1 - color_thresh(img, (0,0,70))
    rock = np.zeros(not_nav.shape)
    for idx, i in np.ndenumerate(not_nav):
        rock[idx] = not_nav[idx] and not_mountain[idx]
    return rock
# Define a function to convert from image coords to rover coords
def rover_coords(binary_img):
    # Identify nonzero pixels
    ypos, xpos = binary_img.nonzero()
    # Calculate pixel positions with reference to the rover position being at the
    # center bottom of the image.
    x_pixel = -(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[1] / 2).astype(np.float)
    return x_pixel, y_pixel


# Define a function to convert to radial coords in rover space
def to_polar_coords(x_pixel, y_pixel):
    # Convert (x_pixel, y_pixel) to (distance, angle)
    # in polar coordinates in rover space
    # Calculate distance to each pixel
    dist = np.sqrt(x_pixel ** 2 + y_pixel ** 2)
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
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))  # keep same size as input image

    return warped


# Apply the above functions in succession and update the Rover state accordingly
def perception_step(Rover):
    # Perform perception steps to update Rover()
    # TODO:
    # NOTE: camera image is coming to you in Rover.img
    # 1) Define source and destination points for perspective transform
    image = Rover.img
    dst_size = 5
    bottom_offset = 6
    source = np.float32([[14, 140], [301, 140], [200, 96], [118, 96]])
    destination = np.float32([[image.shape[1] / 2 - dst_size, image.shape[0] - bottom_offset],
                              [image.shape[1] / 2 + dst_size, image.shape[0] - bottom_offset],
                              [image.shape[1] / 2 + dst_size, image.shape[0] - 2 * dst_size - bottom_offset],
                              [image.shape[1] / 2 - dst_size, image.shape[0] - 2 * dst_size - bottom_offset],
                              ])
    thresh = (160, 142, 130)

    # 2) Apply perspective transform
    bird_eye = perspect_transform(Rover.img, source, destination)
    # 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
    navigable_threshhold = color_thresh(bird_eye, thresh)
    obstacles = obstacle_thresh(bird_eye, (105, 88, 78))
    rock_threshhold = rock_thresh(bird_eye)

    # 4) Convert map image pixel values to rover-centric coords
    nav_rov_x, nav_rov_y = rover_coords(navigable_threshhold)
    obs_xpix, obs_ypix = rover_coords(obstacles)
    rock_rov_x, rock_rov_y = rover_coords(rock_threshhold)

    # 5) Convert rover-centric pixel values to world coordinates
    nav_x, nav_y = pix_to_world(nav_rov_x, nav_rov_y, Rover.pos[0], Rover.pos[1], Rover.yaw, Rover.worldmap.shape[0],
                                dst_size * 2)
    obstacles_x, obstacles_y = pix_to_world(obs_xpix, obs_ypix, Rover.pos[0], Rover.pos[1],
                                                        Rover.yaw, Rover.worldmap.shape[0],
                                                        dst_size * 2)
    rock_x, rock_y = pix_to_world(rock_rov_x, rock_rov_y, Rover.pos[0], Rover.pos[1], Rover.yaw, Rover.worldmap.shape[0], dst_size * 2)                                                    


    # 6) Update Rover worldmap (to be displayed on right side of screen)
    # Example: Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
    #          Rover.worldmap[rock_y_world, rock_x_world, 1] += 1
    #          Rover.worldmap[navigable_y_world, navigable_x_world, 2] += 1
    step = 10
    if Rover.roll > 1:
        step = 1
    Rover.worldmap[obstacles_y, obstacles_x, 0] += 1
    Rover.worldmap[nav_y, nav_x, 2] += step
    Rover.worldmap[rock_y, rock_x, 1] += 1

    # 7) Convert rover-centric pixel positions to polar coordinates
    # Update Rover pixel distances and angles
    # Rover.nav_dists = rover_centric_pixel_distances
    # Rover.nav_angles = rover_centric_angles
    Rover.nav_dists, Rover.nav_angles = to_polar_coords(nav_rov_x, nav_rov_y)



      # 8) Update Rover.vision_image (this will be displayed on left side of screen)
      # Example: Rover.vision_image[:,:,0] = obstacle color-thresholded binary image
      #          Rover.vision_image[:,:,1] = rock_sample color-thresholded binary image
      #          Rover.vision_image[:,:,2] = navigable terrain color-thresholded binary image
    Rover.vision_image[:, :, 2] = navigable_threshhold * 255
    Rover.vision_image[:, :, 0] = obstacles * 255
    Rover.vision_image[:,:,1] =  rock_threshhold * 255

    return Rover
