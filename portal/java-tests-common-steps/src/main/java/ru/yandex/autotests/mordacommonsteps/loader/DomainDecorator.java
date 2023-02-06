package ru.yandex.autotests.mordacommonsteps.loader;

import ru.yandex.autotests.utils.morda.url.Domain;

import java.lang.reflect.Field;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27.05.13
 */
public interface DomainDecorator {

    public Object decorate(Field field, Domain domain);
}
