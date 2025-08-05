import argparse
import sys,array,ROOT,math,os,copy
import numpy as np
import json

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)


def compute_res(input_file, output_name, input_card, hist_name, hist_abrev, subsystem, layer, radius, plotGauss=True):

    fIn = ROOT.TFile(input_file)
    hist = fIn.Get(hist_name)

    rebin = 1
    hist = hist.Rebin(rebin)

    probabilities = np.array([0.001, 0.999, 0.84, 0.16], dtype='d')


    # compute quantiles
    quantiles = np.array([0.0, 0.0, 0.0, 0.0], dtype='d')
    hist.GetQuantiles(4, quantiles, probabilities)
    xMin, xMax = min([quantiles[0], -quantiles[1]]), max([-quantiles[0], quantiles[1]])
    res_quantile = 0.5*(quantiles[2] - quantiles[3])

    # compute RMS
    rms, rms_err = hist.GetRMS(), hist.GetRMSError()

    # fit with Gauss
    gauss = ROOT.TF1("gauss2", "gaus", xMin, xMax)
    gauss.SetParameter(0, hist.Integral())
    gauss.SetParameter(1, hist.GetMean())
    gauss.SetParameter(2, hist.GetRMS())
    hist.Fit("gauss2", "R")

    mu, sigma = gauss.GetParameter(1), gauss.GetParameter(2)
    sigma_FWHM = 0
    xMin, xMax = mu - 3*sigma, mu + 3*sigma
    sigma_err = gauss.GetParError(2)

    # full width at half length sigma
    def helper_fwhm():
        half_max = 0.5 * gauss.GetMaximum()

        x1, x2 = None, None

        for x in np.linspace(xMin, xMax, 10000):
            y = gauss.Eval(x)

            if y >= half_max:
                # this is the first time we're here so, from left to right, this is the leftmost value (x1)
                if x1 is None: 
                    x1 = x

                # second time -> rightmost
                x2 = x
                
        return abs(x2-x1)

    sigma_FWHM = helper_fwhm()



    gauss.SetLineColor(ROOT.kRed)
    gauss.SetLineWidth(3)


    yMin, yMax = 0, 1.3*hist.GetMaximum()
    canvas = ROOT.TCanvas("canvas", "", 1000, 1000)
    canvas.SetTopMargin(0.055)
    canvas.SetRightMargin(0.05)
    canvas.SetLeftMargin(0.15)
    canvas.SetBottomMargin(0.11)

    dummy = ROOT.TH1D("h", "h", 1, xMin, xMax)
    dummy.GetXaxis().SetTitle(f"{hist_abrev} (um)")
    dummy.GetXaxis().SetRangeUser(xMin, xMax)

    dummy.GetXaxis().SetTitleFont(43)
    dummy.GetXaxis().SetTitleSize(40)
    dummy.GetXaxis().SetLabelFont(43)
    dummy.GetXaxis().SetLabelSize(35)

    dummy.GetXaxis().SetTitleOffset(1.2*dummy.GetXaxis().GetTitleOffset())
    dummy.GetXaxis().SetLabelOffset(1.2*dummy.GetXaxis().GetLabelOffset())

    dummy.GetYaxis().SetTitle("Events / bin")
    dummy.GetYaxis().SetRangeUser(yMin, yMax)
    dummy.SetMaximum(yMax)
    dummy.SetMinimum(yMin)

    dummy.GetYaxis().SetTitleFont(43)
    dummy.GetYaxis().SetTitleSize(40)
    dummy.GetYaxis().SetLabelFont(43)
    dummy.GetYaxis().SetLabelSize(35)

    dummy.GetYaxis().SetTitleOffset(1.7*dummy.GetYaxis().GetTitleOffset())
    dummy.GetYaxis().SetLabelOffset(1.4*dummy.GetYaxis().GetLabelOffset())

    dummy.Draw("HIST")
    hist.Draw("SAME HIST")
    if plotGauss:
        gauss.Draw("SAME")

    canvas.SetGrid()
    ROOT.gPad.SetTickx()
    ROOT.gPad.SetTicky()
    ROOT.gPad.RedrawAxis()

    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextSize(0.035)
    latex.SetTextColor(1)
    latex.SetTextFont(42)
    latex.DrawLatex(0.2, 0.9, f"Mean/RMS = {hist.GetMean():.4f}/{rms:.4f}")
    latex.DrawLatex(0.2, 0.85, f"Resolution = {res_quantile:.4f} %")
    if plotGauss:
        latex.DrawLatex(0.2, 0.80, f"#sigma = {sigma}")
        latex.DrawLatex(0.2, 0.75, f"#sigma_FWHL= {sigma_FWHM}")
        latex.DrawLatex(0.2, 0.70, f"Gauss #mu/#sigma = {mu:.4f}/{sigma:.4f}")

    canvas.SaveAs(f"{output_name}.png")
    canvas.SaveAs(f"{output_name}.pdf")
    canvas.Close()

    del gauss

    data = {}

    data["subsystem"] = subsystem
    data["layer"] = layer
    data["radius"] = radius

    with open(input_card, 'r') as f:
        for line in f:
            line = line.strip()
            if line:  # skip empty lines
                key, value = line.split(' ', 1)
                data[key] = value

    data["rms"] = rms
    data["rms_err"] = rms_err
    data["sigma"] = sigma
    data["sigma_err"] = sigma_err
    data["res_quantile"] = res_quantile
    data["sigma_FWHM"] = sigma_FWHM
    
    # Write it to a JSON file
    with open(f"{output_name}.json", "w") as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, help="Input file", required=True)
    parser.add_argument("-o", "--output", type=str, help="Output file base name", required=True)
    parser.add_argument("-ic", "--inputCard", type=str, help=".input file where gun info is stored", required=True)
    parser.add_argument("-n", "--histName", type=str, help="Histogram to plot", required=True)
    parser.add_argument("-ss", "--subsystem", type=str, help="detector subsystem that the file is from (e.g. VTXIB)", required=True)
    parser.add_argument("-l", "--layer", type=int, help="layer of the detector subsystem", required=True)
    parser.add_argument("-r", "--radius", type=float, help="radius of the specified layer of the detector subsystem", required=True)
    
    #not required
    parser.add_argument("-a", "--histAbreviation", type=str, help="shorter reference to the histogram name")
    
    args = parser.parse_args()

    # if no abreviation provided, use histName
    if args.histAbreviation is None:
        args.histAbreviation = args.histName

    compute_res(
        input_file=args.input, 
        output_name=args.output, 
        input_card=args.inputCard, 
        hist_name=args.histName, 
        hist_abrev=args.histAbreviation,
        subsystem=args.subsystem,
        layer=args.layer,
        radius=args.radius,
        )
