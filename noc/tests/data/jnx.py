from . import (Data, LoginPrompt, ExpectLogin, LoginEcho, PasswordEcho, PasswordPrompt, ExpectPassword, USERNAME,
               PASSWORD, Motd, CommandPrompt, AuthError, ExpectCommand, WriteCommandEcho, WriteCommand, MOCK_COMMAND,
               WriteErrorCommand)


PROMPT_VARIANTS = [
    USERNAME + b"@host-new# "
]

NOPROMPT_VARIANTS = [b"\n</rpc-reply>\n"]


PAGER_VARIANTS = [
    b"\n---(Head of output truncated; more)---",
]

COMMAND_ERROR_VARIANTS = [
    b"syntax error.",
    b"         ^\r\nunknown command.",
    b"    ^\r\nsyntax error, expecting <command>.",
    b"^\r\nInvalid numeric value: 'slow' at 'slow'",
    b"^\r\ninvalid interface type in 'abc-22/22/22'.",
]


class JnxTelnetAuth(Data):
    session = [
        LoginPrompt(b"login: "),
        ExpectLogin(USERNAME + b"\r\n"),
        LoginEcho(USERNAME + b"\r\n"),
        PasswordEcho(b"\r\n"),
        PasswordPrompt(b"Password:"),
        ExpectPassword(PASSWORD + b"\r\n"),
    ]


class JnxTelnetSuccessAuth(JnxTelnetAuth):
    session = [
        Motd(b'Last login: Mon Feb  5 09:49:50 from 127.0.0.1\r\n\r\n'
             b'--- JUNOS 15.1F6.9 Kernel 64-bit  JNPR-10.1-20160616.329709_builder_stable_10\r\n'
             b'Note: Junos is currently running in recovery mode on the OAM volume\r\n'),
        CommandPrompt(USERNAME + b"> ")
    ]


class JnxTelnetAuthFail(JnxTelnetAuth):
    session = [
        AuthError(b'Login incorrect\r\n'),
        LoginPrompt(b"login: "),
        # JnxTelnetAuth.session after this
    ]


