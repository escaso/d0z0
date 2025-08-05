import math
import ROOT
import os
import array
import json
import argparse

class DataPoint:

    # class variables (shared accross all instances)
    momentum_ranges = [1, 5, 10, 50, 100]
    theta_ranges = [10,20,30,40,50,60,70,80,90]
    markers = [20,21,22,23,33]
    colors = [ROOT.kBlack, ROOT.kRed, ROOT.kBlue, ROOT.kGreen+2, ROOT.kMagenta+1]
    momentum_markers = {mom: (c,m) for mom,c,m in zip(momentum_ranges, colors, markers)}


    def __init__(self, p, theta, param):
        self.p = p
        self.theta = theta
        self.cosTheta = math.cos(math.radians(theta))
        self.param = param
        self.color, self.marker = DataPoint.momentum_markers[p]

    def __str__(self):
        return f"p = {self.p}; theta = {self.theta}; cosTheta = {self.cosTheta}; param: {self.param}"


def plot_detector_resolutions(param_detector_data, plotting_param, path):
    for param_num, param_name in enumerate(["d0", "z0"]):
        for detector, momentum_dict in param_detector_data[param_num].items():
            c = ROOT.TCanvas(f"c_{detector}_{param_name}", f"{param_name} resolution {detector}", 800, 600)
            c.SetLogy()  # Set logarithmic y-axis
            c.SetGrid(0, 0)  # No grid lines
            c.SetTickx(1)
            c.SetTicky(1)

            mg = ROOT.TMultiGraph()
            mg.SetTitle(f"{param_name} resolution vs cos#theta for {detector};cos#theta;{plotting_param} [{param_name}] [#mu m]")

            legend = ROOT.TLegend(0.1, 0.7, 0.3, 0.9)

            for momentum, points in momentum_dict.items():
                x_arr = array.array("d", [pt.cosTheta for pt in points])
                y_arr = array.array("d", [pt.param for pt in points])

                graph = ROOT.TGraph(len(points), x_arr, y_arr)
                graph.SetMarkerColor(points[0].color)
                graph.SetMarkerStyle(points[0].marker)
                graph.SetMarkerSize(1.2)
                graph.SetLineColor(points[0].color)

                mg.Add(graph, "LP")  # Lines + Points
                legend.AddEntry(graph, f"p = {momentum} GeV", "lp")  # Use the actual graph for legend
            
            mg.Draw("A")
            mg.GetXaxis().SetTitle("cos#theta")
            mg.GetYaxis().SetTitle(f"{plotting_param} (#Delta{param_name}) [#mum]")
            legend.Draw()
            c.SaveAs(f"{path}/{param_name}_plots/{detector}_{param_name}_individual.pdf")
            c.SaveAs(f"{path}/{param_name}_plots/{detector}_{param_name}_individual.png")


