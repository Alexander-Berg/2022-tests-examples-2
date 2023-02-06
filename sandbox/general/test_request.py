# -*- coding: utf-8 -*-

from sandbox.projects.geosuggest.component.request import stabilize, set_experiments


def test():
    assert stabilize('/suggest?text=привет') == '/suggest?text=привет&timeout=1000000000'
    assert stabilize('/suggest?timeout=1&aba=caba') == '/suggest?timeout=1000000000&aba=caba'
    assert stabilize('/?timeout&aba=caba&&k=v') == '/?timeout=1000000000&aba=caba&&k=v'
    assert stabilize('/?timeouts=yes&aba=caba') == '/?timeouts=yes&aba=caba&timeout=1000000000'
    assert stabilize('/?k=v&v=1&k=v', 'v=2') == '/?k=v&v=2&k=v&timeout=1000000000'
    assert stabilize('/suggest?part=aba&v=9&k=v', 'v=0&ms=1=1') == '/suggest?part=aba&v=0&k=v&timeout=1000000000&ms=1%3D1'


def test_experiments():
    assert set_experiments('/suggest?aba=caba', [111]) == '/suggest?aba=caba&exprt=111'
    assert set_experiments('/suggest?exprt=123&aba=caba&experimental_exprt=364', [456, 789]) == '/suggest?aba=caba&exprt=456%2C789'
    assert set_experiments('/suggest?aba=caba&experimental_exprt=100', []) == '/suggest?aba=caba'