class JnxTelnetSuccessCommand(JnxTelnetSuccessAuth):
    session = [
        ExpectCommand(b'show version \r\n'),
        WriteCommandEcho(b'show version \r\n'),
        WriteCommand(b'Model: mx240\r\n'
                     b'Junos: 15.1F6.9\r\n'
                     b'JUNOS OS Kernel 64-bit  [20160616.329709_builder_stable_10]\r\n'
                     b'JUNOS OS libs [20160616.329709_builder_stable_10]\r\n'
                     b'JUNOS OS runtime [20160616.329709_builder_stable_10]\r\n'
                     b'JUNOS OS time zone information [20160616.329709_builder_stable_10]\r\n'
                     b'JUNOS OS libs compat32 [20160616.329709_builder_stable_10]\r\n'
                     b'JUNOS OS 32-bit compatibility [20160616.329709_builder_stable_10]\r\n'
                     b'JUNOS py base [20160701.104257_builder_junos_151_f6]\r\n'
                     b'JUNOS OS crypto [20160616.329709_builder_stable_10]\r\n'
                     b'JUNOS network stack and utilities [20160701.104257_builder_junos_151_f6]\r\n'
                     b'JUNOS modules [20160701.104257_builder_junos_151_f6]\r\n'
                     b'JUNOS libs compat32 [20160701.104257_builder_junos_151_f6]\r\n'
                     b'JUNOS runtime [20160701.104257_builder_junos_151_f6]\r\n'
                     b'JUNOS platform support [20160701.104257_builder_junos_151_f6]\r\n'
                     b'JUNOS libs [20160701.104257_builder_junos_151_f6]\r\n'
                     b'JUNOS mtx Data Plane Crypto Support [20160701.104257_builder_junos_151_f6]\r\n'
                     b'JUNOS daemons [20160701.104257_builder_junos_151_f6]\r\n'
                     b'JUNOS Voice Services Container package [20160701.104257_builder_junos_151_f6]\r\n'
                     b'JUNOS Services SSL [20160701.104257_builder_junos_151_f6]\r\n'
                     b'JUNOS Services Stateful Firewall [20160701.104257_builder_junos_151_f6]\r\n'
                     b'JUNOS Services RPM [20160701.104257_builder_junos_151_f6]\r\n'
                     b'JUNOS Services PTSP Container package [20160701.104257_builder_junos_151_f6]\r\n'
                     b'JUNOS Services NAT [20160701.104257_builder_junos_151_f6]\r\n'
                     b'JUNOS Services Mobile Subscriber Service Container package [20160701.104257_builder_junos_151_f6]\r\n'
                     b'JUNOS Services MobileNext Software package [20160701.104257_builder_junos_151_f6]\r\n'
                     b'JUNOS Services LL-PDF Container package [20160701.104257_builder_junos_151_f6]\r\n'
                     b'JUNOS Services Jflow Container package [20160701.104257_builder_junos_151_f6]\r\n'
                     b'JUNOS Services IPSec [20160701.104257_builder_junos_151_f6]\r\n'
                     b'JUNOS IDP Services [20160701.104257_builder_junos_151_f6]\r\n'
                     b'JUNOS Services HTTP Content Management package [20160701.104257_builder_junos_151_f6]\r\n'
                     b'JUNOS Services Crypto [20160701.104257_builder_junos_151_f6]\r\n'
                     b'JUNOS Services Captive Portal and Content Delivery Container package [20160701.104257_builder_junos_151_f6]\r\n'
                     b'JUNOS Services COS [20160701.104257_builder_junos_151_f6]\r\n'
                     b'JUNOS Border Gateway Function package [20160701.104257_builder_junos_151_f6]\r\n'
                     b'JUNOS AppId Services [20160701.104257_builder_junos_151_f6]\r\n'
                     b'JUNOS Services Application Level Gateways [20160701.104257_builder_junos_151_f6]\r\n'
                     b'JUNOS Services AACL Container package [20160701.104257_builder_junos_151_f6]\r\n'
                     b'JUNOS Packet Forwarding Engine Support (wrlinux) [20160701.104257_builder_junos_151_f6]\r\n'
                     b'JUNOS Packet Forwarding Engine Support (MX/EX92XX Common) [20160701.104257_builder_junos_151_f6]\r\n'
                     b'JUNOS Packet Forwarding Engine Support (M/T Common) [20160701.104257_builder_junos_151_f6]\r\n'
                     b'JUNOS Online Documentation [20160701.104257_builder_junos_151_f6]\r\n'
                     b'JUNOS FIPS mode utilities [20160701.104257_builder_junos_151_f6]\r\n\r'),
        CommandPrompt(USERNAME + b"> ")
    ]


class JnxTelnetSuccessLongCommand(Data):
    # terminal width = 55
    session = [
        CommandPrompt(USERNAME + b"@hostname> "),
        ExpectCommand(b'show interfaces et-0/0/1 | match index\n'),
        WriteCommandEcho(b'show'),
        WriteCommandEcho(b' interfaces'),
        WriteCommandEcho(b' et-0/0/1'),
        WriteCommandEcho(b' |'),
        WriteCommandEcho(b' mat\r'),
        WriteCommandEcho(USERNAME + b'@hostname> ...et-0/0/1 | matc               \x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08h index '),
        WriteCommandEcho(b'\r\n'),

        WriteCommand(b'  Interface index: 725, SNMP ifIndex: 802\r\n'
                     b'  Logical interface et-0/0/1.0 (Index 633) (SNMP ifIndex 607)\r\n'
                     b'\r\n'),
        CommandPrompt(USERNAME + b"@hostname> ")
    ]


class JnxTelnetMockCommand(JnxTelnetSuccessAuth):
    session = [
        ExpectCommand(MOCK_COMMAND + b'\r\n'),
        WriteCommandEcho(MOCK_COMMAND + b'\r\n'),
        WriteErrorCommand(b'         ^\r\nunknown command.\n\n'),
        CommandPrompt(USERNAME + b"> ")
    ]


