import wx
import wx.lib.scrolledpanel
import wx.lib.agw.aui as aui
import wx.lib.mixins.inspection as wit

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar

class ExportWizardFrame(wx.Frame):
  def __init__(self, *args, **kw):
    # ensure the parent's __init__ is called
    super(ExportWizardFrame, self).__init__(*args, **kw)
    ew = ExportWizard(self)
    self.CreateStatusBar()


## IMPROVEMENT seems to not always work perfectly, some help text get "stuck"
def bind_to_status_bar_on_hover(w, help_text):
  def find_status_bar():
    w1 = w
    while w1 is not None:
      if isinstance(w1, wx.Frame):
        break
      else:
        w1 = w1.GetParent()
    if hasattr(w1, 'StatusBar') and w1.StatusBar is not None:
      return w1.StatusBar

  displaying_sb_ref = [None]

  def on_enter(ev):
    sb = find_status_bar()
    if (displaying_sb_ref[0] is None) and (sb is not None):
      displaying_sb_ref[0] = sb
      sb.PushStatusText(help_text)
    ev.Skip()

  def on_leave(ev):
    sb = displaying_sb_ref[0]
    if sb is not None:
      sb.PopStatusText()
      displaying_sb_ref[0] = None
    ev.Skip()

  w.Bind(wx.EVT_ENTER_WINDOW, on_enter)
  w.Bind(wx.EVT_LEAVE_WINDOW, on_leave)
  w.Bind(wx.EVT_WINDOW_DESTROY, on_leave)


class ExportWizard(wx.lib.scrolledpanel.ScrolledPanel):
  def __init__(self, parent, id=-1, **kw):
    #wx.Panel.__init__(self, parent, id=id, **kw)
    wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent, id=id, **kw)
    self.exported_cols = []
    self.next_i = 0

    vsizer_top = wx.BoxSizer(wx.VERTICAL)
    vsizer_cols = wx.BoxSizer(wx.VERTICAL)

    def create_col_panel(col_data):
      panel_col = wx.Panel(self, -1)

      hsizer_col = wx.BoxSizer(wx.HORIZONTAL)

      bullet = wx.StaticText(panel_col, label="•")

      txt_input = wx.TextCtrl(panel_col, value=col_data['txt_content'])
      def update_text(_ev):
        col_data['txt_content'] = txt_input.GetValue()
      txt_input.Bind(wx.EVT_TEXT, update_text)

      delete_btn = wx.Button(panel_col, label="X", size=(35, -1))

      def on_delete(_ev):
        old_excols = self.exported_cols
        i = old_excols.index(col_data)
        if i > -1:
          self.exported_cols = old_excols[0:i] + old_excols[i + 1:len(old_excols)]
        print(self.exported_cols)
        panel_col.Destroy()
        self.myScrollingCompatibleLayout()

      delete_btn.Bind(wx.EVT_BUTTON, on_delete)
      bind_to_status_bar_on_hover(delete_btn, "Delete this column")

      up_btn = wx.Button(panel_col, label="↑", size=(35, -1))

      def on_up(_ev):
        old_excols = self.exported_cols
        i = old_excols.index(col_data)
        if i > 0:
          self.exported_cols = old_excols[0:i - 1] + [col_data, old_excols[i - 1]] + old_excols[i + 1:len(old_excols)]
          vsizer_cols.Detach(panel_col)
          vsizer_cols.Insert(i - 1, panel_col, 0, wx.ALL)
          self.myScrollingCompatibleLayout()
          print(self.exported_cols)

      up_btn.Bind(wx.EVT_BUTTON, on_up)
      bind_to_status_bar_on_hover(up_btn, "Move up")

      down_btn = wx.Button(panel_col, label="↓", size=(35, -1))

      def on_down(_ev):
        old_excols = self.exported_cols
        i = old_excols.index(col_data)
        if i > -1 and i + 1 < len(old_excols):
          self.exported_cols = old_excols[0:i] + [old_excols[i + 1], col_data] + old_excols[i + 2:len(old_excols)]
          vsizer_cols.Detach(panel_col)
          vsizer_cols.Insert(i + 1, panel_col, 0, wx.ALL)
          self.myScrollingCompatibleLayout()
          print(self.exported_cols)

      down_btn.Bind(wx.EVT_BUTTON, on_down)
      bind_to_status_bar_on_hover(down_btn, "Move down")

      replicate_btn = wx.Button(panel_col, label="Replicate")

      def on_replicate(_ev):
        old_excols = self.exported_cols
        i = old_excols.index(col_data)
        if i > -1:
          id = self.next_i
          self.next_i += 1
          new_coldata = {}; new_coldata.update(col_data); new_coldata.update({'id': id})
          self.exported_cols = old_excols[0:i+1] + [new_coldata] + old_excols[i+1:len(old_excols)]
          new_panel_col = create_col_panel(new_coldata)
          vsizer_cols.Insert(i+1, new_panel_col)
          self.myScrollingCompatibleLayout()

      replicate_btn.Bind(wx.EVT_BUTTON, on_replicate)
      bind_to_status_bar_on_hover(replicate_btn, "Create a copy of this column just after this one.")

      hsizer_col.Add(bullet, 0, wx.ALL, 5)
      hsizer_col.Add(txt_input, 0, wx.ALL, 5)
      hsizer_col.Add(up_btn, 0, wx.ALL, 5)
      hsizer_col.Add(down_btn, 0, wx.ALL, 5)
      hsizer_col.Add(replicate_btn, 0, wx.ALL, 5)
      hsizer_col.Add(delete_btn, 0, wx.ALL, 5)
      panel_col.SetSizer(hsizer_col)

      return panel_col

    def on_add(_ev):
      id = self.next_i
      self.next_i += 1
      txt_content = "Coucou " + str(id)
      col_data = {'id': id, 'txt_content': txt_content}
      self.exported_cols.append(col_data)

      panel_col = create_col_panel(col_data)

      vsizer_cols.Add(panel_col, 0, wx.ALL)
      self.myScrollingCompatibleLayout()

    add_btn = wx.Button(self, -1, label="Add column")

    add_btn.Bind(wx.EVT_BUTTON, on_add)
    bind_to_status_bar_on_hover(add_btn, "Add a new column to the export")
    vsizer_top.Add(vsizer_cols, 0, wx.ALL)
    vsizer_top.Add(add_btn, 0, wx.ALL, 5)
    self.SetSizer(vsizer_top)
    self.SetupScrolling()
    self.SetAutoLayout(1)

  def myScrollingCompatibleLayout(self):
    self.Layout()
    self.SetupScrolling()



if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    frm = ExportWizardFrame(None, title='Export Wizard', size=(800, 200))
    frm.Show()
    app.MainLoop()
