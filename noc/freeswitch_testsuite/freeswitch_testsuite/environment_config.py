from os import getcwd, makedirs
from os.path import join, exists
from string import Template
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL

LOG_LEVEL = INFO

# PJLib settings
PJ_LOG_LEVEL = 0
LOG_SIP = 0
UAC_PORT: int = 5070
UAS_PORT: int = 5080
UA_BIND_ADDRESS: str = '127.0.0.1'

# ivr-dispatcher mock params
WEB_PORT = 4400
WEB_BIND_ADDRESS = '127.0.0.1'
ACTION_PATH = '/action'
PROMPTS_PATH = '/prompts'
METRICS_PATH = '/metrics'
SYNTH_PATH = '/synth'

# STT/TTS mock params
HTTP_TTS_PORT = 4500
GRPC_STT_PORT = 4600
GRPC_TTS_PORT = 4700
TTS_PORT = 4500
GRPC_PORT = 4600
GRPC_HOST = 'localhost'

# FS params
TS_DISTRIBUTOR = 'uas'
TS_OP_DISTRIBUTOR = 'uas_op'
ESL_PORT = 8021
ESL_PASSWORD = 'testsuite'
MOD_IVRD_PORT = 8090
FS_SIP_PORT = 5060

# FS directories are relative to testsuite CWD
BASE = join(getcwd(), 'fsut')
CACHE = join(BASE, 'prompts')
CONF_DIR = join(BASE, 'config')
LOG_DIR = join(BASE, 'log')
RUN_DIR = join(BASE, 'run')
DB_DIR = join(BASE, 'db')
SOUNDS_DIR = join(BASE, 'sounds')
MOH_DIR = join(SOUNDS_DIR, 'moh')


ENV_VALUES = dict(
    ts_context='world',
    ts_ext='testsuite',
    ts_profile='external',
    ts_sessions=20,
    fs_sip_port=FS_SIP_PORT,
    ts_distributor=TS_DISTRIBUTOR,
    ts_op_distributor=TS_OP_DISTRIBUTOR,
    codec_prefs='L16',
    web_port=WEB_PORT,
    web_bind_address=WEB_BIND_ADDRESS,
    synth_path=SYNTH_PATH,
    metrics_path=METRICS_PATH,
    action_path=ACTION_PATH,
    ua_bind_address=UA_BIND_ADDRESS,
    uac_port=UAC_PORT,
    uas_port=UAS_PORT,
    cache_path=CACHE,
    mod_ivrd_port=MOD_IVRD_PORT,
    esl_port=ESL_PORT,
    esl_password=ESL_PASSWORD,
    grpc_host=GRPC_HOST,
    grpc_port=GRPC_PORT,
    tts_port=TTS_PORT,
    grpc_stt_port=GRPC_STT_PORT,
    grpc_tts_port=GRPC_TTS_PORT,
    http_tts_port=HTTP_TTS_PORT,
    moh_dir=MOH_DIR
)

