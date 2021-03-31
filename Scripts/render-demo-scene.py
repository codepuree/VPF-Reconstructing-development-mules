"""
Renders a given scene from the start frame to the end frame into the given
output folder.
"""

import argparse
from os import path
import sys

import bpy
import bpycv
import cv2
import numpy as np


def render(output: str):
    result = bpycv.render_data()

    # save result
    # transfer RGB image to opencv's BGR
    cv2.imwrite(output + "_rgb.jpg", result["image"][..., ::-1])

    # save instance map as 16 bit png
    # the value of each pixel represents the inst_id of the object to which the
    # pixel belongs
    cv2.imwrite(output + "_inst.png", np.uint16(result["inst"]))

    # convert depth units from meters to millimeters
    depth_in_mm = result["depth"] * 1000
    cv2.imwrite(output + "_depth.png", np.uint16(depth_in_mm))
    # save as 16bit png

    # visualization inst_rgb_depth for human
    # cv2.imwrite(
    #     path.join(output, name + "_vis(inst_rgb_depth).jpg"),
    #     result.vis()[..., ::-1]
    # )


def main(
    output_path: str, start: int = bpy.context.scene.frame_start,
    end: int = bpy.context.scene.frame_end
):
    for i in range(start, end):
        bpy.context.scene.frame_current = i
        render(path.join(output_path, str(i)))


if __name__ == '__main__':
    argv = sys.argv

    if "--" not in argv:
        argv = []  # as if no args are passed
    else:
        argv = argv[argv.index("--") + 1:]  # get all args after "--"

    # When --help or no args are given, print this help
    USAGE_TEXT = (
        """Renders color, depth and instance images of a given scene from the
        first to the last frame"""
        "  blender --background --python " + __file__ + " -- [options]"
    )

    parser = argparse.ArgumentParser(description=USAGE_TEXT)

    parser.add_argument(
        "-o", "--output", type=str, dest="output_path",
        help="Path to where the rendered images should be stored",
    )

    parser.add_argument(
        "-s", "--start-frame", type=int, default=bpy.context.scene.frame_start,
        dest="start_frame", help="Index of the first frame",
    )

    parser.add_argument(
        "-e", "--end-frame", type=int, default=bpy.context.scene.frame_end,
        dest="end_frame", help="Index of the last frame",
    )

    args = parser.parse_args(argv)  # In this example we won't use the args

    if not argv:
        parser.print_help()
        sys.exit()

    main(args.output_path, start=args.start_frame, end=args.end_frame)
