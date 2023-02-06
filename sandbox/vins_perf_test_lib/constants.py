import sandbox.common.types.client as ctc
from sandbox.common.types.misc import DnsType

# requirements
CLIENT_TAGS = ctc.Tag.Group.LINUX & (ctc.Tag.INTEL_E5_2650 | ctc.Tag.INTEL_E5_2660 | ctc.Tag.INTEL_E5_2660V1 | ctc.Tag.INTEL_E5_2660V4) & ~ctc.Tag.LINUX_LUCID
CORES = 16
DNS = DnsType.DNS64
DISK_SPACE = 250000
RAM = 64 * 1024
PRIVILEGED = True
LIBS = [
    {'package_name': 'startrek_client', 'version': '1.7.0', 'use_wheel': True}
]

# default resources
LXC_CONTAINER = 911872896
TANK_LOAD_CONFIG = 782723570
TANK_MONITORING_CONFIG = 757548823
TANK_AMMO = 1052948970
PYFLAME_BIN = 1000443080
PYFLAME_SCRIPTS = 865006570

# default values
DEFAULT_BASS_URL = 'http://bass.hamster.alice.yandex.net/'
DEFAULT_VINS_URL = 'http://vins.hamster.alice.yandex.net/'
ARCADIA_URL = 'arcadia:/arc/trunk/arcadia'
ARCADIA_REVISION = 'HEAD'
RUN_BASS = False
RUN_VINS = True
LOAD_PROFILE = 'line(10, 16, 10m) const(16, 10m)'
ENV_VARS = 'VINS_DISABLE_SENTRY=1'
PLOT_SENSORS = True
RUN_PYFLAME = False
NUM_OF_RUNS = 1
NO_COMPARISON = False
PYFLAME_SECONDS = 1200
PYFLAME_RATE = 0.1

# filenames
VINS_SENSORS_FILENAME = 'vins_sensors.txt'
MM_SENSORS_FILENAME = 'mm_sensors.txt'
GRAPH_FILENAME = 'graph.html'
VINS_GRAPH_QUANTILES_FILENAME = 'vins_quantiles.svg'
MM_GRAPH_QUANTILES_FILENAME = 'mm_quantiles.svg'
VINS_LOG_FILENAME = 'vins.push_client.out'
VINS_STDOUT_FILENAME = 'stdout_vins.log'
BASS_STDOUT_FILENAME = 'stdout_bass.log'
MEGAMIND_STDOUT_FILENAME = 'stdout_megamind.log'
MEGAMIND_VINS_LIKE_LOGS_FILENAME = 'vins_like_log_megamind.log'
VINS_SENSORS_STATS_FILENAME = 'vins_sensors_stats.json'
MM_SENSORS_STATS_FILENAME = 'mm_sensors_stats.json'

# ports
DEFAULT_VINS_PORT = '8888'
DEFAULT_BASS_PORT = '8898'
DEFAULT_MEGAMIND_PORT = '8908'

# tokens
VAULT_MONGO_PASSWORD_NAME = 'mongo_pass'
VAULT_MONGO_PASSWORD_OWNER = 'VINS'
VAULT_NANNY_TOKEN_NAME = 'robot-voiceint_nanny_token'
VAULT_NANNY_TOKEN_OWNER = 'VINS'
VAULT_ROBOT_BASSIST_NAME = 'robot-bassist_vault_token'
VAULT_ROBOT_BASSIST_OWNER = 'BASS'

RETRY_TIMES_TO_RUN = 5
WAIT_TIME_BETWEEN_TRIES = 120
