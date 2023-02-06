# -*- coding: utf-8 -*-
from nose.tools import (
    assert_is_none,
    eq_,
    ok_,
    raises,
)
from passport.backend.core.test.test_utils import PassportTestCase
from passport.backend.core.types.display_name import DisplayName


class TestDisplayName(PassportTestCase):
    def setUp(self):
        self.display_name = DisplayName()

    def test_passport_set(self):
        self.display_name.set('p:123')
        eq_(self.display_name.is_passport, True)
        eq_(self.display_name.is_social, False)
        eq_(self.display_name.is_template, False)
        eq_(self.display_name.name, '123')

    def test_social_set(self):
        self.display_name.set('s:1:fb:123')
        eq_(self.display_name.is_passport, False)
        eq_(self.display_name.is_social, True)
        eq_(self.display_name.is_template, False)
        eq_(self.display_name.name, '123')
        eq_(self.display_name.profile_id, 1)
        eq_(self.display_name.provider, 'fb')

    def test_template_set(self):
        self.display_name.set('t:%login%')
        eq_(self.display_name.is_passport, False)
        eq_(self.display_name.is_social, False)
        eq_(self.display_name.is_template, True)
        eq_(self.display_name.name, '%login%')

    def test_passport_serialize(self):
        display_name = DisplayName('100500')
        eq_(str(display_name), 'p:100500')

    def test_social_serialize(self):
        display_name = DisplayName('100500', 'fb', 1)
        eq_(str(display_name), 's:1:fb:100500')

    def test_social_with_invalid_name_serialize(self):
        display_name = DisplayName(100500, 'mt', 1)
        eq_(str(display_name), 's:1:mt:100500')

    def test_template_serialize(self):
        self.display_name.set('t:%login%')
        eq_(str(self.display_name), 't:%login%')

    def test_social_with_smile_set(self):
        self.display_name.set('s:8164845:mr:CCCP :)')
        eq_(self.display_name.is_passport, False)
        eq_(self.display_name.is_social, True)
        eq_(self.display_name.is_template, False)
        eq_(self.display_name.name, 'CCCP :)')
        eq_(self.display_name.profile_id, 8164845)
        eq_(self.display_name.provider, 'mr')

    @raises(TypeError)
    def test_display_name_with_provider_and_without_profile_id(self):
        DisplayName(name='test', provider='vk')

    def test_with_public_name(self):
        display_name = DisplayName('display', public_name='public')
        eq_(display_name.name, 'display')
        eq_(display_name.public_name, 'public')
        eq_(
            display_name.as_dict(with_public_name=True),
            {'name': 'display', 'public_name': 'public'},
        )

    def test_convert_to_passport_ok(self):
        self.display_name.set('s:8164845:mr:CCCP :)')
        self.display_name.convert_to_passport()
        ok_(self.display_name.is_passport)
        eq_(self.display_name.name, 'CCCP :)')
        ok_(self.display_name.profile_id is None)
        ok_(self.display_name.provider is None)

    @raises(TypeError)
    def test_convert_to_passport_error(self):
        self.display_name.set('p:123')
        self.display_name.convert_to_passport()

    def test_repr(self):
        self.display_name.set('p:123')
        ok_(repr(self.display_name))

    def test_passport_as_dict(self):
        display_name = DisplayName('100500')
        eq_(
            display_name.as_dict(),
            {'name': '100500'},
        )

    def test_social_as_dict(self):
        display_name = DisplayName('100500', 'fb', 1)
        eq_(
            display_name.as_dict(),
            {
                'name': '100500',
                'social': {
                    'profile_id': 1,
                    'provider': u'fb',
                },
            },
        )

    def test_cyrillic_as_dict(self):
        display_name = DisplayName(u'Козьма Прутков')
        eq_(
            display_name.as_dict(),
            {
                'name': u'Козьма Прутков',
            },
        )

    def test_empty_display_name_set(self):
        self.display_name.set('')
        eq_(self.display_name.is_passport, True)
        eq_(self.display_name.is_social, False)
        eq_(self.display_name.is_template, False)
        assert_is_none(self.display_name.name)
        eq_(
            self.display_name.as_dict(),
            {'name': u''},
        )
