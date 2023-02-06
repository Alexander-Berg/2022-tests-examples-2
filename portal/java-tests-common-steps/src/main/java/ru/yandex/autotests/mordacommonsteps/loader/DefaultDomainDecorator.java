package ru.yandex.autotests.mordacommonsteps.loader;


import ru.yandex.autotests.mordacommonsteps.annotations.DomainDependent;
import ru.yandex.autotests.utils.morda.url.Domain;

import java.lang.reflect.Field;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27.05.13
 */
public class DefaultDomainDecorator implements DomainDecorator {
    public DefaultDomainDecorator() {
    }

    @Override
    public Object decorate(Field field, Domain domain) {
        if (!field.getType().getName().equals(String.class.getName())) {
            return null;
        }

        if (field.isAnnotationPresent(DomainDependent.class)) {
            DomainDependent annotation = field.getAnnotation(DomainDependent.class);
            String result;
            if (domain.equals(Domain.RU)) {
                result = String.format(annotation.pattern(), annotation.ru());
            } else if (domain.equals(Domain.UA)) {
                result = String.format(annotation.pattern(), annotation.ua());
            } else if (domain.equals(Domain.BY)) {
                result = String.format(annotation.pattern(), annotation.by());
            } else if (domain.equals(Domain.KZ)) {
                result = String.format(annotation.pattern(), annotation.kz());
            } else {
                result = String.format(annotation.pattern(), domain);
            }
            return result;
        }
        return null;
    }
}
