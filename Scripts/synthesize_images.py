"""
Synthesizes RGB, instance and depth images of development mules with the help
of Blender.
"""
import argparse
from datetime import datetime, timezone
from math import pi
from os import path
import random
import sqlite3
import sys
from typing import Dict

import bpy
import bpycv
from cv2 import cv2
import numpy as np


def prepare_database(database_path: str):
    """Prepares the sqlite3 database with a schema (if non-existent) and
    returns a handle to it."""
    con = sqlite3.connect(database_path)

    # Create schema if non-existent

    return con


def get_assets() -> Dict:
    """Gets all the available assets from the current scene.

    Blender scene collection structure:
        Scene Collection/
        ├─ Assets/
        │  ├─ Vehicles/
        │  │  ├─ ...
        │  ├─ Buildings/
        │  │  ├─ ...
        ├─ ...
    """

    buildings = bpy.data.collections["Assets"].children.get("Buildings")
    vehicles = bpy.data.collections["Assets"].children.get("Vehicles")

    return {'Buildings': buildings, 'Vehicles': vehicles}


def random_radius(f: float, t: float):
    """Generates a random number that is between -f to -t and f to t."""
    sign = 1 - (2 * round(random.random()))
    return sign * (random.random() * (t - f) + f)


def prepare_scene(seed: float, db_con: sqlite3.Connection, assets: Dict):
    """Prepares and generates a scene in Blender that could then be
    rendered."""

    random.seed(seed)

    # Clear scene from previous runs or newly create it
    scene = None
    if "Scene" in bpy.data.collections:
        scene = bpy.data.collections["Scene"]
        # Clear all objects
        while scene.objects:
            scene.objects.unlink(scene.objects[0])
    else:
        scene = bpy.data.collections.new(name="Scene")
        bpy.context.scene.collection.children.link(scene)

    # Set "Scene" as active scene where the prepared objects get added
    layer_collection = bpy.context.view_layer.layer_collection \
        .children[scene.name]
    bpy.context.view_layer.active_layer_collection = layer_collection

    # Add ground plane
    # TODO: add option to apply different materials to the ground plane

    # Add vehicle model
    vehicle_name = random.choice(assets["Vehicles"].all_objects.keys())
    bpy.ops.object.collection_instance_add(
        name=vehicle_name, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1),
        drop_x=0, drop_y=0
    )
    vehicle = bpy.context.active_object
    # Note: inst_id can only be set if collection and object name are the same
    vehicle["inst_id"] = 1000

    # Reset material
    vehicle_material = 
    bpy.data.materials.get('Body.001').node_tree.nodes.keys()

    # Set random plain color for vehicle
    # TODO: choose random plain color

    # Generate random material for the vehicle
    # TODO: generate pattern for vehicle material

    # Add house models
    # TODO: choose multiple different house models and place them randomly
    # between 30 - 100m away from the vehicle
    for i in range(random.randrange(5, 10)):
        house_name = random.choice(assets["Buildings"].all_objects.keys())
        bpy.ops.object.collection_instance_add(
            name=house_name, align='WORLD',
            location=(
                random_radius(35, 95),
                random_radius(35, 95),
                0
            ),
            scale=(1, 1, 1),
            drop_x=0, drop_y=0
        )
        house = bpy.context.active_object
        house.rotation_euler = (0, 0, random.random() * 2 * pi)
        house["inst_id"] = 2000 + i

    # Assign camera tracking to the vehicle
    # TODO: assign camera to vehicle
    camera = bpy.data.objects["Camera"]
    # TODO: check if a camera exists, otherwise create new one
    #   bpy.context.blend_data.cameras[0]
    camera.constraints.new(type='TRACK_TO')
    constraint = camera.constraints.active

    constraint.target = vehicle
    constraint.up_axis = 'UP_Y'
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.use_target_z = True

    # find perfect camera position - place in radius of -25 - -5 || 5 - 25
    camera.location = (
        random_radius(10, 25),
        random_radius(10, 25),
        random.randrange(1, 2) * 1.7,
    )


def render():
    # render image, instance annoatation and depth in one line code
    # result["ycb_meta"] is 6d pose GT
    # bpy.context.scene.frame_current = 8
    return bpycv.render_data()


def save(result, name: str, output: str, is_human_visible: bool = False):
    """Prepares and stores the result into the specified directory."""
    # save result
    cv2.imwrite(
        path.join(output, name + "_rgb.jpg"),
        result["image"][..., ::-1]
    )  # transfer RGB image to opencv's BGR

    # save instance map as 16 bit png
    # the value of each pixel represents the inst_id of the object to which
    # the pixel belongs
    cv2.imwrite(
        path.join(output, name + "_inst.png"),
        np.uint16(result["inst"])
    )

    # convert depth units from meters to millimeters
    depth_in_mm = result["depth"] * 1000
    cv2.imwrite(
        path.join(output, name + "_depth.png"),
        np.uint16(depth_in_mm)  # save as 16bit png
    )

    # visualization inst_rgb_depth for human
    if is_human_visible:
        cv2.imwrite(
            path.join(output, name + "_vis(inst_rgb_depth).jpg"),
            result.vis()[..., ::-1]
        )


def main(
        output: str, num: int = None,
        start_seed: int = int(datetime.now(timezone.utc).timestamp()),
        database_path: str = None,
        is_human_visible: bool = False
):
    """Synthesizes images of development mules"""
    if database_path is None:
        database_path = path.join(output, "meta_data.db")

    db = prepare_database(database_path)
    assets = get_assets()

    print(output, num, start_seed, database_path)

    seed = start_seed
    while num is None or seed < start_seed + num:
        print("Render:", seed)
        prepare_scene(seed, db, assets)
        res = render()
        save(res, str(seed), output, is_human_visible=is_human_visible)

        seed += 1


if __name__ == '__main__':
    argv = sys.argv

    if "--" not in argv:
        argv = []  # as if no args are passed
    else:
        argv = argv[argv.index("--") + 1:]  # get all args after "--"

    # When --help or no args are given, print this help
    USAGE_TEXT = (
        "Synthesize images for reconstructing development mules"
        "  blender --background --python " + __file__ + " -- [options]"
    )

    parser = argparse.ArgumentParser(description=USAGE_TEXT)

    parser.add_argument(
        "-r", "--render", dest="render_path", metavar='FILE',
        help="Render an image to the specified path",
    )
    parser.add_argument(
        "-s", "--seed", type=int,
        default=int(datetime.now(timezone.utc).timestamp()),
        dest="seed", help="seed for the random number generator"
    )
    parser.add_argument(
        "-n", "--num", type=int, default=None, dest="number_images",
        help="number of images to produce; default is None therefore images"
        "are generated till the application is terminated."
    )
    parser.add_argument(
        "-o", "--output", type=str, default=path.abspath("."), dest="output",
        help="Path to the directory, where the images should be stored"
    )
    parser.add_argument(
        "--database-path", type=str, default=None, dest="database_path",
        help="Path to where the metadata database should be stored/could be"
        "found"
    )
    parser.add_argument(
        "--human-output", type=str, default=False, dest="is_human_visible",
        help="whether human readable output should be generated"
    )

    args = parser.parse_args(argv)  # In this example we won't use the args

    if not argv:
        parser.print_help()
        sys.exit()

    # if not args.text:
    #     print("Error: --text=\"some string\" argument not given, aborting.")
    #     parser.print_help()
    #     sys.exit()

    main(
        args.output, num=args.number_images, start_seed=args.seed,
        database_path=args.database_path,
        is_human_visible=args.is_human_visible
    )
