import itertools

from django.test import TestCase

from l3mgr.models import RealServer, LocationNetwork
from l3mgr.utils.process_groups import process_groups


class ProcessGroupsTestCase(TestCase):
    ips = ("2a02:68b:b040:3100::/56", "77:88:1:0::/25", "93:158:0:0::/25", "5:255:240:50::/32", "93:158:158:87::/50")

    def setUp(self):
        ln_ch = LocationNetwork.LOCATION_CHOICES
        LocationNetwork.objects.bulk_create(
            LocationNetwork(
                ip=ip,
                location=location,
                source=LocationNetwork.SOURCE_CHOICES.RACKTABLES,
            )
            for ip, location in zip(
                self.ips,
                (
                    [ln_ch.IVA, ln_ch.MYT, ln_ch.SAS],
                    [ln_ch.VLX],
                    [ln_ch.VLA],
                    [ln_ch.MAN],
                    [ln_ch.ASH],
                    [ln_ch.AMS],
                ),
            )
        )

    def test_process_groups_dont_duplicate(self):
        RS_COUNT = 100
        ip_gen = itertools.cycle(self.ips)
        fqdn = list(f"test-real{i}.yandex.net={next(ip_gen)[:-5]}::{i}" for i in range(RS_COUNT))

        # place for check process_groups' speed if you want
        for i in range(10):
            process_groups(fqdn)

        self.assertEqual(RS_COUNT, RealServer.objects.all().count())
