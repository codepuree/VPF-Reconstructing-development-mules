"""
Renders the depth and instance images with a colormap to show the differences
in a presentation.
"""

import argparse
from os import path, listdir

import cv2
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from tqdm import tqdm


def save_plot(output_path: str, file_name: str):
    plt.axis('off')
    plt.savefig(
        path.join(output_path, file_name),
        bbox_inches='tight',
        transparent="True", pad_inches=0
    )


def render_rgb(input_path: str):
    rgb = cv2.imread(input_path, 1)
    rgb = cv2.cvtColor(rgb, cv2.COLOR_BGR2RGB)
    plt.axis('off')
    plt.imshow(rgb)


def render_inst(input_path: str):
    inst = cv2.imread(input_path)
    plt.axis('off')
    plt.imshow(inst[:, :, 1])


def render_depth(input_path: str):
    depth = cv2.imread(input_path)
    depth = depth[:, :, 1]  # - depth[:, :, 1].max() * -1
    plt.axis('off')
    plt.imshow(depth, cmap='inferno_r')


def main(input_path: str, output_path: str, combined: bool = False) -> None:
    if combined:
        input_files = [
            f for f in listdir(input_path)
            if path.isfile(path.join(input_path, f))
            and ('.png' in f or '.jpeg' in f or '.jpg' in f)
        ]
        # deduplicate

        def clean_name(name: str) -> str:
            return name.split('.')[0].replace('_inst', '') \
                .replace('_depth', '').replace('_rgb', '')
        input_files = list(set(map(lambda p: clean_name(p), input_files)))

        for n in tqdm(input_files):
            plt.figure()
            gs1 = gridspec.GridSpec(3, 1)
            gs1.update(wspace=0.0, hspace=0.0)

            plt.subplot(gs1[0])
            render_rgb(path.join(input_path, n + '_rgb.jpg'))

            plt.subplot(gs1[1])
            render_inst(path.join(input_path, n + '_inst.png'))

            plt.subplot(gs1[2])
            render_depth(path.join(input_path, n + '_depth.png'))

            save_plot(output_path, n + '_combined.jpg')
    else:
        for file_name in tqdm(listdir(input_path)):
            if "_depth" in file_name:
                render_depth(path.join(input_path, file_name))
                save_plot(output_path, file_name)
            elif "_inst" in file_name:
                save_plot(output_path, file_name)


if __name__ == '__main__':
    # When --help or no args are given, print this help
    USAGE_TEXT = (
        "Renders the depth and instance images with a colormap to show the "
        "differences in a presentation."
        "  python " + __file__ + " [options]"
    )

    parser = argparse.ArgumentParser(description=USAGE_TEXT)

    parser.add_argument(
        "-i", "--input", type=str, dest="input_path",
        help="Path to where the rendered images can be found",
    )

    parser.add_argument(
        "-o", "--output", type=str, dest="output_path",
        help="Path to where the rendered images should be stored",
    )

    parser.add_argument(
        "-c", "--combined", type=bool, dest="combined", default=False,
        help="Whether a combined image of RGB, instance, depth should be"
        "created",
    )

    args = parser.parse_args()  # in this example we won't use the args

    # if not argv:
    #     parser.print_help()
    #     sys.exit()

    main(args.input_path, args.output_path, combined=args.combined)
