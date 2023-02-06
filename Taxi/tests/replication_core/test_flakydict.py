from replication_core.flakydict import core


def test_flakydict():
    layers = _setup()

    layer3 = layers['layer3']
    assert layer3.get('cfg_id') == {'value': '/abc3/', 'extra': 100}
    layer4 = layer3.create_child({'cfg_id': {'value': '/update/'}})
    assert layer4.get('cfg_id') == {'value': '/update/', 'extra': 100}
    assert layer4.get('cfg_id') == layer4['cfg_id']
    assert dict(layer4.items()) == {
        'cfg_id': {'value': '/update/', 'extra': 100},
    }

    assert layers['layer4']['cfg_id'] == {'value': '/abc3/', 'extra': 200}


def _setup():
    cfg1 = {'cfg_id': {'value': '/abc/'}}
    cfg2 = {'cfg_id': {'value': '/abc2/', 'extra': 100}}
    cfg3 = {'cfg_id': {'value': '/abc3/'}}
    cfg4 = {'cfg_id': {'extra': 200}}

    layer1 = core.FlakyDict(cfg1)
    layer2 = layer1.create_child(cfg2)
    layer3 = layer2.create_child(cfg3)
    layer4 = layer3.create_child(cfg4)

    layers = {
        'layer1': layer1,
        'layer2': layer2,
        'layer3': layer3,
        'layer4': layer4,
    }

    assert layers['layer1']['cfg_id'] == {'value': '/abc/'}
    assert layers['layer2']['cfg_id'] == {'value': '/abc2/', 'extra': 100}
    assert layers['layer3']['cfg_id'] == {'value': '/abc3/', 'extra': 100}
    assert layers['layer4']['cfg_id'] == {'value': '/abc3/', 'extra': 200}
    return layers
