package ru.yandex.autotests.morda.pages.interfaces.validation;

import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 02/04/15
 */
public interface Validateable<T> {
    HierarchicalErrorCollector validate(Validator<? extends T> validator);
}
