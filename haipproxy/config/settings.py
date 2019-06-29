"""
Settings for global.
"""
#####################################################################
# Scrapy settings of this project
#####################################################################
# scrapy basic info
BOT_NAME = 'haiproxy'
SPIDER_MODULES = ['haipproxy.crawler.spiders', 'haipproxy.crawler.validators']
NEWSPIDER_MODULE = 'haipproxy.crawler'

# downloader settings
ROBOTSTXT_OBEY = False
COOKIES_ENABLED = False
DOWNLOAD_TIMEOUT = 30

# to aviod infinite recursion
DEPTH_LIMIT = 100
CONCURRENT_REQUESTS = 30

# don't filter anything, also can set dont_filter=True in Request objects
DUPEFILTER_CLASS = 'scrapy.dupefilters.BaseDupeFilter'
HTTPCACHE_ENABLED = False
GFW_PROXY = 'http://127.0.0.1:8123'

# splash settings.If you use docker-compose,SPLASH_URL = 'http://splash:8050'
SPLASH_URL = 'http://127.0.0.1:8050'

# extension settings
RETRY_ENABLED = False
TELNETCONSOLE_ENABLED = False

UserAgentMiddleware = 'haipproxy.crawler.middlewares.UserAgentMiddleware'
ProxyMiddleware = 'haipproxy.crawler.middlewares.ProxyMiddleware'
DOWNLOADER_MIDDLEWARES = {
    UserAgentMiddleware: 543,
    ProxyMiddleware: 543,
    'scrapy_splash.SplashCookiesMiddleware': 723,
    # it should be prior to HttpProxyMiddleware
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware':
    810,
}

SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
}

# scrapy log settings
LOG_LEVEL = 'INFO'

# redis settings.If you use docker-compose, REDIS_HOST = 'redis'
# if some value is empty, set like this: key = ''
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PIPE_BATCH_SIZE = 500

# scheduler settings
TIMER_RECORDER = 'haipproxy:scheduler:task'
LOCKER_PREFIX = 'haipproxy:lock:'

# proxies crawler's settings
SPIDER_FEED_SIZE = 10
SPIDER_COMMON_Q = 'haipproxy:spider:common'
SPIDER_AJAX_Q = 'haipproxy:spider:ajax'
SPIDER_GFW_Q = 'haipproxy:spider:gfw'
SPIDER_AJAX_GFW_Q = 'haipproxy:spider:ajax_gfw'

# data_all is a set , it's a dupefilter
DATA_ALL = 'haipproxy:all'

# the data flow is init queue->validated_queue->validator_queue(temp)->validated_queue(score queue)->
# ttl_queue, speed_qeuue -> clients
# http_queue is a list, it's used to store initially http/https proxy resourecs
INIT_HTTP_Q = 'haipproxy:init:http'

# socks proxy resources container
INIT_SOCKS4_Q = 'haipproxy:init:socks4'
INIT_SOCKS5_Q = 'haipproxy:init:socks5'

# custom validator settings
VALIDATOR_FEED_SIZE = 50

# they are temp sets, come from init queue, in order to filter transparnt ip
TEMP_HTTP_Q = 'haipproxy:http:temp'
TEMP_HTTPS_Q = 'haipproxy:https:temp'
TEMP_WEIBO_Q = 'haipproxy:weibo:temp'
TEMP_ZHIHU_Q = 'haipproxy:zhihu:temp'

# valited queues are zsets.squid and other clients fetch ip resources from them.
VALIDATED_HTTP_Q = 'haipproxy:validated:http'
VALIDATED_HTTPS_Q = 'haipproxy:validated:https'
VALIDATED_WEIBO_Q = 'haipproxy:validated:weibo'
VALIDATED_ZHIHU_Q = 'haipproxy:validated:zhihu'

# time to live of proxy ip resources
TTL_VALIDATED_RESOURCE = 2  # minutes
TTL_HTTP_Q = 'haipproxy:ttl:http'
TTL_HTTPS_Q = 'haipproxy:ttl:https'
TTL_WEIBO_Q = 'haipproxy:ttl:weibo'
TTL_ZHIHU_Q = 'haipproxy:ttl:zhihu'

# queue for proxy speed
SPEED_HTTP_Q = 'haipproxy:speed:http'
SPEED_HTTPS_Q = 'haipproxy:speed:https'
SPEED_WEIBO_Q = 'haipproxy:speed:weibo'
SPEED_ZHIHU_Q = 'haipproxy:speed:zhihu'

# squid settings on linux os
# execute sudo chown -R $USER /etc/squid/ and
# sudo chown -R $USER /var/log/squid/cache.log at first
SQUID_BIN_PATH = '/usr/sbin/squid'  # mac os '/usr/local/sbin/squid'
SQUID_CONF_PATH = '/etc/squid/squid.conf'  # mac os '/usr/local/etc/squid.conf'
SQUID_TEMPLATE_PATH = '/etc/squid/squid.conf.backup'  # mac os /usr/local/etc/squid.conf.backup

# client settings

# client picks proxies which's response time is between 0 and LONGEST_RESPONSE_TIME seconds
LONGEST_RESPONSE_TIME = 10

# client picks proxies which's score is not less than LOWEST_SCORE
LOWEST_SCORE = 6

# if the total num of proxies fetched is less than LOWES_TOTAL_PROXIES, haipproxy will fetch more
# more proxies with lower quality
LOWEST_TOTAL_PROXIES = 5
# if no origin ip is given, request will be sent to https://httpbin.org/ip
ORIGIN_IP = ''

#### monitor and bug trace

# sentry for error tracking, for more information see
# https://github.com/getsentry/sentry
import sentry_sdk
sentry_sdk.init(
    # replace with your own path here.
    # use empty path to disable it
    'https://e5278b49bb5c426ab66bda0d2b59f2ae@sentry.io/1488193',
    debug=False,
)

# prometheus for monitoring, for more information see
# https://github.com/prometheus/prometheus
# you have to config prometheus first if you want to monitor haipproxy status
EXPORTER_LISTEN_HOST = '0.0.0.0'
EXPORTER_LISTEN_PORT = 7001
