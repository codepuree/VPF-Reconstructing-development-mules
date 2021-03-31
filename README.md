# Reconstructing Development Mules

This project tries to synthesize color and depth images with Blender that have a similarity with pictures of development mules.
Therefore, a process gets defined and implemented in Python with the Blender Python API.
Additionally, the generated images get tested on conventional approaches such like Agisoft's Metashape and Meshroom implement it, as well as on SGDepth, a deep monocular approach.

> **Note:** A more detailed writeup can be found in the [Report](./Reconstructing_Development_Mules.pdf).

## Repository Structure

```
./VPF-Reconstructing-development-mules/
├── Blends
│   ├── default-synthesis.blend
│   └── demo-scene.blend
├── Dockerfiles
│   ├── Dockerfile.highres
│   └── Dockerfile.sgdepth
├── README.md
├── Reconstructing_Development_Mules.pdf
└── Scripts
    ├── plot_depth_instace_for_presentation.py
    ├── render-demo-scene.py
    └── synthesize_images.py
```

## Executing the provided scripts

### `synthesize_images.py`

All scripts that are using the `bpy` package have to be run with Blender, as the following code snippet shows.

```bash
blender Blends/default-synthesis.blend -b -P Scripts/synthesize_images -- -o Renders/default-scene/ -n 500
```

> **Note:** You may have to install the additional packages (numpy, bpycv) into the Blender Python environment.
> `pip install --target /opt/blender-2.93.0-fc08fe82ae5d-linux64/2.93/python/lib/python3.9 numpy bpycv`

### `render-demo-scene.py

```bash
blender Blends/demo-scene.blend -b -P render-demo-scene.py -- -o Renders/demo-scene/
```

### `plot_depth_instance_for_presentation.py`

```bash
python Scripts/plot_depth_instance_for_presentation.py -i Renders/demo-scene/ -o Renders/demo-scene/presentation/ --combined True
```

## Contributing

If find a bug, have or problem or just want to ask some questions, then feel free to open an issue.
