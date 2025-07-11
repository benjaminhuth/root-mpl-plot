import datetime
import math
from pathlib import Path
import re
           
import matplotlib
import matplotlib.pyplot as plt
import atlasify
import click

from plotter import Plotter

@click.command()
@click.argument('rootfiles', nargs=-1)
@click.option('--path', '-p', help='Path within the ROOT file')
@click.option('--output', '-o', default="plot.png", help='Name of the output file')
def main(rootfiles, path, output):
    atlasify.monkeypatch_axis_labels()
    plotter = Plotter(rescale_config=None)

    path = Path(path)
    config = {
        "path": path.parent,
        "histograms": [path.histograms],
        "options": {},
    }

    fig = plotter.plot_entry(files=rootfiles, name="", **config)
    fig.tight_layout()
    fig.savefig(output, dpi=300)


if __name__ == "__main__":
    main()
