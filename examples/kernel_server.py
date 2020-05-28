from subprocess import Popen, PIPE


def get_lines(std_pipe):
    '''Generator that yields lines from a standard pipe as they are printed.'''
    for line in iter(std_pipe.readline, ''):
        yield line
    std_pipe.close()


def launch_kernel_server():
    p = Popen('jupyter notebook --no-browser --ip=127.0.0.1'.split(), stderr=PIPE, universal_newlines=True)

    state = 'before_ip'
    for line in get_lines(p.stderr):
        if state == 'before_ip':
            if 'The Jupyter Notebook is running at:' in line:
                state = 'get_ip'
        elif state == 'get_ip':
            i = line.find('http')
            url = line[i:-1]
            s = '?token='
            i = url.find(s)
            token = url[i + len(s):]
            url = url[:i]
            break

    print(url + '?token=' + token)
    return url, token, p.pid


def serve_kernels(nb=1):
    '''When you're done, just kill 'em all!
    killall -9 jupyter-notebook
    '''
    url_token = []
    pids = []
    for i in range(nb):
        url, token, pid = launch_kernel_server()
        url_token.append((url, token))
        pids.append(pid)
    #url_token = [launch_kernel_server() for i in range(nb)]
    return url_token, pids
