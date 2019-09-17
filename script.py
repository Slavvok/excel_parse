from conn import db_session
from models import *
from datetime import datetime
import settings
import pandas as pd
import sys
import logging.config
import traceback
from functools import wraps
import time
import asyncio
import aiohttp
import async_timeout

logging.config.dictConfig(settings.dictConfig)
logger1 = logging.getLogger("scriptLogger")
logger2 = logging.getLogger("errorLogger")
_ = settings.ExceptionLogging


def timewrap(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        f = func(*args, **kwargs)
        end = time.time() - start
        return f, end
    return wrapper


async def url_parse(session, data):
    with async_timeout.timeout(settings.TIMEOUT):
        try:
            async with session.get(data.url) as resp:
                await resp.release()
                return resp, data
        except Exception as e:
            stack_info = traceback.format_exc()
            logger2.error(_(datetime.now(), e, data.url, stack_info))


async def multi_parse(loop):
    r = pd.read_excel(settings.DEFAULT_EXCEL_FILE, index_col=None)
    r = r[r.fetch == 1]
    async with aiohttp.ClientSession(loop=loop) as session:
        tasks = [url_parse(session, data) for index, data in r.iterrows()]
        m = await asyncio.gather(*tasks)
        return list(zip(m, [data for index, data in r.iterrows()]))


def insert_data(resp_list):
    monitor_list = []
    for resp, data in resp_list:
        if not db_session.query(Monitoring).filter_by(label=data.label)\
                .count() and resp:
            ts = datetime.now()
            response_time = resp.elapsed.total_seconds()
            status_code = resp.status_code
            content_length = len(resp.content)
            m = Monitoring(ts, data.url, data.label, response_time,
                           status_code, content_length)
            monitor_list.append(m)
    db_session.add_all(monitor_list)
    db_session.commit()
    return len(monitor_list)


def delete_data():
    from models import Monitoring
    from conn import db_session
    db_session.query(Monitoring).delete()
    db_session.commit()


@timewrap
def get_data():
    loop = asyncio.get_event_loop()
    resp_list = loop.run_until_complete(multi_parse(loop))
    added_amount = insert_data(resp_list)
    return len(resp_list), added_amount


if __name__ == "__main__":
    if len(sys.argv) >= 1:
        settings.DEFAULT_EXCEL_FILE = sys.argv[1]
    data, tt = get_data()
    logger1.info(f"Filename: {settings.DEFAULT_EXCEL_FILE} "
                 f"Fetched: {data[0]} Added: {data[1]} "
                 f"Time: {tt} ")
