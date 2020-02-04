## From WxPython tutorial: https://www.wxpython.org/pages/overview/#hello-world

"""
Hello World, but with more meat.
"""

import wx
import wx.lib.agw.aui as aui
import wx.lib.mixins.inspection as wit

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar

import numpy as np
import kernel_utils as ku

import pandas as pd

class HelloFrame(wx.Frame):
    """
    A Frame that says Hello World
    """

    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(HelloFrame, self).__init__(*args, **kw)

        gp_plot = GpPlot(self, GpState())

        # create a panel in the frame
        # pnl = wx.Panel(self)
        #
        # # put some text with a larger bold font on it
        # st = wx.StaticText(pnl, label="Hello World!")
        # font = st.GetFont()
        # font.PointSize += 10
        # font = font.Bold()
        # st.SetFont(font)
        #
        # # and create a sizer to manage the layout of child widgets
        # sizer = wx.BoxSizer(wx.VERTICAL)
        # #sizer.Add(st, wx.SizerFlags().Border(wx.TOP|wx.LEFT, 25))
        # sizer.Add(GpPlot(pnl, GpState()), wx.SizerFlags()) #.Border(wx.TOP | wx.LEFT, 25))
        # pnl.SetSizer(sizer)

        # create a menu bar
        self.makeMenuBar()

        # and a status bar
        self.CreateStatusBar()
        self.SetStatusText("Welcome to wxPython!")


    def makeMenuBar(self):
        """
        A menu bar is composed of menus, which are composed of menu items.
        This method builds a set of menus and binds handlers to be called
        when the menu item is selected.
        """

        # Make a file menu with Hello and Exit items
        fileMenu = wx.Menu()
        # The "\t..." syntax defines an accelerator key that also triggers
        # the same event
        helloItem = fileMenu.Append(-1, "&Hello...\tCtrl-H",
                "Help string shown in status bar for this menu item")
        fileMenu.AppendSeparator()
        # When using a stock ID we don't need to specify the menu item's
        # label
        exitItem = fileMenu.Append(wx.ID_EXIT)

        # Now a help menu for the about item
        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)

        # Make the menu bar and add the two menus to it. The '&' defines
        # that the next letter is the "mnemonic" for the menu item. On the
        # platforms that support it those letters are underlined and can be
        # triggered from the keyboard.
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(helpMenu, "&Help")

        # Give the menu bar to the frame
        self.SetMenuBar(menuBar)

        # Finally, associate a handler function with the EVT_MENU event for
        # each of the menu items. That means that when that menu item is
        # activated then the associated handler function will be called.
        self.Bind(wx.EVT_MENU, self.OnHello, helloItem)
        self.Bind(wx.EVT_MENU, self.OnExit,  exitItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)


    def OnExit(self, event):
        """Close the frame, terminating the application."""
        self.Close(True)


    def OnHello(self, event):
        """Say hello to the user."""
        wx.MessageBox("Hello again from wxPython")


    def OnAbout(self, event):
        """Display an About Dialog"""
        wx.MessageBox("This is a wxPython Hello World sample",
                      "About Hello World 2",
                      wx.OK|wx.ICON_INFORMATION)


mean_fn = ku.constant_fn(0.5)
kernel_fn = ku.kernel_Matern3_2_1D(1e1, 1e-1)
kernel_params = (kernel_fn, mean_fn)
noise_var_fn = ku.constant_fn(1e-2 ** 2)


def predictions(observed_data):
  xs = np.array([np.linspace(0., 1., 100)]).transpose()
  predict = ku.predictor(kernel_params, noise_var_fn, observed_data)
  predicted_means, = predict(xs)
  return (xs[:, 0], predicted_means)


initial_data = (np.array([[0.2]]), np.array([0.72]))

class GpState:
  def __init__(self):
    self.initialize()

  def initialize(self):
    self.observed_data = initial_data

  def add_observed(self, x, y):
    ox, oy = self.observed_data
    self.observed_data = (np.append(ox, np.array([[x]]), axis=0), np.append(oy, np.array([y]), axis=0))


def export_observed_data_csv(file, observed_data):
  observed_x, observed_y = observed_data
  df = pd.DataFrame({'observed_x': observed_x[:, 0], 'observed_y': observed_y})
  df.to_csv(file, index=False, sep=",")


class GpPlot(wx.Panel):
  def __init__(self, parent, gp_state, id=-1, dpi=None, **kwargs):
    wx.Panel.__init__(self, parent, id=id, **kwargs)
    self.gp_state = gp_state
    self.figure = mpl.figure.Figure(dpi=dpi, figsize=(4, 4))
    self.canvas = FigureCanvas(self, -1, self.figure)
    self.toolbar = NavigationToolbar(self.canvas)
    self.toolbar.Realize()

    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(self.canvas, 1, wx.EXPAND)

    export_btn = wx.Button(self, -1, label="Export observed data as CSV")

    def export(ev):
      with wx.FileDialog(self, "Save CSV file", wildcard="CSV files (*.csv)|*.csv",
                         style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

        if fileDialog.ShowModal() == wx.ID_CANCEL:
          return  # the user changed their mind

        # save the current contents in the file
        pathname = fileDialog.GetPath()
        try:
          with open(pathname, 'w') as file:
            export_observed_data_csv(file, self.gp_state.observed_data)
        except IOError:
          wx.LogError("Cannot save current data in file '%s'." % pathname)
    export_btn.Bind(wx.EVT_BUTTON, export)
    sizer.Add(export_btn)

    clear_button = wx.Button(self, -1, label="Reset")
    def reset(ev):
      self.gp_state.initialize()
      self.refresh_plot()
    clear_button.Bind(wx.EVT_BUTTON, reset)
    sizer.Add(clear_button)

    sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
    self.SetSizer(sizer)
    self.refresh_plot()

    def on_click_figure(ev):
      self.gp_state.add_observed(ev.xdata, ev.ydata)
      self.refresh_plot()

    _cid = self.figure.canvas.mpl_connect('button_press_event', on_click_figure)

  def refresh_plot(self):
    observed_data = self.gp_state.observed_data
    fig = self.figure
    xs, predicted_means = predictions(observed_data)
    ax = fig.gca()
    ax.clear()
    observed_xs, observed_y = observed_data
    ax.scatter(observed_xs[:, 0], observed_y)
    ax.plot(xs, predicted_means)
    ax.legend(['Predicted mean', 'Observed data'])
    ax.set_title("Gaussian Process regression. Click figure to add observed data points.")
    plt.show()
    fig.canvas.draw()




if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    frm = HelloFrame(None, title='SciPy GUI demo', size=(800, 600))
    frm.Show()
    app.MainLoop()
