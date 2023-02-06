# generated via tvmknife unittest service -s 200 -d 300 (priority->tags)
TICKET_200_300 = (
    '3:serv:CBAQ__________9_IgYIyAEQrAI:RGXe3QVsvyGEMcOnW4VEqV78XIcLC4XXS7FTy'
    '-iafuLdLR2FY8UmScF7VOCVTh9e3YQfCQ9VsnscVMmdbmiSKDoHZofqGA-rACcc0rdGv9D81'
    'fpualqaL_O6nPEuXtTb7qpxQVjpX1EknAam_FQEKeyEG6KN51rcf4iwgQSsacg'
)

# generated via tvmknife unittest service -s 300 -d 200
TICKET_300_200 = (
    '_3:serv:CBAQ__________9_IgYIrAIQyAE:kqftMeryz0oR__X2DpAGWHga3cFV_y5FmPjY'
    'RASdxB-RY1PgC0aw-YoPQ6ZHU30Ojg07a3EJzWSuJoNdYmpztSiNz4Dn50TXjrDjTsl9CIrU'
    'ugnYYbFFbgrLZR8BmSctwhbObJM37z-IrZgyhM45Lw4kv80MezQ4Xt6r3oazUw'
)

BR_ROOT = 'br_root'
MSK = 'moscow'
SPB = 'spb'
TULA = 'tula'

DEFAULT_ZONES_WHITELIST = {'__default__': True, MSK: True}
DEFAULT_ACCEPT_LANGUAGE = 'en-US, en;q=0.8,ru;q=0.6'
DEFAULT_USER_AGENT = 'Taximeter 9.20 (1234)'
DEFAULT_HEADERS = {
    'Accept-Language': DEFAULT_ACCEPT_LANGUAGE,
    'User-Agent': DEFAULT_USER_AGENT,
}

POLLING_URL = 'v1/polling/priority'
DIAGNOSTICS_URL = 'v1/priority/diagnostics'
SCREEN_URL = 'v1/priority/screen'
VALUE_URL = 'v1/priority/value'
VALUES_URL = 'v1/priority/values'
FLEET_URL = 'fleet/driver-priority/v1/priority/diagnostics'

MSK_COORDS = (37.6, 55.75)
