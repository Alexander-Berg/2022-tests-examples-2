LIBRARY()

VERSION(2.5)

LICENSE(Public Domain)

OWNER(g:python-contrib torkve)

RESOURCE_FILES(
    PREFIX contrib/python/pycrypto/
    .dist-info/METADATA
    .dist-info/top_level.txt
)

SRCDIR(contrib/python/pycrypto/lib/Crypto)

PY_SRCS(
    NAMESPACE Crypto
    __init__.py
    pct_warnings.py
    Cipher/__init__.py
    Cipher/PKCS1_OAEP.py
    Cipher/PKCS1_v1_5.py
    Hash/__init__.py
    Hash/HMAC.py
    Hash/MD2.py
    Hash/MD4.py
    Hash/MD5.py
    Hash/RIPEMD.py
    Hash/SHA224.py
    Hash/SHA256.py
    Hash/SHA384.py
    Hash/SHA512.py
    Hash/SHA.py
    Protocol/__init__.py
    Protocol/AllOrNothing.py
    Protocol/Chaffing.py
    Protocol/KDF.py
    PublicKey/__init__.py
    PublicKey/_DSA.py
    PublicKey/DSA.py
    PublicKey/ElGamal.py
    PublicKey/pubkey.py
    PublicKey/qNEW.py
    PublicKey/_RSA.py
    PublicKey/RSA.py
    PublicKey/_slowmath.py
    Random/__init__.py
    Random/random.py
    Random/_UserFriendlyRNG.py
    Random/Fortuna/__init__.py
    Random/Fortuna/FortunaAccumulator.py
    Random/Fortuna/FortunaGenerator.py
    Random/Fortuna/SHAd256.py
    Random/OSRNG/__init__.py
    Random/OSRNG/fallback.py
    Random/OSRNG/posix.py
    Random/OSRNG/rng_base.py
    Signature/__init__.py
    Signature/PKCS1_PSS.py
    Signature/PKCS1_v1_5.py
    Util/__init__.py
    Util/asn1.py
    Util/Counter.py
    Util/_number_new.py
    Util/number.py
    Util/py21compat.py
    Util/py3compat.py
    Util/randpool.py
    Util/RFC1751.py
    Util/wrapper.py
)

ADDINCL(contrib/python/pycrypto/src/libtom)

SRCS(
    src/MD2.c
    src/MD4.c
    src/SHA224.c
    src/SHA256.c
    src/SHA384.c
    src/SHA512.c
    src/RIPEMD160.c

    src/AES.c
    src/ARC2.c
    src/Blowfish.c
    src/CAST.c
    src/DES.c
    src/DES3.c
    src/ARC4.c
    src/XOR.c

    src/strxor.c
    src/_counter.c

    # src/_fastmath.c  # no mpir or gmp in arcadia
)

PY_REGISTER(
    Crypto.Hash._MD2
    Crypto.Hash._MD4
    Crypto.Hash._SHA224
    Crypto.Hash._SHA256
    Crypto.Hash._SHA384
    Crypto.Hash._SHA512
    Crypto.Hash._RIPEMD160

    Crypto.Cipher.AES
    Crypto.Cipher.ARC2
    Crypto.Cipher.Blowfish
    Crypto.Cipher.CAST
    Crypto.Cipher.DES
    Crypto.Cipher.DES3
    Crypto.Cipher.ARC4
    Crypto.Cipher.XOR

    Crypto.Util.strxor
    Crypto.Util._counter

    # Crypto.PublicKey._fastmath
)

IF (OS_WINDOWS)
    PY_SRCS(
        NAMESPACE Crypto
        Util/winrandom.py
        Random/OSRNG/nt.py
    )
    SRCS(
        src/winrand.c
    )
    LDFLAGS(
        advapi32.lib
        ws2_32.lib
    )
    PY_REGISTER(
        Crupto.Random.OSRNG.winrandom
    )
ENDIF()


NO_COMPILER_WARNINGS()
NO_LINT()

END()
