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

    def __init__(self, kwargs):
        self.ts = kwargs['timestamp']
        self.url = kwargs['url']
        self.label = kwargs['label']
        self.response_time = kwargs['response_time']
        self.status_code = kwargs['status_code']
        self.content_length = kwargs['content_length']

    def __str__(self):
        return
