package ru.yandex.metrika.cdp.api.validation.builders;

import java.util.Map;
import java.util.Set;

import ru.yandex.metrika.cdp.dto.schema.Attribute;
import ru.yandex.metrika.cdp.dto.schema.AttributesContainer;

public interface AttributesContainerBuilder<T extends AttributesContainer, Self extends AttributesContainerBuilder<T, Self>> extends Builder<T> {
    Self withAttributeValues(Map<Attribute, Set<String>> attributeValues);

    Self withAttribute(Attribute attribute, Set<String> values);

    Self withAttribute(Attribute attribute, String value);
}