class JnxTelnetCompleteOnSpaceEcho(JnxTelnetSuccessAuth):
    # Juniper complete-on-space CLI feature
    session = [
        ExpectCommand(b'sho ver | mat NEVER\r\n'),
        WriteCommandEcho(b'show version | match NEVER \r\n'),
        CommandPrompt(USERNAME + b"> ")
    ]


class JnxTelnetPager(JnxTelnetSuccessAuth):
    # screen width = 10
    session = [
        ExpectCommand(b'help topic interfaces mtu-protocol\r\n'),
        WriteCommandEcho(b'help topic interfaces mtu-protocol\r\n'),
        WriteCommand(b'Setting the Protocol MTU\r\n'),
        WriteCommand(b'\r\n'
                     b'   When you initially configure an interface, the protocol maximum\r\n'
                     b'   transmission unit (MTU) is calculated automatically. If you subsequently\r\n'
                     b'   change the media MTU, the protocol MTU on existing address families\r\n'
                     b'   automatically changes.\r\n\r\n'
                     b'   For a list of default protocol MTU values, see Configuring the Media MTU.\r\n\r\n'
                     b'---(more)---'),
        ExpectCommand(b' '),
        WriteCommand(b'\r\x00                                        \r\x00'
                     b'   To modify the MTU for a particular protocol family, include the mtu\r\n'
                     b'   statement:\r\n\r\n'),
        WriteCommand(b'   mtu bytes;\r\n\r\n'
                     b'   You can include this statement at the following hierarchy levels:\r\n\r\n'
                     b'     * [edit interfaces interface-name unit logical-unit-number family\r\n'
                     b'       family]\r\n'
                     b'---(more 40%)---'),
        ExpectCommand(b' '),
        WriteCommand(b'\r\x00                                        \r\x00'
                     b'     * [edit logical-systems logical-system-name interfaces interface-name\r\n'
                     b'       unit logical-unit-number family family]\r\n\r\n'),
        WriteCommand(b'   If you increase the size of the protocol MTU, you must ensure that the\r\n'
                     b'   size of the media MTU is equal to or greater than the sum of the protocol\r\n'
                     b'   MTU and the encapsulation overhead. For a lift of encapsulation overhead\r\n'
                     b'   values, see Configuring the Media MTU. If you reduce the media MTU size,\r\n'
                     b'   but there are already one or more address families configured and active\r\n'
                     b'   on the interface, you must also reduce the protocol MTU size. (You\r\n'
                     b'---(more 60%)---'),
        ExpectCommand(b' '),
        WriteCommand(b'\r\x00                                        \r\x00'
                     b'   configure the media MTU by including the mtu statement at the [edit\r\n'
                     b'   interfaces interface-name] hierarchy level, as discussed in Configuring\r\n'
                     b'   the Media MTU.)\r\n'),
        WriteCommand(b'\r\n'
                     b'          +---------------------------------------------------------+\r\n'
                     b'          || Note: Changing the media MTU or protocol MTU causes an |\r\n'
                     b'          || interface to be deleted and added again.               |\r\n'
                     b'          +---------------------------------------------------------+\r\n\r\n'
                     b'---(more 80%)---'),
        ExpectCommand(b' '),
        WriteCommand(b'\r\x00                                        \r\x00'
                     b'   The maximum number of data-link connection identifiers (DLCIs) is\r\n'
                     b'   determined by the MTU on the interface. If you have keepalives enabled,\r\n'),
        WriteCommand(b'   the maximum number of DLCIs is 1000, with the MTU set to 5012.\r\n\r\n'
                     b'   The actual frames transmitted also contain cyclic redundancy check (CRC)\r\n'
                     b'   bits, which are not part of the MTU. For example, the default protocol MTU\r\n'
                     b'   for a Gigabit Ethernet interface is 1500 bytes, but the largest possible\r\n'
                     b'   frame size is actually 1504 bytes; you need to consider the extra bits in\r\n'
                     b'   calculations of MTUs for interoperability.\r\n'
                     b'---(more 100%)---'),
        ExpectCommand(b' '),
        WriteCommand(b'\r\x00                                        \r\x00\r\n'),
        CommandPrompt(USERNAME + b"> ")
    ]
