#!/usr/bin/env python3
"""
-r^t * T = Coordinate of project/camera center:
r^t = inverse/transpose of the 3x3 rotation matrix composed from the quaternion
T = translation vector
python3 matrix.py output.csv >out.txt
combined filed parsing and matrix formation
command: python3 matrix.py images.txt camera.txt
parse_data.py will first parse images.txt and redirect to parsed_data.csv
matrix.py will then take the parsed_data.csv and redirect intrinsic and extrinsic
matrix to out_matrix.txt with the following info:
1. camera model
2. resolution
3. 1 intrinsic matrix
4. extrinsic matrix for each image w/ image name
"""

import sys
import csv
import math
import numpy as np
import parse_data

# https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles
def euler_from_quaternion(x, y, z, w):
    """
    Convert a quaternion into euler angles (roll, pitch, yaw)

    Parameters
    ----------
    x, y, z, w : float
        A 4 element array representing the quaternion (x,y,z,w)

    Returns
    -------
    roll: float
        rotation around x in radians (counterclockwise)
    pitch: float
        rotation around y in radians (counterclockwise)
    yaw: float
        rotation around z in radians (counterclockwise)
    """

    # roll (x-axis rotation)
    sinr_cosp = +2.0 * (w * x + y * z)
    cosr_cosp = +1.0 - 2.0 * (x * x + y * y)
    roll_x = math.atan2(sinr_cosp, cosr_cosp)

    # pitch (y-axis rotation)
    sinp = +2.0 * (w * y - z * x)
    sinp = +1.0 if sinp > +1.0 else sinp
    sinp = -1.0 if sinp < -1.0 else sinp
    pitch_y = math.asin(sinp)

    # yaw (x-axis rotation)
    siny_cosp = +2.0 * (w * z + x * y)
    cosy_cosp = +1.0 - 2.0 * (y * y + z * z)
    yaw_z = math.atan2(siny_cosp, cosy_cosp)

    return roll_x, pitch_y, yaw_z  # in radians


# https://www.euclideanspace.com/maths/geometry/rotations/conversions/quaternionToMatrix/index.htm
def quaternion_rotation_matrix(qw, qx, qy, qz) -> np.ndarray:
    # w   x   y   z
    """
    Convert a quaternion into a full three-dimensional rotation matrix.

    Parameters
    ----------
    qw, qx, qy, qz : float
        A 4 element array representing the quaternion (qw,qx,qy,qz)

    Returns
    -------
    rotation_matrix : np.ndarray
        A 3x3 element matrix representing the full 3D rotation matrix.
        This rotation matrix converts a point in the local reference
        frame to a point in the global reference frame.
    """

    # First row of the rotation matrix
    r00 = 1 - 2 * qy**2 - 2 * qz**2
    r01 = 2 * qx * qy - 2 * qz * qw
    r02 = 2 * qx * qz + 2 * qy * qw

    # Second row of the rotation matrix
    r10 = 2 * qx * qy + 2 * qz * qw
    r11 = 1 - 2 * qx**2 - 2 * qz**2
    r12 = 2 * qy * qz - 2 * qx * qw

    # Third row of the rotation matrix
    r20 = 2 * qx * qz - 2 * qy * qw
    r21 = 2 * qy * qz + 2 * qx * qw
    r22 = 1 - 2 * qx**2 - 2 * qy**2

    # 3x3 rotation matrix
    rotation_matrix = np.array([[r00, r01, r02], 
                                [r10, r11, r12], 
                                [r20, r21, r22]])
    # np.set_printoptions(threshold=sys.maxsize)
    return rotation_matrix


def get_extrinsic(fp: str = "parsed_data.csv"):
    # opening input ile
    with open(fp) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        row = next(csv_reader)  # start with second line
        print("EXTRINSIC:")

        for row in csv_reader:
            image_name = str(row[0])

            qw = float(row[1])
            qx = float(row[2])
            qy = float(row[3])
            qz = float(row[4])

            tx = float(row[5])
            ty = float(row[6])
            tz = float(row[7])

            # find extrinsic matrix
            T = np.array([tx, ty, tz])
            r = quaternion_rotation_matrix(qw, qx, qy, qz)  # rotational matrix
            r_t = r.transpose()
            extrinsic = -r_t * T  # projection_centers
            print(image_name)
            print(extrinsic, end="")
            print("\n")


def get_intrinsic(fp: str = "cameras.txt"):
    infile = open(fp, "r")
    lines = infile.readlines()

    for line in lines:
        data = line.split(" ")
        if not data[0].startswith("#"):
            camera = data[1]
            width = data[2]
            height = data[3]

            fx = data[4]
            fy = data[5]
            x0 = data[6]
            y0 = data[7]

    intrinsic = np.array([[fx, 0, x0], [0, fy, y0], [0, 0, 1]])

    print(camera + " => RESOLUTION: (" + width + "," + height + ")\n")
    print("INTRINSIC:")
    print(intrinsic, end="")
    print("\n")


def main():
    # check for input argument
    if len(sys.argv) != 3:
        print("bad arguments: ")
        print("Usage: python3 %s images.txt camera.txt" % sys.argv[0])
        sys.exit(1)

    sys.stdout = open("out_matrix.txt", "w")
    get_intrinsic()
    get_extrinsic()
    sys.stdout.close()


if __name__ == "__main__":
    parse_data.main()
    main()
