# -*- coding: utf-8 -*-
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.core.raises import (
    calling,
    Raises as MatcherRaises,
)


class SubmittedForm(BaseMatcher):
    def __init__(self, params, matcher, state=None):
        self.params = params
        self.matcher = matcher
        self.state = state

    def _matches(self, form):
        return self.matcher.matches(self._can_raise(form))

    def describe_to(self, description):
        description.append_text('form submitted with %s: ' % self.params)
        description.append_description_of(self.matcher)

    def describe_mismatch(self, form, description):
        description.append_text('after submit of %s - ' % form.__class__)
        self.matcher.matches(self._can_raise(form), description)

    def _can_raise(self, form):
        if isinstance(self.matcher, MatcherRaises):
            return calling(form.to_python).with_args(self.params, self.state)
        return form.to_python(self.params, self.state)


def submitted_with(params, matcher, state=None):
    """Вызывает сабмит формы и применяет другой матчер к результату.

    :param params: Форма для сабмита
    :param matcher: Матчер, который будет применен к результату
    :param state: Дополнительный параметр стейта - будет спроксирован в форму

    этот матчер - простой проксик между формой, ее сабмитом и валидацией результата

    Примеры::

        assert_that(some_form, submitted_with(invalid_form_args_dict, raises_invalid()))
        assert_that(some_form, submitted_with(form_args_dict, deep_eq(to_expected_state)))

    :return: Матчер, готовый сматчить форму путем ее сабмита и передачи результата другому матчеру
    """
    return SubmittedForm(params, matcher, state)
