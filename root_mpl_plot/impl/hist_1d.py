import numpy as np


def rebin_factor(bins_desired, bins_current):
    if bins_desired > bins_current:
        raise RuntimeError("Cannot increase number of bins")

    if bins_current % bins_desired != 0:
        raise RuntimeError(f"Cannot rebin {bins_current} to {bins_desired}")

    return bins_current // bins_desired


class Hist1DWrapper:
    def __init__(self, root_hist_1d, rebin_to=None, rescale=None):
        # This should work also for TEfficiency
        try:
            th1 = root_hist_1d.GetTotalHistogram()
            assert rescale is None, "Cannot rescale TEfficiency"

            if rebin_to is not None:
                f = rebin_factor(rebin_to, th1.GetNbinsX())

                if f != 1:
                    totalCpy = root_hist_1d.GetCopyTotalHisto()
                    passedCpy = root_hist_1d.GetCopyPassedHisto()

                    totalCpy.Rebin(f)
                    passedCpy.Rebin(f)

                    root_hist_1d = ROOT.TEfficiency(passedCpy, totalCpy)
                    th1 = root_hist_1d.GetTotalHistogram()

        except:
            th1 = root_hist_1d

            if rebin_to is not None:
                f = rebin_factor(rebin_to, th1.GetNbinsX())
                if f != 1:
                    th1.Rebin(f)

            if rescale is not None:
                th1.Scale(rescale)

        self.nbins = th1.GetNbinsX()

        bins = [i for i in range(th1.GetNbinsX()) if th1.GetBinContent(i) > 0.0]
        bins = bins[1:]

        self.x = [th1.GetBinCenter(i) for i in bins]

        self.x_lo = [th1.GetBinLowEdge(i) for i in bins]
        self.x_width = [th1.GetBinWidth(i) for i in bins]
        self.x_hi = np.add(self.x_lo, self.x_width)
        self.x_err_lo = np.subtract(self.x, self.x_lo)
        self.x_err_hi = np.subtract(self.x_hi, self.x)

        try:
            self.y = [root_hist_1d.GetEfficiency(i) for i in bins]
            self.y_err_lo = [root_hist_1d.GetEfficiencyErrorLow(i) for i in bins]
            self.y_err_hi = [root_hist_1d.GetEfficiencyErrorUp(i) for i in bins]
        except:
            self.y = [root_hist_1d.GetBinContent(i) for i in bins]
            self.y_err_lo = [root_hist_1d.GetBinError(i) for i in bins]
            self.y_err_hi = [root_hist_1d.GetBinError(i) for i in bins]

        self.xlabel = th1.GetXaxis().GetTitle()
        self.ylabel = th1.GetYaxis().GetTitle()

        def latexify(label):
            label = label.replace("#", "\\").replace(" ", "\\:")
            return f"${label}$"

        self.xlabel = latexify(self.xlabel.replace("_", " "))
        self.ylabel = self.ylabel.replace("_", " ")

    def common(self, ax):
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)

    def errorbar(self, ax, **errorbar_kwargs):
        ax.errorbar(
            self.x,
            self.y,
            yerr=(self.y_err_lo, self.y_err_hi),
            xerr=(self.x_err_lo, self.x_err_hi),
            **errorbar_kwargs,
        )
        self.common(ax)
        return ax

    def step(self, ax, **step_kwargs):
        ax.step(self.x_hi, self.y, **step_kwargs)
        self.common(ax)
        return ax

    def bar(self, ax, **bar_kwargs):
        ax.bar(self.x, height=self.y, yerr=(self.y_err_lo, self.y_err_hi), **bar_kwargs)
        self.common(ax)
        return ax
