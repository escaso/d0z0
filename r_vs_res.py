import ROOT
import os
import array
import json
import argparse

class DataPoint:

    # class variables (shared accross all instances)
    momentum_ranges = [1, 5, 10, 50, 100]
    markers = [20,21,22,23,33]
    colors = [ROOT.kBlack, ROOT.kRed, ROOT.kBlue, ROOT.kGreen+2, ROOT.kMagenta+1]
    momentum_markers = {mom: (c,m) for mom,c,m in zip(momentum_ranges, colors, markers)}


    def __init__(self, p, subsystem, layer, radius, param):
        self.p = p
        self.subsystem = subsystem
        self.layer = layer
        self.radius = radius
        self.param = param
        self.color, self.marker = DataPoint.momentum_markers[p]

    def __str__(self):
        return f"p = {self.p}; subsystem = {self.subsystem}; layer: {self.layer}; radius: {self.radius}; param: {self.param}"


def plot(param_detector_data, default_data, plotting_param, default_detector, input_dir):

    def helper_default_radius(param):
        detector_path = os.path.join(input_dir, default_detector)
        dir = os.path.join(detector_path, f"gun_{param}_plots")

        for filename in os.listdir(dir):
            if filename.endswith(".json"):

                # Open and load the JSON file
                with open(os.path.join(dir, filename), 'r') as json_file:
                    json_data = json.load(json_file)

                return float(json_data["radius"])
            
            
    for param_num, param_name in enumerate(["d0", "z0"]):
        for theta, momentum_dict in param_detector_data[param_num].items():
            c = ROOT.TCanvas(f"c_{theta}_{param_name}", f"{param_name} resolution {theta}", 800, 600)
            # c.SetLogy()  # Set logarithmic y-axis
            c.SetGrid(0, 0)  # No grid lines
            c.SetTickx(1)
            c.SetTicky(1)

            mg = ROOT.TMultiGraph()
            mg.SetTitle(f"{param_name} resolution vs radius for theta {theta} [deg];radius [mm];{plotting_param} [{param_name}] [#mu m]")

            legend = ROOT.TLegend(0.1, 0.7, 0.3, 0.9)

            for momentum, points in momentum_dict.items():

                reference_point = default_data[param_num][theta][momentum][0] #only one value

                x_arr = array.array("d", [pt.radius for pt in points])
                y_arr = array.array("d", [((pt.param - reference_point.param)/reference_point.param)*100 for pt in points])

                graph = ROOT.TGraph(len(points), x_arr, y_arr)
                graph.SetMarkerColor(points[0].color)
                graph.SetMarkerStyle(points[0].marker)
                graph.SetMarkerSize(1.2)
                graph.SetLineColor(points[0].color)

                mg.Add(graph, "LP")  # Lines + Points
                legend.AddEntry(graph, f"p = {momentum} GeV", "lp")  # Use the actual graph for legend
            
            mg.Draw("A")
            mg.GetXaxis().SetTitle("VTXIB layer 1 radius [mm]")
            mg.GetYaxis().SetTitle(f"{plotting_param} (#frac{{(#Delta {param_name} - #Delta {param_name}_ref)}}{{#Delta {param_name}_ref}} #times 100) [%]")
            legend.Draw()


            line = ROOT.TLine(mg.GetXaxis().GetXmin(), 0, mg.GetXaxis().GetXmax(), 0)
            line.SetLineColor(ROOT.kBlack)     # Black line (or any color you want)
            line.SetLineWidth(1)               # Thin line
            line.SetLineStyle(ROOT.kDashed)   # Dashed line (ROOT.kDashed is dotted/dashed style)
            line.Draw("same")


            default_radius = helper_default_radius(param_name)

            # Draw arrow at default_radius
            arrow_y_min = mg.GetYaxis().GetXmin()
            arrow = ROOT.TArrow(float(default_radius), arrow_y_min * 0.1, float(default_radius), arrow_y_min, 0.02, "|>")
            arrow.SetLineColor(ROOT.kRed + 2)
            arrow.SetFillColor(ROOT.kRed + 2)
            arrow.SetLineWidth(2)
            arrow.Draw()

            

            c.SaveAs(f"{input_dir}/{param_name}_plots/{param_name}_theta_{theta}_vs_res.pdf")
            c.SaveAs(f"{input_dir}/{param_name}_plots/{param_name}_theta_{theta}_vs_res.png")


