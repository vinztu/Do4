from figure_size import set_size
import matplotlib.pyplot as plt
import numpy as np


class PlotParameters:
    
    def __init__(self, latex_width):
        self.latex_width = latex_width
        self.Figure = self.Figure(self)
        
        tex_fonts = {
            "text.usetex": True,
            "font.family": "Computer Modern Roman"
        }
        plt.rcParams.update(tex_fonts)
        plt.style.use('seaborn-v0_8-paper')
        
    class Figure:
        def __init__(self, outer_class):
            self.latex_width = outer_class.latex_width
            self.figsize = set_size(self.latex_width, fraction = 1, subplots = (1,1))
            
        colors = plt.cm.tab10
        facecolor = "w"
        edgecolor = "k"

    class Plot:
        fmt = "-"
        mec = "black"
        ms = 3
        linewidth = 1
        elinewidth = 1
        capsize = 3
        capthick = 0.5
        alpha = 0.7
        text_font_size = 10
        text_font_weight = "normal"
        text_font_style = "normal"#"oblique"
        text_font_family = "serif"
        
    class Grid:
        linewidth = 0.5
        linestyle = ":"
        alpha = 0.8

    class Title:
        fontsize = 10
        pad = 6
        fontweight = "bold"
        family = "serif"

    class Labels:
        labelpad = 10
        labelsize = 10
        style = "italic"
        tick_params = 3
        fontsize = 10
        fontweight = "regular"
        family = "serif"

    class Ticks:
        number_minor = 3
        minor_width = 0.3
        major_width = 0.8
        minor_length = 2
        major_length = 4
        direction = "in"
        minor_pad = 3
        major_pad = 5
        labelsize = 8
        labelcolor = "black"

    class Legend:
        loc = "best"
        frameone = True
        fontsize = 8
        title_fontsize = 8
        borderaxespad = 0
        borderpad = 0.4
        labelspacing = 0.3
        handlelength = 0.3
        graph_linewidth = 1.0
        edgecolor = "black"
        facecolor = "white"
        family = "serif"
        linewidth = 0.5
        alpha = 0.8
        bbox_to_anchor = None# (0.5, 1.25) #(0.98, 0.93)
        fancybox = True
        ncol = 2
        columnspacing = 0.5