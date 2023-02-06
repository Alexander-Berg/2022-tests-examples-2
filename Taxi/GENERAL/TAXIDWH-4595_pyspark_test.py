from ytspark import submit_python

from connection.yt import get_yt_path_with_prefix
from init_py_env import settings

if __name__ == '__main__':
    token = settings('yt.yt_token')
    cluster = settings('yt.default_cluster') + ".yt.yandex.net"

    main_py_path = get_yt_path_with_prefix("etl/scala/test_main.py")
    py_zip = get_yt_path_with_prefix("etl/scala/test.zip")
    discovery_dir = "//home/taxi-dwh-dev/unstable/etl/scala/spark-discovery"
    log_dir = "//home/taxi-dwh-dev/unstable/etl/scala/spark-discovery/logs/test"

    submit_python(spark_id="test", discovery_dir=discovery_dir, log_dir=log_dir,
                  yt_proxy=cluster, yt_user="robot-taxi-stat", yt_token=token,
                  spark_home="/usr/lib/yandex/spark", deploy_mode="cluster",
                  spark_conf={
                      "spark.cores.max": "4",
                      "spark.executor.memory": "6G"
                  },
                  main_py_path="yt:/{}".format(main_py_path),
                  py_files="yt:/{}".format(py_zip),
                  job_args={})
