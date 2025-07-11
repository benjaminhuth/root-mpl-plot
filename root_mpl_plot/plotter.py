import atlasify
import matplotlib

from hist_1d import Hist1DWrapper 


# Make list of colors to use, don't use grey, its for indet
class Plotter:
    def __init__(self):
        colors = matplotlib.colors.TABLEAU_COLORS
        del colors["tab:gray"]
        self.colors = colors.keys()

        self.ax_size=(6,6)

    def plot_entry(self, name, path, histograms, files, options={}):
        # Hardcode to have two columns
        grid = max(1, math.ceil(len(histograms)/2)), min(2, len(histograms))
        figsize = grid[1]*self.ax_size[1], grid[0]*self.ax_size[0]
        fig, axes = plt.subplots(*grid, figsize=figsize)    

        fig.suptitle(name.replace("_", " "))

        loaded = []

        for file_name, color in zip(files, self.colors):
            title = str(Path(file_name).name).replace(".root","").replace("_idpvm","")
            loaded.append((file_name, path, title, color))

        axes = [axes] if len(histograms) == 1 else axes.flatten()
        for hist, ax in zip(histograms, axes):
            for fname, basepath, label, color in loaded:
                rfile = ROOT.TFile.Open(fname)

                rebin_to = None
                if "rebin" in options:
                    rebin_to = options["rebin"]["desired_bins"]

                teff = Hist1DWrapper(rfile.Get(basepath + "/" + hist), rebin_to=rebin_to)
                teff.errorbar(ax, color=color, elinewidth=0.6, markersize=2, label=label, lw=0)
                rfile.Close()

                print(f"Plotted: {fname}, {basepath}, {hist}, bins={teff.nbins}")
                ax.set_title(hist.replace("_", " "))
                
        if "hlines" in options:
            for ax in axes.flatten():
                ax.hlines(options["hlines"], *ax.get_xlim(), color='black', lw=0.6, zorder=-100)

        if "vlines" in options:
            for ax in axes.flatten():
                ax.vlines(options["vlines"], *ax.get_ylim(), color='black', lw=0.6, zorder=-100)

        if "atlasify" in options:
            atlasify_kwargs = dict(atlas="Simulation Internal")
            atlasify_kwargs.update(options["atlasify"])
            for ax in axes:
                atlasify.atlasify(axes=ax, **atlasify_kwargs)
        else:
            for ax in axes.flatten():
                lmin, lmax = ax.get_ylim()
                d = lmax - lmin
                ax.set_ylim(lmin, lmax + d*0.5)
                ax.legend(fontsize=7)

        return fig

