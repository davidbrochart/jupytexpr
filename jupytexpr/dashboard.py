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


def show_func(self, target):
    kernel_id = kernels[bars.index(self)]
    i = target['data']['sub_index'] - 1
    button.description = functions[kernel_id][i]


class Dashboard:

    def __init__(self, config):
        global kernels
        self.config = config
        kernel_figs = self.get_figs()
        self.nb = len(kernel_figs)
        self.prev_time = [0] * self.nb
        self.prev_busy = ['White'] * self.nb  # every kernel is idle at the beginning
        self.db = VBox(kernel_figs)
        self.initialized = True
        self.t0 = 0
        self.first = True
        self.window = None  # size of the shown window in seconds
        for kernel_id in self.config['kernels'].keys():
            functions[kernel_id] = []
            kernels.append(kernel_id)

    def get_figs(self):
        x = OrdinalScale()
        y = LinearScale()  # because it is common to all kernels, all kernels react
                           # each time a state is set on a kernel
        col_sc = OrdinalColorScale(colors=['White', 'Green', 'Red'])
        figs = []
        for kernel_id in self.config['kernels'].keys():
            bar = Bars(x=[0], y=[[0]], scales={'x': x, 'y': y, 'color': col_sc}, orientation='horizontal')#, stroke='White')
            xax = Axis(scale=x, orientation='vertical')
            yax = Axis(scale=y, orientation='horizontal', num_ticks=0)
            bar.color = ['White']
            bar.on_hover(show_func)
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
            # code that we don't want to show in the dashboard
            return
        functions[kernel_id].append(func)
        if self.first:
            self.first = False
            self.t0 = t
        t -= self.t0
        idx = list(self.config['kernels']).index(kernel_id)
        child = self.db.children[idx]
        bar = child.marks[0]
        busys = list(bar.color)
        busys.append(self.prev_busy[idx])
        self.prev_busy[idx] = busy
        times = list(bar.y)
        dt = t - self.prev_time[idx]
        times.append([dt])
        self.prev_time[idx] = t
        bar.color = busys
        bar.y = times
        # show a window of the last n seconds
        # FIXME: too slow (too much data sent to the browser)
        if self.window is not None:
            # update all other kernels' state
            for idx2 in range(self.nb):
                if idx2 != idx:
                    child = self.db.children[idx2]
                    bar = child.marks[0]
                    busys = list(bar.color)
                    busys.append(self.prev_busy[idx2])
                    self.prev_busy[idx2] = self.prev_busy[idx2]
                    times = list(bar.y)
                    times.append([dt])
                    self.prev_time[idx2] = t
                    bar.color = busys
                    bar.y = times
            for idx2 in range(self.nb):
                child = self.db.children[idx2]
                bar = child.marks[0]
                busys = list(bar.color)
                times = list(bar.y)
                win = 0
                for i, dt in enumerate(times[::-1]):
                    win += dt[0]
                    if win >= self.window:
                        times[-1 - i] = [win - self.window]
                        bar.y = times[-1 - i:]
                        bar.color = busys[-1 - i:]
                        break
