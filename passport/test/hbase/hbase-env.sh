#
# PASSPADMIN-4476 - включение CMS GC для всего hbase
#

HBASE_SERVER_OPTS="-XX:+UseConcMarkSweepGC -XX:+CMSParallelRemarkEnabled"
HBASE_SERVER_OPTS="${HBASE_SERVER_OPTS} -XX:+CMSScavengeBeforeRemark -XX:+ScavengeBeforeFullGC"
HBASE_SERVER_OPTS="${HBASE_SERVER_OPTS} -XX:+UseCMSInitiatingOccupancyOnly -XX:CMSInitiatingOccupancyFraction=75"
HBASE_SERVER_OPTS="${HBASE_SERVER_OPTS} -XX:+UnlockDiagnosticVMOptions -XX:ParGCCardsPerStrideChunk=32768"
HBASE_SERVER_OPTS="${HBASE_SERVER_OPTS} -verbose:gc -XX:+PrintGCDateStamps -XX:+PrintGCDetails -XX:+PrintTenuringDistribution -XX:+PrintAdaptiveSizePolicy"
HBASE_SERVER_OPTS="${HBASE_SERVER_OPTS} -XX:+UseGCLogFileRotation -XX:NumberOfGCLogFiles=5 -XX:GCLogFileSize=512M"

# survivor space size = -Xmn / (SurvivorRatio + 2), default 8 (s0 = -Xmn / 10)
HBASE_SERVER_OPTS="${HBASE_SERVER_OPTS} -XX:-UseAdaptiveSizePolicy -XX:SurvivorRatio=3"

export HBASE_MASTER_OPTS="${HBASE_SERVER_OPTS} -Xmn128m -Xms512m -Xmx512m"
export HBASE_REGIONSERVER_OPTS="${HBASE_SERVER_OPTS} -Xmn512m -Xms8g -Xmx8g"
export HBASE_THRIFT_OPTS="${HBASE_SERVER_OPTS} -Xms1g -Xmx1g"
