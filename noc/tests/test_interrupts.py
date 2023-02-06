import json
from random import randint

from interrupts import check_interrupts
from tt_main.constants import CRIT_STATUS, OK_STATUS, WARN_STATUS


def gen_interrupt_data(interfaces=1,
                       queues=32,
                       min_rand=5000,
                       max_rand=300000,
                       int_prefix="eth"):
    """Generates dictionary, which values resemble '/proc/interrupts' file for
    mocking purpose. It will be filled with requested number of interfaces,
    queues and random number of interrupts.
    Arguments:
        * interfaces (defaults to 1) - number of interfaces to generate
            interrupts data for.
        * queues (defaults to 32) - number of queues enabled on an interface
        * min_rand (defaults to 5000) - minimum limit for random range
        * max_rand (defaults to 300000) - maximum limit for random range, range
            will be used to generate random interrupt number
        * int_prefix (defaults to 'eth') - prefix to generate interface names,
            so they will be looked like 'eth0', 'eth1', 'eth2', etc...
    Returns: dictionary with following format:
        {'INDEX0': {'CPU0': 'X', 'CPUN': 'Y', 'description': 'DESCR'},
        {'INDEXN': ...
     Where:
        * INDEX0, INDEXN - integer index of IRQ, to which interface-queue
            pair binded
        * CPU0, CPUN - string, which identify CPU core, i.e. CPU0, CPU10
        * description - IRQ description of form design by kernel (or driver?);
            this function supports Intel and Mellanox NICs"""
    interrupt_data = {}
    if queues > 49:
        raise ValueError("Can work with 49 queues max")
    for int_num in range(0, interfaces):
        for queue in range(0, queues):
            if int_prefix == "eth":
                interface_descr = "PCI-MSI 524295-edge eth%d-TxRx-%d" % (
                    int_num, queue)
            elif int_prefix == "mlx":
                interface_descr = "mlx5_comp%d@pci:0000:8%d:00.0" % (queue,
                                                                     int_num)
            cores_list = ["CPU" + str(x) for x in range(0, queues)]
            interrupts_hit = ["0" for x in range(0, queues)]
            interrupts_hit[queue] = str(randint(min_rand, max_rand))
            interrupt_data[str(100 + (int_num * 50) + queue)] = dict(
                zip(cores_list, interrupts_hit))
            interrupt_data[str(100 + (int_num * 50) +
                               queue)]["description"] = interface_descr
    return interrupt_data


def test_interrupts_hit_rise_on_same_core_one_interface_ok():
    prev_interrupt_data = gen_interrupt_data(max_rand=20000)
    new_interrupt_data = gen_interrupt_data(min_rand=20100)
    with open("/tmp/monitoring_check_interrupts.prev", "w") as wfd:
        json.dump(prev_interrupt_data, wfd)
    status, msg = check_interrupts(new_interrupt_data)
    assert msg == "OK"
    assert status == OK_STATUS


def test_interrupts_hit_rise_on_same_core_two_interfaces_ok():
    prev_interrupt_data = gen_interrupt_data(interfaces=2, max_rand=20000)
    new_interrupt_data = gen_interrupt_data(interfaces=2, min_rand=20100)
    with open("/tmp/monitoring_check_interrupts.prev", "w") as wfd:
        json.dump(prev_interrupt_data, wfd)
    status, msg = check_interrupts(new_interrupt_data)
    assert msg == "OK"
    assert status == OK_STATUS


def test_interrupts_did_not_rise_for_one_queue():
    prev_interrupt_data = gen_interrupt_data(interfaces=1, max_rand=20000)
    new_interrupt_data = gen_interrupt_data(interfaces=1, min_rand=20100)
    new_interrupt_data["105"]["CPU5"] = prev_interrupt_data["105"]["CPU5"]
    with open("/tmp/monitoring_check_interrupts.prev", "w") as wfd:
        json.dump(prev_interrupt_data, wfd)
    status, msg = check_interrupts(new_interrupt_data)
    assert "was not changed" in msg
    assert status == CRIT_STATUS


