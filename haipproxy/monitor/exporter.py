import logging
import time

from prometheus_client import start_http_server
from prometheus_client.core import (CounterMetricFamily, GaugeMetricFamily,
                                    REGISTRY)

from haipproxy.config.settings import (
    DATA_ALL,
    INIT_HTTP_Q,
    SPIDER_COMMON_Q,
    SPIDER_AJAX_Q,
    SPIDER_GFW_Q,
    SPIDER_AJAX_GFW_Q,
    TEMP_ZHIHU_Q,
    VALIDATED_ZHIHU_Q,
    TTL_ZHIHU_Q,
    SPEED_ZHIHU_Q,
    TTL_VALIDATED_RESOURCE,
    LOWEST_SCORE,
    LONGEST_RESPONSE_TIME,
    EXPORTER_LISTEN_HOST,
    EXPORTER_LISTEN_PORT,
)
from haipproxy.utils import get_redis_conn

logger = logging.getLogger(__name__)


class CustomCollector:
    def __init__(self):
        self.redis_conn = get_redis_conn()

    def collect(self):
        start_time = int(time.time()) - TTL_VALIDATED_RESOURCE * 60

        pipe = self.redis_conn.pipeline(False)
        pipe.scard(DATA_ALL)
        pipe.llen(INIT_HTTP_Q)
        pipe.scard(TEMP_ZHIHU_Q)
        pipe.zrevrangebyscore(VALIDATED_ZHIHU_Q, '+inf', LOWEST_SCORE)
        pipe.zrevrangebyscore(TTL_ZHIHU_Q, '+inf', start_time)
        pipe.zrangebyscore(SPEED_ZHIHU_Q, 0, 1000 * LONGEST_RESPONSE_TIME)
        pipe.llen(SPIDER_COMMON_Q)
        pipe.llen(SPIDER_AJAX_Q)
        pipe.llen(SPIDER_GFW_Q)
        pipe.llen(SPIDER_AJAX_GFW_Q)
        r = pipe.execute()
        available_proxies = len(set(r[3]) & set(r[4]) & set(r[5]))

        yield CounterMetricFamily('total_proxies', 'total proxies', r[0])
        yield GaugeMetricFamily('init_proxies', 'total init proxies', r[1])
        yield GaugeMetricFamily('to_validated_proxies',
                                'total proxies to validate', r[2])
        yield GaugeMetricFamily('scored_proxies', 'high score proxies',
                                len(r[3]))
        yield GaugeMetricFamily('alive_proxies', 'proxies validated recently',
                                len(r[4]))
        yield GaugeMetricFamily('speed_proxies', 'high speed proxies',
                                len(r[5]))
        yield GaugeMetricFamily('available_proxies', 'proxies of high quality',
                                available_proxies)
        yield GaugeMetricFamily('total_common_task', 'common task num', r[6])
        yield GaugeMetricFamily('total_ajax_task', 'ajax task num', r[7])
        yield GaugeMetricFamily('total_gfw_task', 'gfw task num', r[8])
        yield GaugeMetricFamily('total_ajax_gfw_task', 'ajax gfw task num',
                                r[9])


def exporter_start():
    logger.info('starting server http://{}:{}/metrics'.format(
        EXPORTER_LISTEN_HOST, EXPORTER_LISTEN_PORT))
    REGISTRY.register(CustomCollector())
    start_http_server(EXPORTER_LISTEN_PORT, addr=EXPORTER_LISTEN_HOST)
    while True:
        time.sleep(5)
