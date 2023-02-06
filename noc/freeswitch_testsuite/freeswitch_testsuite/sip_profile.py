import pjsua2 as pj
from asyncio import AbstractEventLoop, Future
from freeswitch_testsuite.sip_call import SipCall
from freeswitch_testsuite.logs import log_debug


# An abstraction over PJSIP Account
# Currently handles just one call per one
# SipProfile instance (self.call).
# Creates SIP socket and listens to INVITEs
# On incoming call creates a SipCall instance
# associated with a particular PJSIP Call.
# After that a callback will be executed.
# On outgoing call creates a SipCall instance
# without association and passes it to pjlib.
# Pjlib creates PJSIP Call (new INVITE session)
# and establishes association with a SipCall instance.
class SipProfile(pj.Account):
    def __init__(self, loop: AbstractEventLoop, role: str):
        super(SipProfile, self).__init__()
        self.role: str = role
        self.loop: AbstractEventLoop = loop
        self.call: SipCall = None
        self.incoming_future: Future = Future()

    def __del__(self):
        del self.call
        self.call = None
        self.loop = None
        self.shutdown()
        log_debug(f'{self.__class__.__name__} deleted')

    # Destructs call, removes association, resets future
    def reset(self):
        del self.call
        self.call = None
        self.incoming_future = Future()

    def make_outgoing(self) -> SipCall:
        # Since outgoing -- no call_id provided
        self.call = SipCall(self.role, self.loop, self)
        # A SipCall with a new callId will be returned
        return self.call

    def onIncomingCall(self, prm: pj.OnIncomingCallParam):
        log_debug(f'{self.role}: Incoming call. callId:[{prm.callId}]')
        self.call = SipCall(self.role, self.loop, self, call_id=prm.callId)
        # Someone may be waiting for this event
        # A SipCall instance is provided along.
        self.incoming_future.set_result(self.call)

