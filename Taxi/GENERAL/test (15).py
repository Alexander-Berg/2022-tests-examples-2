from loguru import logger
from business_models import cohorts

import pandas as pd
import sys
from datetime import datetime

today = datetime.today().date()
dm_order_path = '//home/eda-dwh/cdm/order/dm_order/'
dm_order_paths = [dm_order_path + str(month)[:7] for month in pd.date_range('2015-11-01', today, freq='MS')]

from pyspark.sql.functions import col
import pyspark.sql.functions as F
import pyspark.sql.types as T
from pyspark.sql.window import Window
import spyt

import os
os.environ["JAVA_HOME"] = "/usr/local/jdk-11"

with spyt.spark_session(
    driver_memory='4G', 
    spark_conf_args={
        'spark.driver.maxResultSize': '4G',
        'spark.sql.autoBroadcastJoinThreshold': -1
    }
) as spark:

    sdf = spark.read.yt(*dm_order_paths)
    logger.info(sdf.count())