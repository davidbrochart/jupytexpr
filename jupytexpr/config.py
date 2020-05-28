class Config:

    def __init__(self, url_token, mem_nb, mem_depth):
        self.config = {'servers': {}, 'kernels': {}, 'mem_nb': mem_nb, 'mem_depth': mem_depth}
        for url, token in url_token:
            self.config['servers'][url] = {'token' : token}
