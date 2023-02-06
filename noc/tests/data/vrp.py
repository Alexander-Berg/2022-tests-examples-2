QUESTION_VARIANTS = [
    b"Info: Reboot system at 17:10:00 2018/03/29 UTC+03:00 (in 0 hours and 49 minutes).\nConfirm? [Y/N]:",
    b"Warning: The current configuration will be written to the device. Continue? [Y/N]:",
    b"Are you sure to continue?[Y/N]",
    b'\nWarning: The file CE6850EI-V200R002C50SPC800.cc already exists. Overwrite it? [Y/N]:',
    b"\nInfo: Please input the file name(*.cfg, *.zip, *.dat):",
    b"Warning: All DHCP functions will be disabled. Continue? [Y/N]",
]

MOTD_VARIANTS = [(b'\r\n'
                  b'Info: The max number of VTY users is 5, the number of current VTY users online is 1, and total number of terminal users online is 1.\r\n'
                  b'      The current login time is 2018-03-29 18:13:55.\r\n'
                  b'      The last login time is 2018-03-29 18:12:36 from 95.108.170.150 through SSH.\r\n')]

COMMAND_ERROR_VARIANTS = [
    b"Error: Unrecognized command found at '^' position.",
    b"Error: No permission to run the command.",
    b"Error: You do not have permission to run the command or the command is incomplete.",
    b"Error: Invalid file name log.",
    b"              ^\r\nError[1]: Unrecognized command found at '^' position.",
    b"              ^\r\nError[2]: Incomplete command found at '^' position.",
]

DATA_READ_CB_VARIANTS = [
    {
        "input": b'port trunk allow-pass vlan 1\r\n\rRunning: 33%\r\rRunning: 33%\r\rRunning: 66%\r\rRunning: 66%\r\r            \x1b[1A\r\n\r\n[*test]',
        "expected": b'port trunk allow-pass vlan 1\n\n[*test]'}
]
