from passport.infra.daemons.blackbox.config.usernets.network_description_filter import NetworkDescriptionFilter


def test_network_description_uniqueness():
    # ARRANGE
    nets_with_duplicates = {
        "macroname": {
            "192.123.0.1": 30,
            "155.132.7.8": 43,
        },
        "second_macroname": {
            "192.123.0.1": 20,
            "155.132.7.8": 43,
        },
    }

    nets_without_duplicates = {
        "macroname": {
            "192.123.0.1": 30,
            "155.132.7.8": 43,
        },
        "second_macroname": {
            "192.123.0.1": 30,
            "155.132.7.8": 43,
        },
    }

    network_description_filter = NetworkDescriptionFilter()

    # ACT
    sorted_nets = network_description_filter.make_unique_rates(nets_with_duplicates)

    # ASSERT
    # checking changes between different macros in one dictionary if rate is different and the same
    assert sorted_nets == nets_without_duplicates


def test_network_description_good_treat():
    # ARRANGE
    nets_without_duplicates = {
        "macroname": {
            "192.123.0.1": 20,
            "155.132.7.8": 43,
            "195.192.4.8": 3,
        },
        "second_macroname": {
            "115.137.8.9": 63,
            "195.192.4.8": 3,
        },
    }

    network_description_filter = NetworkDescriptionFilter()

    # ACT
    sorted_nets = network_description_filter.make_unique_rates(nets_without_duplicates)

    # ASSERT
    # checking that dictionary with out duplicates doesn't change
    assert sorted_nets == nets_without_duplicates
