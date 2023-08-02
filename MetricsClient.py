#%%
import os, time
from abc import ABC, abstractmethod
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

url="http://localhost:8086"
token='token-api'
org="FairPrice"
bucket="Propiedades"

# Abstract base class for writing points to InfluxDB
class PointWriter(ABC):
  @abstractmethod
  def write_point(self, point):
    pass

# Concrete implementation of PointWriter using InfluxDBClient
class InfluxWriter(PointWriter):
  def __init__(self, client, write_api, bucket):
    self.client = client
    self.write_api = write_api
    self.bucket = bucket

  def write_point(self, point):
    self.write_api.write(bucket=self.bucket, org=org, record=point)

# Helper function to create a point object from a value
class MetricsClient:
    def __init__(self):
        self.client = InfluxDBClient(url=url, token=token, org=org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.writer = InfluxWriter(self.client, self.write_api, bucket)

    def send_metrics(self, measurement_name:str, tags:dict, fields:dict ):
          point = self.create_point(measurement_name, tags, fields)
          self.writer.write_point(point)

    @staticmethod
    def create_point(measurement_name:str, tags:dict, fields:dict) -> Point:
        point = Point(measurement_name)
        for tag_name, tag_value in tags.items():
            point = point.tag(tag_name, tag_value)
        for field_name, field_value in fields.items():
            field_value = float(field_value) if (isinstance(field_value, int) or isinstance(field_value, float)) else field_value
            point = point.field(field_name, field_value)
        return point
    
#%%
import threading
import time
metrics = MetricsClient()

def metrics_sample(tags:dict, fields:dict) -> None:
  for _ in range(20):
      metrics.send_metrics('test', tags=tags, fields=fields)
      time.sleep(2) # separate points by 1 second

tags={'site': 'argen-prop-test', 'subzone1': 'GBA Norte', 'subzone2': 'Vicente Lopez'}
fields={'recuento': 30}

tags2={'site': 'argen-prop-test', 'subzone1': 'GBA Norte', 'subzone2': 'Tigre'}
fields2={'recuento': 20}

thread = threading.Thread(target= metrics_sample, args=(tags, fields))
thread.start()
time.sleep(10)
thread = threading.Thread(target= metrics_sample, args=(tags2, fields2))
thread.start()