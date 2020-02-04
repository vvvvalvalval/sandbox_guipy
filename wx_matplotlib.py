## From Matplotlib Gallery: https://matplotlib.org/gallery/user_interfaces/embedding_in_wx5_sgskip.html

import wx
import wx.lib.scrolledpanel
import wx.lib.agw.aui as aui
import wx.lib.mixins.inspection as wit

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar


class Plot(wx.Panel):
    def __init__(self, parent, id=-1, dpi=None, **kwargs):
        wx.Panel.__init__(self, parent, id=id, **kwargs)
        self.figure = mpl.figure.Figure(dpi=dpi, figsize=(2, 2))
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.Realize()
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.EXPAND)
        btn = wx.Button(self, -1, "Toggle curve")
        sizer.Add(btn, 0, wx.EXPAND)
        screenSize = wx.DisplaySize()
        screenWidth, screenHeight = screenSize
        text_panel = wx.lib.scrolledpanel.ScrolledPanel(self, -1, size=(screenWidth, 100), style=wx.SIMPLE_BORDER)
        text_panel.SetupScrolling()
        text_sizer = wx.BoxSizer(wx.VERTICAL)
        text_panel.SetSizer(text_sizer)
        def when_clicked(ev):
          print(ev)
          text_sizer.Add(wx.StaticText(text_panel, label="coucou"), 1)
          text_sizer.Fit(text_panel)
        btn.Bind(wx.EVT_BUTTON, when_clicked)
        sizer.Add(text_panel, 1, wx.LEFT | wx.EXPAND)
        sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        self.SetSizer(sizer)


class PlotNotebook(wx.Panel):
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id=id)
        self.nb = aui.AuiNotebook(self)
        sizer = wx.BoxSizer()
        sizer.Add(self.nb, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def add(self, name="plot"):
        page = Plot(self.nb)
        self.nb.AddPage(page, name)
        return page.figure

def demo():
    # alternatively you could use
    #app = wx.App()
    # InspectableApp is a great debug tool, see:
    # http://wiki.wxpython.org/Widget%20Inspection%20Tool
    app = wit.InspectableApp()
    frame = wx.Frame(None, -1, 'Plotter')
    plotter = PlotNotebook(frame)
    fig1 = plotter.add('figure 1')
    axes1 = fig1.gca()
    l1, = axes1.plot([1, 2, 3], [2, 1, 4])

    def toggle_line(event):
      l1.set_visible(not l1.get_visible())
      fig1.canvas.draw() ## important for refreshing the display


    ## From https://matplotlib.org/users /event_handling.html
    cid = fig1.canvas.mpl_connect('button_press_event', toggle_line) ## cid is an integer
    print("cid: " + str(cid))


    axes2 = plotter.add('figure 2').gca()
    axes2.plot([1, 2, 3, 4, 5], [2, 1, 4, 2, 3])
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    demo()
