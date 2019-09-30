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
log_info = logging.getLogger("scriptLogger")
log_except = logging.getLogger("exceptionLogger")
_ = settings.ExceptionLogging


def timewrap(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        f = func(*args, **kwargs)
        end_time = time.time() - start_time
        return f, end_time
    return wrapper


async def url_parse(session, row):
    with async_timeout.timeout(settings.TIMEOUT):
        try:
            async with session.get(row.url) as resp:
                await resp.release()
                return resp, row
        except Exception as e:
            stack_info = traceback.format_exc()
            log_except.error(_(datetime.now(), e, row.url, stack_info))


async def multi_parse(loop):
    table = pd.read_excel(settings.DEFAULT_EXCEL_FILE, index_col=None)
    table = table[table.fetch == 1]
    async with aiohttp.ClientSession(loop=loop) as session:
        tasks = [url_parse(session, row) for row in table.itertuples()]
        resp_list = await asyncio.gather(*tasks)
        return list(zip(resp_list, [row for row in table.itertuples()]))


def insert_data(resp_list):
    monitor_list = []
    for resp, row in resp_list:
        if not db_session.query(Monitoring).filter_by(label=row.label)\
                .count() and resp:
            params = dict(
                timestamp=datetime.now(),
                url=row.url,
                label=row.label,
                response_time=None,
                status_code=resp[0].status,
                content_length=resp[0].content_length
            )
            m = Monitoring(params)
            monitor_list.append(m)
    db_session.add_all(monitor_list)
    db_session.commit()
    return len(monitor_list)


@timewrap
def get_data():
    loop = asyncio.get_event_loop()
    resp_list = loop.run_until_complete(multi_parse(loop))
    added_amount = insert_data(resp_list)
    return len(resp_list), added_amount


if __name__ == "__main__":
    if len(sys.argv) >= 1:
        settings.DEFAULT_EXCEL_FILE = sys.argv[1]
    data, elapsed_time = get_data()
    log_info.info(f"Filename: {settings.DEFAULT_EXCEL_FILE} "
                  f"Fetched: {data[0]} Added: {data[1]} "
                  f"Time: {elapsed_time} ")
