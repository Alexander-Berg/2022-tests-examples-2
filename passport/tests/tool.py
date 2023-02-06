#!/usr/bin/python

import sys
import base64
import struct
import Crypto.Random
from Crypto.Cipher import AES
from Crypto.Hash import HMAC

import xml.etree.ElementTree as ET

from passport.infra.daemons.blackbox.src.protobuf import totp_profile_pb2


def load_keys(path):
    keys = {}
    root = ET.parse(path).getroot()

    for elem in root:
        keys[elem.get('id')] = base64.b64decode(elem.text)

    return keys


class TotpTool:
    def __init__(self, keys_dir='/etc/fastcgi2/available/blackbox_keys'):
        self.aes_keys = load_keys(keys_dir + '/totp_aes.keys')
        self.mac_keys = load_keys(keys_dir + '/totp_hmac.keys')

    def __decrypt(self, value):
        output = ''
        output += 'Going to decrypt value %s\n' % value
        fields = value.split(':')
        if len(fields) != 6:
            raise Exception('Incorrect number of fields: "%s"\n' % value)
        version = fields[0]
        if version != '1' and version != '2' and version != '3':
            raise Exception('Unknown format version: %s\n' % str(fields[0]))
        iv = base64.b64decode(fields[3])
        aes_block = base64.b64decode(fields[4])
        mac_block = base64.b64decode(fields[5])

        output += "hex iv : %s\n" % iv.hex()
        # print("hex aes:", aes_block.hex())
        # print("hex mac:", mac_block.hex())

        if version == '1':
            mac = HMAC.new(self.mac_keys[fields[2]], aes_block, Crypto.Hash.SHA256).digest()
        else:
            mac = HMAC.new(
                self.mac_keys[fields[2]], value[: value.rfind(':')].encode('utf-8'), Crypto.Hash.SHA256
            ).digest()

        if mac != mac_block:
            output += "MAC mismatch, your value is invalid!\n"
            return output

        aes = AES.new(self.aes_keys[fields[1]], AES.MODE_CBC, iv)
        block = aes.decrypt(aes_block)

        # unpad decrypted block
        block = block[: -block[-1]]

        output += "plaintext=%s\n" % ' '.join([block.hex()[i : i + 32] for i in range(0, 2 * len(block), 32)])

        return output, version, block

    def __encrypt(self, version, block, iv):
        output = ''
        if not iv:
            rand = Crypto.Random.new().read(AES.block_size)
            output += 'new iv is %s\n' % rand.hex()
            iv = base64.b64encode(rand)  # get random 128 bit IV

        bin_iv = base64.b64decode(iv)

        # add PKCS5 padding
        pad_count = 16 - len(block) % 16
        block += chr(pad_count) * pad_count

        aes_key_id = max(self.aes_keys.iterkeys())
        mac_key_id = max(self.mac_keys.iterkeys())

        aes = AES.new(self.aes_keys[aes_key_id], AES.MODE_CBC, bin_iv)

        output += "plaintext=%s\n" % (' '.join([block.hex()[i : i + 32] for i in range(0, 2 * len(block), 32)]))

        encrypted = aes.encrypt(block)

        output += 'hex aes: %s len= %d' % (encrypted.hex(), len(encrypted))

        # value format is 'version:aes_key_id:mac_key_id:IV:AES:MAC
        value = ':'.join([version, aes_key_id, mac_key_id, iv, base64.b64encode(encrypted)])

        if version == '1':
            mac = HMAC.new(self.mac_keys[mac_key_id], encrypted, Crypto.Hash.SHA256).digest()
        else:
            mac = HMAC.new(self.mac_keys[mac_key_id], value, Crypto.Hash.SHA256).digest()

        output += 'hex mac: %s len= %d\n' % (mac.hex(), len(mac))

        value += ':' + base64.b64encode(mac)

        output += 'Encrypted value is: %s\n' % value
        return output

    def decrypt(self, value):
        output, version, block = self.__decrypt(value)

        if version == '3':
            totp_profile = totp_profile_pb2.TotpProfile()
            try:
                totp_profile.ParseFromString(block)
            except:
                print("TotpProfile protobuf format is broken:", sys.exc_info())
                sys.exit(1)

            output += "Totp profile: \n %s" % str(totp_profile)
            output += "To get a secret for gentotp utility please do: echo -n <pin><secret>|openssl dgst -binary -sha256 |openssl enc -base64 \n"

        else:
            output += 'Decrypted secret is %s, uid=%s\n' % (
                base64.b64encode(block[:16]),
                struct.unpack('<Q', block[16:24])[0],
            )

        return output

    def encrypt(self, uid, secret, iv):
        block = base64.b64decode(secret) + struct.pack('<Q', int(uid))

        return self.__encrypt('2', block, iv)

    def create(self, uid, pin, secret_id, secret, iv, ts):
        totp_profile = totp_profile_pb2.TotpProfile()
        totp_profile.version = 1
        totp_profile.uid = uid
        totp_profile.pin = pin

        s = totp_profile.secrets.add()
        s.id = secret_id
        s.secret = secret
        s.created = ts

        return self.__encrypt('3', totp_profile.SerializeToString(), iv)

    def add(self, secret_id, secret, value, iv, ts):
        output, version, block = self.__decrypt(value)

        if version < 3:
            print("Version of encrypted value is not supported")
            sys.exit(1)

        totp_profile = totp_profile_pb2.TotpProfile()
        try:
            totp_profile.ParseFromString(block)
        except:
            print("TotpProfile protobuf format is broken:", sys.exc_info())
            sys.exit(1)

        s = totp_profile.secrets.add()
        s.id = secret_id
        s.secret = secret
        s.created = ts

        output += self.__encrypt('3', totp_profile.SerializeToString(), iv)
        return output

    def delete(self, secret_id, value, iv):
        output, version, block = self.__decrypt(value)

        if version < 3:
            print("Version of encrypted value is not supported")
            sys.exit(1)

        totp_profile = totp_profile_pb2.TotpProfile()
        try:
            totp_profile.ParseFromString(block)
        except:
            print("TotpProfile protobuf format is broken:", sys.exc_info())
            sys.exit(1)

        for i in range(len(totp_profile.secrets)):
            if totp_profile.secrets[i].id == secret_id:
                del totp_profile.secrets[i]

        output += "Resulting profile: %s" % str(totp_profile)

        output += self.__encrypt('3', totp_profile.SerializeToString(), iv)
        return output
