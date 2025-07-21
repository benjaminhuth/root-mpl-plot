from pathlib import Path
import math
import textwrap

import ROOT
import atlasify
import matplotlib
import matplotlib.pyplot as plt

from .hist_1d import Hist1DWrapper


# Make list of colors to use, don't use grey, its for indet
class Plotter:
    def __init__(self):
        colors = matplotlib.colors.TABLEAU_COLORS
        del colors["tab:gray"]
        self.colors = colors.keys()
        self.lw = 1.0

        self.ax_size = (6, 6)

    def plot_entry(self, name, histograms, files, options={}):
        # Hardcode to have two columns
        grid = max(1, math.ceil(len(histograms) / 2)), min(2, len(histograms))
        figsize = grid[1] * self.ax_size[1], grid[0] * self.ax_size[0]
        fig, axes = plt.subplots(*grid, figsize=figsize)

        fig.suptitle(name.replace("_", " "))

        base_path = Path(options["base_path"] if "base_path" in options else "")

        loaded = []
        for file_name, color in zip(files, self.colors):
            title = str(Path(file_name).name).replace(".root", "")
            loaded.append((file_name, title, color))

        axes = [axes] if len(histograms) == 1 else axes.flatten()
        for hist, ax in zip(histograms, axes):
            for fname, label, color in loaded:
                print(f"Load {fname}, {hist}", flush=True)
                rfile = ROOT.TFile.Open(fname)

                rebin_to = (
                    options["rebin"]["desired_bins"] if "rebin" in options else None
                )

                if "label_replace" in options:
                    print(label)
                    label = label.replace(*options["label_replace"])
                    print(label)

                teff = Hist1DWrapper(
                    rfile.Get(str(base_path / hist)), rebin_to=rebin_to
                )
                teff.errorbar(
                    ax, color=color, elinewidth=self.lw, markersize=2, label=label, lw=0
                )
                rfile.Close()

                print(f"Plotted: {fname}, {hist}, bins={teff.nbins}")
                ax.set_title("\n".join(textwrap.wrap(hist, 60)))

        for ax in axes.flatten():
            if "xlim" in options:
                ax.set_xlim(*options["xlim"])

            if "ylim" in options:
                ax.set_ylim(*options["ylim"])

            if "hlines" in options:
                ax.hlines(
                    options["hlines"],
                    *ax.get_xlim(),
                    color="black",
                    lw=self.lw,
                    zorder=-100,
                )

            if "vlines" in options:
                ax.vlines(
                    options["vlines"],
                    *ax.get_ylim(),
                    color="black",
                    lw=self.lw,
                    zorder=-100,
                )

            if "atlasify" in options:
                atlasify_kwargs = dict(atlas="Simulation Internal")
                atlasify_kwargs.update(options["atlasify"])

                ax.legend(loc="lower right")
                atlasify.atlasify(axes=ax, **atlasify_kwargs)
                atlasify.atlasify_legend(axes=ax)
            else:
                lmin, lmax = ax.get_ylim()
                d = lmax - lmin
                ax.set_ylim(lmin, lmax + d * 0.5)
                ax.legend(fontsize=7)

        return fig
