from libstall.util import barcode

def test_barcode_pack(tap):
    with tap.plan(2):
        tap.eq(barcode.pack(0, 1, 2), '2001000000029', 'упаковка')
        tap.eq(barcode.unpack('2001000000029'), (0, 1, 2), 'распаковка')


def test_weigh_pack(tap):
    with tap.plan(2):
        tap.eq(barcode.weight_pack(1, 2),
               '2000001000021',
               'упаковка')
        tap.eq(barcode.weight_unpack('2000001000021'),
               (1, 2, None),
               'распаковка')


def test_weigh_child(tap):
    with tap.plan(2):
        tap.eq(barcode.weight_pack(1, 2, 3),
               '200000100002103',
               'упаковка')
        tap.eq(barcode.weight_unpack('200000100002103'),
               (1, 2, 3),
               'распаковка')