def plot_detector_comparisons(data, default_detector, detectors, plotting_param, path):

    for param_num, param_name in enumerate(["d0", "z0"]):
        for det in detectors:
            c = ROOT.TCanvas(f"c_{param_name}_{det}_over_{default_detector}", f"{plotting_param} ratio: {det}/{default_detector} - {param_name}", 800, 900)

            # Split canvas into upper and lower pads for main plot and ratio
            pad1 = ROOT.TPad("pad1", "Top pad", 0, 0.33, 1, 1.0)   # Left, Bottom, Right, Top (normalized [0,1])
            pad1.SetLogy()
            pad1.SetBottomMargin(0.02)   # No x-axis label space for upper pad
            pad1.SetTopMargin(0.08)      # Space for title
            pad1.SetGridx()              # Add grid in x
            pad1.Draw()                 # Attach pad to canvas
            pad1.cd()                   # Make pad1 the current drawing pad
            
            # TMultiGraph to hold all points from both detectors
            multigraph = ROOT.TMultiGraph()

            # Add a legend in the upper right corner
            legend = ROOT.TLegend(0.1, 0.5, 0.5, 0.9)  
            # (x1, y1, x2, y2) in normalized pad coordinates
            legend.SetTextSize(0.025)

            ratio_graphs = []

            for momentum, points1 in data[param_num][det].items():

                points2 = data[param_num][default_detector][momentum]

                color = points1[0].color
                contrast_markers = {20: 24, 21: 25, 22: 26, 23: 32, 33: 27}

                # --- Plot detector ---
                x1 = array.array("d", [p.cosTheta for p in points1])
                y1 = array.array("d", [p.param for p in points1])
                g1 = ROOT.TGraph(len(points1), x1, y1)
                g1.SetMarkerColor(color)
                g1.SetMarkerStyle(points1[0].marker)
                g1.SetMarkerSize(1.2)
                g1.SetLineColor(color)
                multigraph.Add(g1, "P")
                legend.AddEntry(g1, f"{momentum} GeV ({det})", "p")

                # --- Plot default_detector ---
                x2 = array.array("d", [p.cosTheta for p in points2])
                y2 = array.array("d", [p.param for p in points2])
                g2 = ROOT.TGraph(len(points2), x2, y2)
                g2.SetMarkerColor(color)
                g2.SetMarkerStyle(contrast_markers[points1[0].marker])
                g2.SetMarkerSize(1.2)
                g2.SetLineColor(color)
                multigraph.Add(g2, "P")
                legend.AddEntry(g2, f"{momentum} GeV ({default_detector})", "p")

                # --- Create ratio graph ---
                ratio_x, ratio_y = [], []
                for p1, p2 in zip(points1, points2):
                    ratio_x.append(p1.cosTheta)
                    ratio_y.append(p1.param / p2.param if p2.param != 0 else 0)

                gr_ratio = ROOT.TGraph(len(ratio_x), array.array("d", ratio_x), array.array("d", ratio_y))
                gr_ratio.SetMarkerColor(DataPoint.momentum_markers[momentum][0])
                gr_ratio.SetMarkerStyle(20)  # Uniform marker for ratio panel
                gr_ratio.SetMarkerSize(1.2)
                gr_ratio.SetLineColor(DataPoint.momentum_markers[momentum][0])
                ratio_graphs.append(gr_ratio)


            # Draw top pad
            multigraph.SetTitle(f"{param_name} resolution: {det} vs {default_detector};cos#theta;{plotting_param} (#Delta{param_name}) [#mum]")
            multigraph.Draw("A")
            multigraph.GetYaxis().SetTitleSize(0.045)
            multigraph.GetYaxis().SetTitleOffset(1.1)
            multigraph.GetXaxis().SetLabelSize(0)
            x_min = multigraph.GetXaxis().GetXmin()
            x_max = multigraph.GetXaxis().GetXmax()
            legend.Draw()

            # Lower pad
            c.cd()
            pad2 = ROOT.TPad("pad2", "pad2", 0, 0.05, 1, 0.33)
            pad2.SetTopMargin(0.01)
            pad2.SetBottomMargin(0.35)
            pad2.SetGridx()
            pad2.Draw()
            pad2.cd()

            # Collect all y-values from ratio graphs
            all_ratio_y = []
            for gr in ratio_graphs:
                y_array = gr.GetY()  # This returns a Python array-like object (double*)
                all_ratio_y.extend([y_array[i] for i in range(gr.GetN())])

            ymin = None
            ymax = None

            if all_ratio_y:
                ymin = min(all_ratio_y)
                ymax = max(all_ratio_y)
                # Add some padding (10% of range)
                padding = 0.1 * (ymax - ymin) if (ymax - ymin) != 0 else 0.1
                ymin -= padding
                ymax += padding

            frame = ROOT.TH1F("frame", "", 1, x_min, x_max)
            frame.SetStats(0)
            frame.SetMinimum(ymin)
            frame.SetMaximum(ymax)

            frame.GetXaxis().SetTitle("cos#theta")
            frame.GetXaxis().SetTitleSize(0.12)
            frame.GetXaxis().SetTitleOffset(1.0)    
            frame.GetXaxis().SetLabelSize(0.10)

            frame.GetYaxis().SetTitle(f"{det} / {default_detector}")
            frame.GetYaxis().SetTitleSize(0.08)
            frame.GetYaxis().SetTitleOffset(0.4)
            frame.GetYaxis().SetLabelSize(0.08)

            frame.Draw()

            line = ROOT.TLine(frame.GetXaxis().GetXmin(), 1, frame.GetXaxis().GetXmax(), 1)
            line.SetLineColor(ROOT.kBlack)     # Black line (or any color you want)
            line.SetLineWidth(1)               # Thin line
            line.SetLineStyle(ROOT.kDashed)   # Dashed line (ROOT.kDashed is dotted/dashed style)
            line.Draw("same")
 
            for gr in ratio_graphs:
                gr.Draw("P SAME")

            # Save the canvas
            c.SaveAs(f"{path}/{param_name}_plots/{param_name}_ratio_{det}_over_{default_detector}.pdf")
            c.SaveAs(f"{path}/{param_name}_plots/{param_name}_ratio_{det}_over_{default_detector}.png")



