from collections import OrderedDict

from sandbox.projects.sandbox_ci.pulse.measure_wizard_weights import measurer

TEST_DATA = {
    'WIZIMAGES': {
        'total_template_time': -2,
        'gzipped_size': -10,
    },
    'WIZVIDEO': {
        'total_template_time': -5,
        'gzipped_size': -18,
    },
    'BNA': {
        'total_template_time': -1,
        'gzipped_size': -50,
    },
    'DRUGS': {
        'total_template_time': 0.01,
        'gzipped_size': 0,
    }
}

REAL_DATA = {
    'WEB_BNA': {'gzipped_size': 0.28561106035786565, 'total_template_time': -0.6282636512096786},
    'COLLECTIONS_BOARD': {'gzipped_size': -0.9262928794178791, 'total_template_time': -2.4927580935550964},
    'WIZIMAGES': {'gzipped_size': -14.652692802459839, 'total_template_time': -5.896721385542165},
    'ENTITY_SEARCH': {'gzipped_size': -27.748314123585388, 'total_template_time': -20.172358238683138},
    'VIDEOWIZ': {'gzipped_size': -3.7540513616967885, 'total_template_time': -6.288128823293178}
}

TEST_WEIGHTS = OrderedDict((
    ('WIZVIDEO', 51),
    ('BNA', 28),
    ('WIZIMAGES', 21),
))


def test_weights_on_test_data():
    res = measurer.measure_weights(TEST_DATA, template_weight=70, size_weight=30)

    assert res == {'BNA': 27.98076923076923,
                   'WIZIMAGES': 21.346153846153847,
                   'WIZVIDEO': 50.67307692307693,
                   'DRUGS': 0.001}


def test_weights_on_real_data():
    res = measurer.measure_weights(REAL_DATA, template_weight=60, size_weight=40)

    assert res == {'COLLECTIONS_BOARD': 5.002669694135656,
                   'ENTITY_SEARCH': 57.68982857521709,
                   'VIDEOWIZ': 13.823761549630305,
                   'WEB_BNA': 1.0625056229772083,
                   'WIZIMAGES': 22.421234558039735}


def test_draw_diagram():
    res = measurer.draw_diagram(TEST_WEIGHTS)

    assert res == """WIZVIDEO\t###################################################
BNA\t############################
WIZIMAGES\t#####################"""