CONF_TEMPL = Template(
    """<?xml version="1.0"?>
<document type="freeswitch/xml">
    <section name="dialplan" description="Regex/XML Dialplan">
        <context name="$ts_context">
            <extension name="test_ivr_dispatch">
                <condition field="destination_number" expression="^$ts_ext$$">
                    <action application="ivr_dispatch"/>
                </condition>
            </extension>

        </context>
    </section>

    <section name="directory">
    </section>

    <section name="configuration" description="Various Configuration">

        <configuration name="switch.conf" description="Core Configuration">
            <cli-keybindings>
            </cli-keybindings>
            <default-ptimes>
            </default-ptimes>
            <settings>
                <param name="dialplan-timestamps" value="true"/>
                <param name="max-db-handles" value="50"/>
                <param name="db-handle-timeout" value="10"/>
                <param name="max-sessions" value="$ts_sessions"/>
                <param name="sessions-per-second" value="5"/>
                <param name="loglevel" value="debug"/>
                <param name="dump-cores" value="yes"/>
                <param name="rtp-start-port" value="5000"/>
                <param name="rtp-end-port" value="5099"/>
                <param name="event-heartbeat-interval" value="5"/>
            </settings>
        </configuration>

        <configuration name="sofia.conf" description="sofia Endpoint">

            <global_settings>
                <param name="log-level" value="0"/>
                <param name="debug-presence" value="0"/>
            </global_settings>

            <profiles>
                <profile name="$ts_profile">
                    <gateways>
                        <gateway name="ts_uac">
                            <param name="proxy" value="$ua_bind_address:$uac_port;transport=tcp"/>
                            <param name="register" value="false"/>
                            <param name="caller-id-in-from" value="true"/>
                        </gateway>
                        <gateway name="ts_uas">
                            <param name="proxy" value="$ua_bind_address:$uas_port;transport=tcp"/>
                            <param name="register" value="false"/>
                            <param name="caller-id-in-from" value="true"/>
                        </gateway>
                    </gateways>
                    <settings>
                        <param name="debug" value="0"/>
                        <param name="sip-trace" value="no"/>
                        <param name="sip-capture" value="no"/>
                        <param name="rfc2833-pt" value="101"/>
                        <param name="dialplan" value="XML"/>
                        <param name="context" value="$ts_context"/>
                        <param name="dtmf-duration" value="2000"/>
                        <param name="codec-prefs" value="$codec_prefs"/>
                        <param name="hold-music" value="local_stream://moh"/>
                        <param name="rtp-timer-name" value="soft"/>
                        <param name="manage-presence" value="false"/>
                        <param name="user-agent-string" value="Taxi.FS.Testsuite"/>

                        <param name="inbound-codec-negotiation" value="generous"/>
                        <param name="auth-calls" value="false"/>
                        <param name="inbound-late-negotiation" value="true"/>

                        <param name="bind-params" value="transport=tcp"/>
                        <param name="sip-port" value="$fs_sip_port"/>
                        <param name="rtp-ip" value="$ua_bind_address"/>
                        <param name="sip-ip" value="$ua_bind_address"/>
                        <param name="rtp-timeout-sec" value="300"/>
                        <param name="rtp-hold-timeout-sec" value="1800"/>
                        <param name="rtp-rewrite-timestamps" value="true"/>
                    </settings>
                </profile>
            </profiles>
        </configuration>

        <configuration name="ivr_dispatcher.conf" description="Yandex ivr-dispatcher telephony API">
            <settings>
                <param name="debug" value="true"/>
                <param name="api_url" value="http://$web_bind_address:$web_port$action_path"/>
                <param name="api_timeout_sec" value="2"/>
                <param name="api_attempts" value="3"/>
                <param name="web_port" value="$mod_ivrd_port"/>
                <param name="cache_path" value="$cache_path"/>
                <param name="sofia_profile" value="$ts_profile"/>
            </settings>
        </configuration>

         <configuration name="ya_speechkit.conf" description="SpeechKit Cloud Synth">
            <settings>
                <param name="synth_api_url" value="http://$web_bind_address:$http_tts_port$synth_path"/>
                <param name="synth_grpc_api_url" value="$grpc_host:$grpc_tts_port"/>
                <param name="recog_api_url" value="$grpc_host:$grpc_stt_port"/>
                <param name="solomon_agent_url" value="http://$web_bind_address:$web_port$metrics_path"/>
                <param name="api_key" value="SET_ME"/>
                <param name="max_sessions" value="0"/>
                <param name="trace" value="no"/>
            </settings>
        </configuration>

        <configuration name="distributor.conf" description="Distributor Configuration">
            <lists>
                <list name="$ts_distributor">
                    <node name="ts_uas" weight="1"/>
                </list>
                <list name="$ts_op_distributor">
                    <node name="ts_uas" weight="1"/>
                </list>
            </lists>
        </configuration>

        <configuration name="acl.conf" description="Network Lists">
            <network-lists>
                <!-- TODO: fix ACL -->
                <list name="esl_acl" default="allow">
                    <node type="allow" network="0.0.0.0"/>
                    <node type="allow" network="::"/>
                </list>
            </network-lists>
        </configuration>

        <configuration name="event_socket.conf" description="Socket Client">
            <settings>
                <param name="nat-map" value="false"/>
                <param name="listen-ip" value="$ua_bind_address"/>
                <param name="listen-port" value="$esl_port"/>
                <param name="password" value="$esl_password"/>
                <param name="apply-inbound-acl" value="esl_acl"/>
            </settings>
        </configuration>

        <configuration name="local_stream.conf" description="stream files from local dir">
            <directory name="default" path="$moh_dir">
                <param name="rate" value="8000"/>
                <param name="shuffle" value="true"/>
                <param name="channels" value="1"/>
                <param name="interval" value="20"/>
                <param name="timer-name" value="soft"/>
            </directory>
        </configuration>

        <configuration name="http_cache.conf" description="HTTP GET cache">
            <settings>
                <param name="enable-file-formats" value="true"/>
                <param name="max-urls" value="10000"/>
                <param name="location" value="$cache_path"/>
                <param name="default-max-age" value="120"/>
                <param name="prefetch-thread-count" value="8"/>
                <param name="prefetch-queue-size" value="100"/>
                <param name="ssl-cacert" value="$${certs_dir}/cacert.pem"/>
                <param name="ssl-verifypeer" value="false"/>
                <param name="ssl-verifyhost" value="false"/>
            </settings>
            <profiles>
                <profile name="s3">
                    <aws-s3>
                        <access-key-id><![CDATA[<access-key-id>]]></access-key-id>
                        <secret-access-key><![CDATA[<secret-access-key>]]></secret-access-key>
                        <region><![CDATA[us-east-1]]></region>
                        <base-domain><![CDATA[s3.mdst.yandex.net]]></base-domain>
                    </aws-s3>
                    <domains>
                        <domain name="127.0.0.1:4400"></domain>
                    </domains>
                </profile>
            </profiles>
        </configuration>

        <configuration name="console.conf" description="Console Logger">
            <mappings>
                <map name="all" value="console,debug,info,notice,warning,err,crit,alert"/>
            </mappings>
            <settings>
                <param name="colorize" value="true"/>
                <param name="loglevel" value="9"/>
            </settings>
        </configuration>

        <configuration name="logfile.conf" description="File Logging">
            <settings>
                <param name="rotate-on-hup" value="true"/>
            </settings>
            <profiles>
                <profile name="default">
                    <settings>
                        <param name="rollover" value="53687091"/>
                        <param name="maximum-rotate" value="20"/>
                        <param name="uuid" value="true"/>
                    </settings>
                    <mappings>
                        <map name="all" value="console,debug,info,notice,warning,err,crit,alert"/>
                    </mappings>
                </profile>
            </profiles>
        </configuration>

        <configuration name="modules.conf" description="Modules">
            <modules>
                <load module="mod_console"/>
                <load module="mod_logfile"/>
                <load module="mod_cdr_csv"/>
                <load module="mod_event_socket"/>
                <load module="mod_sofia"/>
                <load module="mod_loopback"/>
                <load module="mod_commands"/>
                <load module="mod_dptools"/>
                <load module="mod_dialplan_xml"/>
                <load module="mod_distributor"/>
                <load module="mod_tone_stream"/>
                <load module="mod_native_file"/>
                <load module="mod_sndfile"/>
                <load module="mod_ya_speechkit"/>
                <load module="mod_ivr_dispatcher"/>
                <load module="mod_http_cache"/>
                <load module="mod_tone_stream"/>
                <load module="mod_local_stream"/>
            </modules>
        </configuration>

        <configuration name="post_load_modules.conf" description="Modules">
            <modules>
            </modules>
        </configuration>

        <configuration name="timezones.conf" description="Timezones">
            <timezones>
                <zone name="Etc/GMT" value="GMT0"/>
                <zone name="Etc/GMT+3" value="&lt;GMT+3&gt;3"/>
            </timezones>
        </configuration>
    </section>
</document>""")


def make_moh():
    moh_path: str = join(MOH_DIR, 'moh.r8')
    if not exists(moh_path):
        with open(moh_path, 'wb') as outfile:
            for _ in range(0, 500):
                outfile.write(bytes('MOHMOHMOH', 'utf-8'))
            outfile.flush()


def make_environment():
    makedirs(CONF_DIR, exist_ok=True)
    makedirs(LOG_DIR, exist_ok=True)
    makedirs(DB_DIR, exist_ok=True)
    makedirs(MOH_DIR, exist_ok=True)
    makedirs(RUN_DIR, exist_ok=True)
    make_moh()
    conf_file = join(CONF_DIR, 'freeswitch.xml')
    with open(conf_file, 'w') as out:
        print(CONF_TEMPL.substitute(**ENV_VALUES), file=out)