def gather_data(plotting_param_name, detector_names, default_detector, input_dir):
    data = [{}, {}]
    default_data = [{}, {}]
    detectors = detector_names + [default_detector]

    for param_num, param_name in enumerate(["d0", "z0"]):
        for detector in detectors:

            detector_path = os.path.join(input_dir, detector)
            dir = os.path.join(detector_path, f"gun_{param_name}_plots")

            for filename in os.listdir(dir):
                if filename.endswith(".json"):

                    # Open and load the JSON file
                    with open(os.path.join(dir, filename), 'r') as json_file:
                        json_data = json.load(json_file)

                    # ONLY WORKS FOR SINGLE NUMBER RANGE (e.g. 10.0,10.0)
                    theta = float(json_data["theta_range"].split(",")[0])
                    p = int(float(json_data["mom_range"].split(",")[0]))
                    subsystem = json_data["subsystem"]
                    layer = int(json_data["layer"])
                    radius = float(json_data["radius"])
                    plotting_param = float(json_data[plotting_param_name])
                        
                    point = DataPoint(p, subsystem, layer, radius, plotting_param)

                    if theta not in data[param_num]:
                        data[param_num][theta] = {}

                    if p not in data[param_num][theta]:
                        data[param_num][theta][p] = []

                    data[param_num][theta][p].append(point)

                    if detector == default_detector:
                        if theta not in default_data[param_num]:
                            default_data[param_num][theta] = {}

                        if p not in default_data[param_num][theta]:
                            default_data[param_num][theta][p] = []

                        default_data[param_num][theta][p].append(point)


            # Now that all files for this param_name are read, sort everything
            for theta in data[param_num]:
                for momentum in data[param_num][theta]:
                    data[param_num][theta][momentum].sort(key=lambda point: point.radius)
                data[param_num][theta] = dict(sorted(data[param_num][theta].items()))

            if detector == default_detector:
                for theta in default_data[param_num]:
                    # no need to loop over momentums to sort by radius because only one radius here
                    default_data[param_num][theta] = dict(sorted(default_data[param_num][theta].items()))

    return data, default_data

def print_data(data):
    for param_num, param_name in enumerate(["d0", "z0"]):
        print(f"\nParameter: {param_name}")
        for theta in sorted(data[param_num].keys()):
            print(f"  Theta: {theta} rad")
            for momentum in sorted(data[param_num][theta].keys()):
                print(f"    Momentum: {momentum} GeV")
                for point in data[param_num][theta][momentum]:
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

    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--detectorNames", type=str, nargs="+", help="detectors to plot individually and the ratios of against the default", required=True)
    parser.add_argument("-p", "--parameter", type=str, help="parameter to plot (e.g. sigma, res)", required=True)

    #not required:

    # python plot_ratios.py            ---> args.inputDir == False
    # python plot_ratios.py --inputDir ---> args.inputDir == True
    parser.add_argument("-i", "--inputDir", type=str, default=f"{d0z0_path}/VTXIB_r1", help="Directory where the detector plot folders are")
    parser.add_argument("-dis", "--displayParams", type=int, help="1: ONLY displays the parameters to choose from")
    parser.add_argument("-def", "--defaultDetector", type=str, default="IDEA_base25", help="Detector that every detector will be compared to")

    args = parser.parse_args()

    # the user wants to display the options
    if args.displayParams:
        print_json_params()

    # do one thing or the other
    else:
        data, default_data = gather_data(
            plotting_param_name=args.parameter,
            detector_names=args.detectorNames, 
            default_detector=args.defaultDetector, 
            input_dir=args.inputDir
        )

        print_data(data=data)
        print_data(data=default_data)

        
        plot(
            param_detector_data=data, 
            default_data=default_data,
            plotting_param=args.parameter,
            input_dir=args.inputDir, 
            default_detector=args.defaultDetector
        )
