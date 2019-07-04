"""
scrapy pipelines for storing proxy ip infos.
"""
import logging
import time

from ..utils import get_redis_conn
from ..config.settings import (REDIS_DB, DATA_ALL, INIT_HTTP_Q, INIT_SOCKS4_Q,
                               INIT_SOCKS5_Q, REDIS_PIPE_BATCH_SIZE)
from .items import (ProxyScoreItem, ProxyVerifiedTimeItem, ProxySpeedItem)

logger = logging.getLogger(__name__)


class BasePipeline:
    def open_spider(self, spider):
        self.redis_conn = get_redis_conn()
        self.pipe = self.redis_conn.pipeline()
        self.pipe_size = 0

    def close_spider(self, spider):
        self.pipe.execute()
        logger.info(f'{self.pipe_size} redis commands executed')


class ProxyIPPipeline(BasePipeline):
    def process_item(self, item, spider):
        url = item.get('url', None)
        if not url:
            return item
        not_exists = self.pipe.hmset(
            url, {
                'used_count': 0,
                'success_count': 0,
                'total_seconds': 0,
                'last_fail': '',
                'timestamp': 0,
                'score': 0
            })
        self.pipe_size += 1
        if not_exists:
            if 'socks4' in url:
                self.pipe.rpush(INIT_SOCKS4_Q, url)
            elif 'socks5' in url:
                self.pipe.rpush(INIT_SOCKS5_Q, url)
            else:
                self.pipe.rpush(INIT_HTTP_Q, url)
            self.pipe_size += 1
        if self.pipe_size >= REDIS_PIPE_BATCH_SIZE:
            self.pipe.execute()
            logger.info(f'{self.pipe_size} redis commands executed')
            self.pipe_size = 0
        return item


class ProxyStatPipeline(BasePipeline):
    def process_item(self, item, spider):
        # stat = self.redis_conn.hgetall(item['proxy'])
        # stat['used_count'] += 1
        # stat['success_count'] += item['success']
        # stat['total_seconds'] += item['seconds']
        # stat['last_fail'] = item['fail']
        # stat['timestamp'] = int(time.time())
        # self.redis_conn.hmset(item['proxy'], stat)
        # return item
        self.pipe.hincrby(item['proxy'], 'used_count')
        self.pipe.hincrby(item['proxy'], 'success_count', item['success'])
        self.pipe.hincrby(item['proxy'], 'total_seconds', item['seconds'])
        self.pipe.hset(item['proxy'], 'last_fail', item['fail'])
        self.pipe.hset(item['proxy'], 'timestamp', int(time.time()))
        self.pipe.execute()
        return item

class ProxyCommonPipeline(BasePipeline):
    def process_item(self, item, spider):
        if isinstance(item, ProxyScoreItem):
            self._process_score_item(item, spider)
        if isinstance(item, ProxyVerifiedTimeItem):
            self._process_verified_item(item, spider)
        if isinstance(item, ProxySpeedItem):
            self._process_speed_item(item, spider)
        return item

    def _process_score_item(self, item, spider):
        score = self.redis_conn.zscore(item['queue'], item['url'])
        if score is None:
            self.redis_conn.zadd(item['queue'], {item['url']: item['score']})
        else:
            # delete ip resource when score < 1 or error happens
            if item['incr'] == '-inf' or (item['incr'] < 0 and score <= 1):
                self.pipe.zrem(item['queue'], item['url'])
                self.pipe.execute()
            elif item['incr'] < 0 and 1 < score:
                self.redis_conn.zincrby(item['queue'], -1, item['url'])
            elif item['incr'] > 0 and score < 10:
                self.redis_conn.zincrby(item['queue'], 1, item['url'])
            elif item['incr'] > 0 and score >= 10:
                incr = round(10 / score, 2)
                self.redis_conn.zincrby(item['queue'], incr, item['url'])

    def _process_verified_item(self, item, spider):
        if item['incr'] == '-inf' or item['incr'] >= 0:
            self.redis_conn.zadd(item['queue'],
                                 {item['url']: item['verified_time']})

    def _process_speed_item(self, item, spider):
        if item['incr'] == '-inf' or item['incr'] >= 0:
            self.redis_conn.zadd(item['queue'],
                                 {item['url']: item['response_time']})
