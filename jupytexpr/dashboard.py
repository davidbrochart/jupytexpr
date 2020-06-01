from bqplot import OrdinalScale, LinearScale, OrdinalColorScale, Bars, Axis, Figure
from ipywidgets import VBox, Layout, Button



class NullDashboard:
    def __init__(self, config):
        pass
    def set(self, kernel_id, t, busy, func):
        pass
    def show(self):
        pass


button = Button()
functions = {}
kernels = []
bars = []


def print_event(self, target):
    kernel_id = kernels[bars.index(self)]
    i = target['data']['sub_index'] - 1
    button.description = functions[kernel_id][i]


class Dashboard:

    def __init__(self, config):
        global kernels
        self.config = config
        kernel_figs = self.get_figs()
        nb = len(kernel_figs)
        self.prev_time = [0 for i in range(nb)]
        self.prev_busy = ['White' for i in range(nb)]
        self.db = VBox(kernel_figs)
        self.initialized = True
        self.t0 = 0
        self.first = True
        for kernel_id in self.config['kernels'].keys():
            functions[kernel_id] = []
            kernels.append(kernel_id)

    def get_figs(self):
        x = OrdinalScale()
        y = LinearScale()
        col_sc = OrdinalColorScale(colors=['White', 'Green', 'Red'])
        figs = []
        for kernel_id in self.config['kernels'].keys():
            times = [[0]]
            bar = Bars(x=[0], y=times, scales={'x': x, 'y': y, 'color': col_sc}, orientation='horizontal', stroke='White')
            xax = Axis(scale=x, orientation='vertical')
            yax = Axis(scale=y, orientation='horizontal', num_ticks=0)
            bar.color = ['White']
            bar.on_hover(print_event)
            ins = button
            bar.tooltip = ins
            fig = Figure(marks=[bar], axes=[xax, yax], background_style={'fill': 'White'}, layout=Layout(width='99%', height='10px'), fig_margin={'top': 0, 'bottom': 0, 'left': 0, 'right': 0})
            figs.append(fig)
            bars.append(bar)
        return figs

    def show(self):
        return self.db

    def set(self, kernel_id, t, busy, func):
        if func is None:
            return
        functions[kernel_id].append(func)
        if self.first:
            self.first = False
            self.t0 = t
        t -= self.t0
        offset = list(self.config['kernels']).index(kernel_id)
        child = self.db.children[offset]
        bar = child.marks[0]
        busys = list(bar.color)
        busys.append(self.prev_busy[offset])
        self.prev_busy[offset] = busy
        times = [[i[0]] for i in bar.y]
        times.append([t - self.prev_time[offset]])
        self.prev_time[offset] = t
        bar.color = busys
        bar.y = times
