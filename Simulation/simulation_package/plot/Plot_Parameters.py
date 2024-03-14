from figure_size import set_size
import matplotlib.pyplot as plt

class PlotParameters:
    
    def __init__(self, latex_width):
        self.latex_width = latex_width
        self.Figure = self.Figure(self)
        
    class Figure:
        def __init__(self, outer_class):
            self.latex_width = outer_class.latex_width
            self.figsize = set_size(self.latex_width, fraction = 0.475, subplots = (1,1))
            
        colors = plt.cm.Set1
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
        text_font_size = 11
        text_font_weight = "bold"
        text_font_style = "oblique"
        
    class Grid:
        linewidth = 0.5
        linestyle = ":"
        alpha = 0.8

    class Title:
        fontsize = 11
        pad = 1
        fontweight = "bold"

    class Labels:
        labelpad = 10
        labelsize = 11
        style = "italic"
        x_lab_size = 11
        tick_params = 3
        fontsize = 11
        fontweight = "bold"
    
    class Ticks:
        number_minor = 3
        minor_width = 0.5
        major_width = 1.5
        minor_length = 4
        major_length = 6
        direction = "in"
        minor_pad = 3
        major_pad = 5
        labelsize = 11
        labelcolor = "black"

    class Legend:
        loc = "upper right"
        frameone = True
        fontsize = 9
        title_fontsize = 11
        borderaxespad = 0.5
        borderpad = 1
        labelspacing = 1.0
        handlelength = 2.0
        edgecolor = "black"
        facecolor = "white"
        linewidth = 1.0
        alpha = 0.8
        bbox_to_anchor = (0.98, 0.93)
        fancybox = True
        ncol = 3