def gather_data(plotting_param_name, detector_names, default_detector, path):
    data = [{}, {}]
    detectors = detector_names + [default_detector]

    for param_num, param_name in enumerate(["d0", "z0"]):
        data[param_num] = {name: {} for name in detectors}

        for detector in detectors:

            detector_path = os.path.join(path, detector)
            input_dir = os.path.join(detector_path, f"gun_{param_name}_plots")

            for filename in os.listdir(input_dir):
                if filename.endswith(".json"):

                    # Open and load the JSON file
                    with open(os.path.join(input_dir, filename), 'r') as json_file:
                        json_data = json.load(json_file)

                    # ONLY WORKS FOR SINGLE NUMBER RANGE (e.g. 10.0,10.0)
                    theta = float(json_data["theta_range"].split(",")[0])
                    p = int(float(json_data["mom_range"].split(",")[0]))
                    plotting_param = float(json_data[plotting_param_name])

                    if p not in data[param_num][detector]:
                        data[param_num][detector][p] = []
                    
                    data[param_num][detector][p].append(DataPoint(p,theta, plotting_param))

            for momentum, _ in data[param_num][detector].items():
                # order tuples by theta, from smallest theta to largest theta
                # data[param_num][detector][momentum].sort(key=lambda point: point.theta)
                data[param_num][detector][momentum].sort(key=lambda point: point.cosTheta)

            # order momenta from smallest to largest
            data[param_num][detector] = dict(sorted(data[param_num][detector].items()))

    return data

def print_data(data):
    for param_num, param_name in enumerate(["d0", "z0"]):
        print(f"\nParameter: {param_name}")
        for detector, momentum_dict in data[param_num].items():
            print(f"  Detector: {detector}")
            for momentum, point_list in momentum_dict.items():
                print(f"    Momentum: {momentum} GeV")
                for point in point_list:
                    print(f"      {point}")

def print_json_params():
    # only prints the relevant ones
    print()
    print('"rms": root-mean-square width')
    print('"sigma": automatically generated gaussian fit sigma')
    print('"res_quantile": resolution by quantiles')
    print('"sigma_FWHM": full width half maximum sigma')
    print()


if __name__ == "__main__":

    d0z0_path = "/home/submit/escaso/summer2025/d0z0"
    detector_path = os.path.join(d0z0_path, "inside_pipe")

    for p in ["d0_plots", "z0_plots"]:
        os.makedirs(os.path.join(detector_path, p), exist_ok=True)


    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--detectorNames", type=str, nargs="+", help="detectors to plot individually and the ratios of against the default", required=True)
    parser.add_argument("-p", "--parameter", type=str, help="parameter to plot (e.g. sigma, res)", required=True)

    #not required:

    # python plot_ratios.py            ---> args.inputDir == False
    # python plot_ratios.py --inputDir ---> args.inputDir == True
    parser.add_argument("-i", "--inputDir", type=str, default=detector_path, help="Directory where the detector plot folders are")
    parser.add_argument("-dis", "--displayParams", type=int, help="1: ONLY displays the parameters to choose from")
    parser.add_argument("-def", "--defaultDetector", type=str, default="IDEA_base25", help="Detector that every detector will be compared to")

    args = parser.parse_args()

    # the user wants to display the options
    if args.displayParams:
        print_json_params()

    # do one thing or the other
    else:
        data = gather_data(plotting_param_name=args.parameter, detector_names=args.detectorNames, default_detector=args.defaultDetector, path=detector_path)
        print_data(data=data)
        plot_detector_resolutions(param_detector_data=data, plotting_param=args.parameter, path=detector_path)
        plot_detector_comparisons(data=data, default_detector=args.defaultDetector, detectors=args.detectorNames, plotting_param=args.parameter, path=detector_path)