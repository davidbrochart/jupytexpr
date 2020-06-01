import nest_asyncio
nest_asyncio.apply()
import asyncio
from time import time
import aiohttp
import pickle
import uuid
import numpy as np
from .dashboard import NullDashboard
from .state import State



class Cluster:

    def __init__(self, config):
        self.config = config
        self.dashboard_class = NullDashboard
        self.connected = False

    def connect(self):
        tasks = [self.start_kernel(url, self.config['servers'][url]['token']) for url in self.config['servers']]
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(asyncio.gather(*tasks))
        self.state = State(self.config)
        self.dashboard = self.dashboard_class(self.config)
        self.connected = True
        self.session = aiohttp.ClientSession()

    def set_dashboard(self, Dashboard):
        self.dashboard_class = Dashboard
        if self.connected:
            self.dashboard = self.dashboard_class(self.config)

    async def start_kernel(self, url, token):
        session = aiohttp.ClientSession()
        try:
            resp = await session.post(url + 'api/kernels?token=' + token)
        except Exception as e:
            print('Kernel: start failed {}'.format(str(e)))
            raise
        if resp.status != 201:
            print('Kernel: start failed')
        kernel_id = (await resp.json())['id']
        print('Kernel started {}'.format(kernel_id))
        ws_url = url + 'api/kernels/' + kernel_id + '/channels?token=' + token
        self.config['kernels'][kernel_id] = {}
        self.config['kernels'][kernel_id]['session'] = session
        self.config['kernels'][kernel_id]['url'] = url
        self.config['kernels'][kernel_id]['ws_url'] = ws_url
        self.config['kernels'][kernel_id]['ws'] = await session.ws_connect(ws_url)
        code = []
        code.append("import pickle")
        code.append("import numpy as np")
        code = '\n'.join(code)
        await self.run_in_kernel(kernel_id, ws_url, code)
        return url, kernel_id, ws_url

    # Arguments

    async def arg_chunk(self, mem_i, kernel_id, input_array):
        url = self.config['kernels'][kernel_id]['url']
        token = self.config['servers'][url]['token']
        url = f'{url}jupytexpr/{mem_i}?token={token}'
        await self.session.post(url, data=pickle.dumps(input_array))

    # Results

    async def res_chunk(self, mem_i, kernel_id, output_array, await_tasks=[]):
        for t in await_tasks:
            await t
        url = self.config['kernels'][kernel_id]['url']
        token = self.config['servers'][url]['token']
        url = f'{url}jupytexpr/{mem_i}?token={token}'
        async with self.session.get(url) as response:
            data = await response.read()
        r = pickle.loads(data)
        output_array[:] = r

    # Functions

    async def unary_func(self, func, mem_i0, mem_i1, kernel_id, await_tasks=[]):
        for t in await_tasks:
            await t
        code = get_code_unary(func, mem_i0, mem_i1, kernel_id)
        ws_url = self.config['kernels'][kernel_id]['ws_url']
        async with self.state.kernel_free[kernel_id]:
            await self.run_in_kernel(kernel_id, ws_url, code, func)

    async def binary_func(self, func, mem_i0, mem_i1, mem_i2, kernel_id, await_tasks=[]):
        for t in await_tasks:
            await t
        code = get_code_binary(func, mem_i0, mem_i1, mem_i2, kernel_id)
        ws_url = self.config['kernels'][kernel_id]['ws_url']
        async with self.state.kernel_free[kernel_id]:
            await self.run_in_kernel(kernel_id, ws_url, code, func)

    async def free_mem(self, mem, kernel_id, await_tasks=[]):
        for t in await_tasks:
            await t
        self.state.mem_free(kernel_id, len(mem))

    async def run_in_kernel(self, kernel_id, ws_url, code, func=None):
        msg_id = str(uuid.uuid4())
        ws = self.config['kernels'][kernel_id]['ws']
        j = request_execute_code(msg_id, code)
        await ws.send_json(j)
        if func is not None:
            self.dashboard.set(kernel_id, time(), 'Green', 'idle')
        async for msg_text in ws:
            msg = msg_text.json()
            if 'parent_header' in msg and msg['parent_header'].get('msg_id') == msg_id:
                if msg['channel'] == 'shell':
                    if msg['msg_type'] == 'execute_reply':
                        if msg['content']['status'] == 'ok':
                            break
                        else:
                            print(msg['content']['traceback'])
        if func is not None:
            self.dashboard.set(kernel_id, time(), 'White', func)


def request_execute_code(msg_id, code):
    return {
        "header": {
            "msg_id": msg_id,
            "username": 'fakeusername',
            "msg_type": "execute_request",
            "version": "5.2"
        },
        "metadata": {},
        "content": {
            "code": code,
            "silent": False,
            "store_history": True,
            "user_expressions": {},
            "allow_stdin": True,
            "stop_on_error": True
        },
        "buffers": [],
        "parent_header": {},
        "channel": "shell"
    }

def get_code_unary(func, mem_i0, mem_i1, kernel_id):
    code = []
    code.append(f"with open('{mem_i0}', 'rb') as f:")
    code.append("    a0 = pickle.load(f)")
    code.append(f"r = np.__getattribute__('{func}')(a0)")
    code.append(f"r = np.__getattribute__('{func}')(a0)")
    code.append(f"with open('{mem_i1}', 'wb') as f:")
    code.append("    pickle.dump(r, f)")
    code = '\n'.join(code)
    return code

def get_code_binary(func, mem_i0, mem_i1, mem_i2, kernel_id):
    code = []
    code.append(f"with open('{mem_i0}', 'rb') as f:")
    code.append("    a0 = pickle.load(f)")
    code.append(f"with open('{mem_i1}', 'rb') as f:")
    code.append("    a1 = pickle.load(f)")
    code.append(f"r = np.__getattribute__('{func}')(a0, a1)")
    code.append(f"with open('{mem_i2}', 'wb') as f:")
    code.append("    pickle.dump(r, f)")
    code = '\n'.join(code)
    return code
