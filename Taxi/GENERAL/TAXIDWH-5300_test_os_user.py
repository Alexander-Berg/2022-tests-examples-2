import os
import pwd
from tempfile import NamedTemporaryFile

print(os.getlogin())
print(pwd.getpwuid(os.getuid()).pw_name)

with NamedTemporaryFile() as f:
    print(f.name)
    print(pwd.getpwuid(os.stat(f.name).st_uid).pw_name)

