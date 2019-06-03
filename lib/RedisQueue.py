import redis



class RedisQueue(object):
    def __init__(self, name, host, port, password, decode_responses=True):
        self.key = str(name)
        self.host = host
        self.port = port
        self.password = password
        self.decode_responses = decode_responses
        self.__pool = redis.ConnectionPool(host=self.host, port=self.port, password=self.password, decode_responses=self.decode_responses)
        self.__db = redis.Redis(connection_pool=self.__pool)

    def qsize(self):
        return self.__db.llen(self.key)

    def put(self, item):
        self.__db.rpush(self.key, item)

    def get(self, timeout=None):
        item = self.__db.brpop(self.key, timeout=timeout)
        return item

    def ltrim(self):
        self.__db.ltrim(self.key, 1, 0)

