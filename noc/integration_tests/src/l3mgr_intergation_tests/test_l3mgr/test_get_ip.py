from multiprocessing.dummy import Pool as ThreadPool
import urllib3

from ..core.client import L3mgrSimpleClient


# Disable annoying ssl certificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ABC_SERVICE = "slb"


def test_ips_not_overlapping_on_get_ip_call():
    """
    Making parallel getip requests and check that allocated IPs are not overlapping
    """

    num_workers = 4

    with ThreadPool(num_workers) as pool:
        future_results = []

        for _ in range(num_workers):
            future_results.append(pool.apply_async(L3mgrSimpleClient.get_ip, args=(ABC_SERVICE,)))

        results = [f.get()["object"] for f in future_results]

    assert len(results) == len(set(results))
