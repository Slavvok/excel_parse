from conn import db_session, init_db
from models import *
from datetime import datetime
import settings
import pandas as pd
import requests
import sys
import logging.config
import inspect

logging.config.dictConfig(settings.dictConfig)
logger1 = logging.getLogger("scriptLogger")
logger2 = logging.getLogger("errorLogger")
_ = settings.ExceptionLogging


def insert_data(resp_list):
    monitor_list = []
    for resp, data in resp_list:
        if not db_session.query(Monitoring).filter_by(label=data.label)\
                .count():
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


def get_data():
    r = pd.read_excel(settings.DEFAULT_EXCEL_FILE, index_col=None)
    r = r[r.fetch == 1]
    resp_list = []
    added_amount = 0
    for index, data in r.iterrows():
        try:
            res = requests.get(data.url, timeout=settings.TIMEOUT)
            resp_list.append((res, data))
        except requests.exceptions.RequestException as e:
            stack_info = inspect.stack()
            logger2.error(_(datetime.now(), e, data.url, stack_info))
    if resp_list:
        added_amount = insert_data(resp_list)
    logger1.info(f"Filename: {settings.DEFAULT_EXCEL_FILE} "
                 f"Fetched: {len(r)}. Added: {added_amount}")


if __name__ == "__main__":
    if len(sys.argv) >= 1:
        settings.DEFAULT_EXCEL_FILE = sys.argv[1]
    get_data()
