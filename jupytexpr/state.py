import asyncio
import os



class State(object):
    def __init__(self, config):
        kernel_nb = len(config['kernels'])
        kernels = config['kernels']
        self.mem_busy = {k: 0 for k in kernels.keys()}
        self.free_mem_nb = {k: config['mem_nb'] for k in kernels.keys()}
        self.free_kernel_nb = kernel_nb
        self.kernel_free = {k: asyncio.Lock() for k in kernels.keys()}
        self.mem_i = 0
        os.makedirs('data', exist_ok=True)
    def alloc(self, busy, nb, i0=0, i1=None):
        res = []
        if i1 is None:
            i1 = len(busy)
        i = i0
        for _ in range(nb):
            while busy[i]:
                i += 1
                if i == i1:
                    i = i0
            busy[i] = True
            res.append(i)
        if nb == 1:
            return res[0]
        return res

    def mem_free(self, kid, nb=1):
        self.mem_busy[kid] -= nb
        self.free_mem_nb[kid] += nb

    def request(self, mem_nb):
        # request for resources (a kernel that has this memory)
        # the current strategy is to allocate memory on the kernel
        # that has the less allocated memory
        less_busy = -1
        kid = None
        mem = None
        for k, v in self.mem_busy.items():
            if (v < less_busy or less_busy < 0) and (self.free_mem_nb[k] - mem_nb >= 0):
                less_busy = v
                kid = k
                if v == 0:
                    break

        if kid is not None:
            self.free_mem_nb[kid] -= mem_nb
            self.mem_busy[kid] += mem_nb
            mem = [f'data/{self.mem_i+i}' for i in range(mem_nb)]
            self.mem_i += mem_nb

        return kid, mem
