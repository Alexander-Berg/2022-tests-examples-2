import pjsua2 as pj
from freeswitch_testsuite.environment_config import (
    UAS_PORT, UAC_PORT, UA_BIND_ADDRESS, PJ_LOG_LEVEL, LOG_SIP)
from freeswitch_testsuite.sip_profile import SipProfile
from freeswitch_testsuite.sip_call import SipCall

__all__ = [
    'B2BUA',
]


# An abstraction over PJSUA2 library
# Manages Transports, SipProfiles
# Is responsive for library configuration,
# creation and destruction of the library
# and their children.
# Library creates couple of threads, running
# PJSIP stack. Stack talks to outer world
# via callbacks (See SipCall, SipProfile).
class B2BUA(pj.Endpoint):
    def __init__(self, loop):
        super().__init__()
        self.loop = loop
        self.libCreate()
        self.libInit(self.make_endpoint_config())
        self.audDevManager().setNullDev()
        self.codecSetPriority('L16/8000/1', 1)
        self.uac_account: SipProfile = self.make_account('initiator', UAC_PORT)
        self.uas_account: SipProfile = self.make_account('responder', UAS_PORT)
        self.libStart()

    def make_outgoing(self) -> SipCall:
        return self.uac_account.make_outgoing()

    async def get_uas_incoming(self) -> SipCall:
        return await self.uas_account.incoming_future

    async def get_uac_incoming(self) -> SipCall:
        return await self.uac_account.incoming_future

    def stop(self) -> None:
        del self.uac_account
        del self.uas_account
        self.loop = None

    def reset(self):
        self.uac_account.reset()
        self.uas_account.reset()

    def make_endpoint_config(self) -> pj.EpConfig:
        ep_cfg: pj.EpConfig = pj.EpConfig()
        ep_cfg.uaConfig = self.make_ua_config()
        ep_cfg.medConfig = self.make_media_config()
        ep_cfg.logConfig = self.make_log_config()
        return ep_cfg

    def make_tcp_transport(self, port: int) -> int:
        tp_config: pj.TransportConfig = pj.TransportConfig()
        tp_config.port = port
        tp_config.boundAddress = UA_BIND_ADDRESS
        return self.transportCreate(
            pj.PJSIP_TRANSPORT_TCP, tp_config)

    def make_account(self, role: str, port: int) -> SipProfile:
        transport_id = self.make_tcp_transport(port)
        t_info: pj.TransportInfo = self.transportGetInfo(transport_id)
        acc_cfg: pj.AccountConfig = pj.AccountConfig()
        acc_cfg.sipConfig.transportId = transport_id
        acc_cfg.idUri = f'sip:{role}@{t_info.localAddress}' \
                        f';transport={t_info.typeName}'
        acc: SipProfile = SipProfile(self.loop, role)
        acc.create(acc_cfg)
        return acc

    @staticmethod
    def make_media_config() -> pj.MediaConfig:
        media_config: pj.MediaConfig = pj.MediaConfig()
        media_config.clockRate = 8000
        media_config.noVad = True
        media_config.ecTailLen = 0
        media_config.channelCount = 1
        media_config.threadCnt = 2
        media_config.hasIoqueue = True
        media_config.sndAutoCloseTime = -1
        media_config.jbInit = 0
        media_config.jbMinPre = 0
        media_config.jbMaxPre = 0
        media_config.jbMax = 0
        media_config.sndRecLatency = 0
        media_config.sndPlayLatency = 0
        media_config.audioFramePtime = 20
        return media_config

    @staticmethod
    def make_ua_config() -> pj.UaConfig:
        ua_config: pj.UaConfig = pj.UaConfig()
        ua_config.maxCalls = 3
        ua_config.threadCnt = 1
        ua_config.mainThreadOnly = False
        ua_config.userAgent = "PJSUA2-Testsuite"
        return ua_config

    @staticmethod
    def make_log_config() -> pj.LogConfig:
        log_config: pj.LogConfig = pj.LogConfig()
        log_config.consoleLevel = PJ_LOG_LEVEL
        log_config.msgLogging = LOG_SIP
        return log_config
