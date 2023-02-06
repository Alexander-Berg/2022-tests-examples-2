from noc.grad.grad.utils.diag import Test, if_alias, if_hc_out_octets


def test_ifalias_utf8():
    incorrect_string = "тест".encode()[0:-1]
    t = Test("host")
    data = [[if_alias, 1, incorrect_string, 1]]
    t.insert_data(data)
    assert t.analyze(["test_ifalias_utf8"])["test_ifalias_utf8"]


def test_incorrect_reset():
    # NOCDEV-1360
    t = Test("host")
    data = [
        [if_hc_out_octets, 1, 78975858556803, 1],
        [if_hc_out_octets, 1, 78971564031702, 3],
        [if_hc_out_octets, 1, 78971564350521, 5],
    ]
    t.insert_data(data)
    assert t.analyze(["test_counter_reset"])["test_counter_reset"]


def test_correct_reset():
    t = Test("host")
    data = [[if_hc_out_octets, 1, 78975858556803, 1], [if_hc_out_octets, 1, 0, 3], [if_hc_out_octets, 1, 100, 5]]
    t.insert_data(data)
    assert not t.analyze(["test_counter_reset"])["test_counter_reset"]
