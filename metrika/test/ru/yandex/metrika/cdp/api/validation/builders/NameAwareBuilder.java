package ru.yandex.metrika.cdp.api.validation.builders;

public interface NameAwareBuilder<T, Self extends NameAwareBuilder<T, Self>> extends Builder<T> {

    Self withName(String name);

    Self withHumanized(String humanized);
}
