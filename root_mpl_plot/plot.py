import datetime
import math
from pathlib import Path
import re

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from scipy.stats import norm
from scipy.optimize import curve_fit

import numpy as np
import ROOT

import atlasify
import yaml
import click

from impl.plotter import Plotter


@click.command()
@click.argument("rootfiles", nargs=-1)
@click.option("--input-config", "-c", help="YAML config file for the plots")
@click.option("--output", "-o", default="plots.pdf", help="Name of the output PDF")
@click.option("--pngs/--no-pngs", default=True, help="Make png files")
def main(rootfiles, input_config, output, pngs):
    if pngs:
        png_path = Path(output).parent / "pngs"
        png_path.mkdir(exist_ok=True, parents=True)

    atlasify.monkeypatch_axis_labels()

    with open(input_config) as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)

    plotter = Plotter()

    with PdfPages(output) as pdf:
        for name, args in config.items():
            fig = plotter.plot_entry(files=rootfiles, name=name, **args)

            fig.tight_layout()
            pdf.savefig(figure=fig)
            if pngs:
                fig.savefig(png_path / f"{name.lower()}.png", dpi=300)

        d = pdf.infodict()
        d["Title"] = "GSF Report"
        d["Author"] = "Benjamin Huth"
        d["CreationDate"] = datetime.datetime.today()
        d["ModDate"] = datetime.datetime.today()


if __name__ == "__main__":
    main()
