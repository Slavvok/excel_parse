from conn import Base
from sqlalchemy import Column, Integer, Float, String, TIMESTAMP


class Monitoring(Base):
    __tablename__ = 'monitoring'

    id = Column(Integer, primary_key=True)
    ts = Column(TIMESTAMP, nullable=True)
    url = Column(String, nullable=False)
    label = Column(String, nullable=False)
    response_time = Column(Float)
    status_code = Column(Integer, default=None)
    content_length = Column(Integer, default=None)

    def __init__(self, ts, url, label, response_time, status_code, content_length):
        self.ts = ts
        self.url = url
        self.label = label
        self.response_time = response_time
        self.status_code = status_code
        self.content_length = content_length