def test_interrupt_core_not_exist_in_prev_state():
    prev_interrupt_data = gen_interrupt_data(interfaces=1, max_rand=20000)
    new_interrupt_data = gen_interrupt_data(interfaces=1, min_rand=20100)
    new_interrupt_data["131"]["CPU32"] = "8214"
    with open("/tmp/monitoring_check_interrupts.prev", "w") as wfd:
        json.dump(prev_interrupt_data, wfd)
    status, msg = check_interrupts(new_interrupt_data)
    assert "irq 131, key CPU32 not exists in prev state" in msg
    assert status == CRIT_STATUS


def test_interrupt_data_became_longer():
    prev_interrupt_data = gen_interrupt_data(interfaces=1, max_rand=20000)
    new_interrupt_data = gen_interrupt_data(interfaces=1, min_rand=20100)
    new_interrupt_data["132"] = {"CPU0": "5000", "CPU1": "8000"}
    with open("/tmp/monitoring_check_interrupts.prev", "w") as wfd:
        json.dump(prev_interrupt_data, wfd)
    status, msg = check_interrupts(new_interrupt_data)
    assert "different data len" in msg
    assert status == CRIT_STATUS


def test_interrupt_data_different_keys():
    prev_interrupt_data = gen_interrupt_data(interfaces=1, max_rand=20000)
    new_interrupt_data = gen_interrupt_data(interfaces=1, min_rand=20100)
    del new_interrupt_data["105"]
    new_interrupt_data["132"] = {"CPU0": "5000", "CPU1": "8000"}
    with open("/tmp/monitoring_check_interrupts.prev", "w") as wfd:
        json.dump(prev_interrupt_data, wfd)
    status, msg = check_interrupts(new_interrupt_data)
    assert "irq 132 not exists in prev state" in msg
    assert status == CRIT_STATUS


def test_interrupts_hit_rise_on_same_core_two_mlx_interfaces_ok():
    prev_interrupt_data = gen_interrupt_data(interfaces=2,
                                             max_rand=20000,
                                             int_prefix="mlx")
    new_interrupt_data = gen_interrupt_data(interfaces=2,
                                            min_rand=20100,
                                            int_prefix="mlx")
    with open("/tmp/monitoring_check_interrupts.prev", "w") as wfd:
        json.dump(prev_interrupt_data, wfd)
    status, msg = check_interrupts(new_interrupt_data)
    assert msg == "OK"
    assert status == OK_STATUS


def test_interrupts_negative_delta_is_ok():
    prev_interrupt_data = gen_interrupt_data(interfaces=2, max_rand=20000)
    new_interrupt_data = gen_interrupt_data(interfaces=2, min_rand=20100)
    new_interrupt_data["108"]["CPU8"] = "4900"
    with open("/tmp/monitoring_check_interrupts.prev", "w") as wfd:
        json.dump(prev_interrupt_data, wfd)
    status, msg = check_interrupts(new_interrupt_data)
    assert msg == "OK"
    assert status == OK_STATUS


def test_interrupts_on_too_few_cores():
    prev_interrupt_data = gen_interrupt_data(interfaces=1,
                                             queues=8,
                                             max_rand=20000)
    new_interrupt_data = gen_interrupt_data(interfaces=1,
                                            queues=8,
                                            min_rand=20100)
    for i in range(3, 8):
        new_interrupt_data[str(100 + i)]["CPU" + str(i)] = 500
    with open("/tmp/monitoring_check_interrupts.prev", "w") as wfd:
        json.dump(prev_interrupt_data, wfd)
    status, msg = check_interrupts(new_interrupt_data)
    assert "detected interrupt only on 3 CPUs" in msg
    assert status == CRIT_STATUS
