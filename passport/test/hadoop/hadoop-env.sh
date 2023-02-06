#
# PASSPADMIN-4476 - включение CMS GC для всего hadoop
#

HADOOP_SERVER_OPTS="-XX:+UseConcMarkSweepGC -XX:+CMSParallelRemarkEnabled"
HADOOP_SERVER_OPTS="${HADOOP_SERVER_OPTS} -XX:+CMSScavengeBeforeRemark -XX:+ScavengeBeforeFullGC"
HADOOP_SERVER_OPTS="${HADOOP_SERVER_OPTS} -XX:+UseCMSInitiatingOccupancyOnly -XX:CMSInitiatingOccupancyFraction=75"
HADOOP_SERVER_OPTS="${HADOOP_SERVER_OPTS} -XX:+UnlockDiagnosticVMOptions -XX:ParGCCardsPerStrideChunk=32768"
HADOOP_SERVER_OPTS="${HADOOP_SERVER_OPTS} -verbose:gc -XX:+PrintGCDateStamps -XX:+PrintGCDetails -XX:+PrintTenuringDistribution -XX:+PrintAdaptiveSizePolicy"
HADOOP_SERVER_OPTS="${HADOOP_SERVER_OPTS} -XX:+UseGCLogFileRotation -XX:NumberOfGCLogFiles=5 -XX:GCLogFileSize=512M"
HADOOP_SERVER_OPTS="${HADOOP_SERVER_OPTS} -XX:NewRatio=5"

export HADOOP_JOURNALNODE_OPTS="${HADOOP_SERVER_OPTS}"
export HADOOP_NAMENODE_OPTS="${HADOOP_SERVER_OPTS}"
export HADOOP_DATANODE_OPTS="${HADOOP_SERVER_OPTS}"
