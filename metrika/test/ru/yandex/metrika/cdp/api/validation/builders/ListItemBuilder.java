package ru.yandex.metrika.cdp.api.validation.builders;

import java.util.HashMap;
import java.util.Map;
import java.util.Set;

import ru.yandex.metrika.cdp.dto.schema.Attribute;
import ru.yandex.metrika.cdp.dto.schema.ListItem;

public final class ListItemBuilder implements AttributesContainerBuilder<ListItem, ListItemBuilder>, NameAwareBuilder<ListItem, ListItemBuilder> {
    private String name;
    private String humanized;
    private Map<Attribute, Set<String>> attributeValues = new HashMap<>();

    private ListItemBuilder() {
    }

    public static ListItemBuilder aListItem() {
        return new ListItemBuilder();
    }

    public ListItemBuilder withName(String name) {
        this.name = name;
        return this;
    }

    public ListItemBuilder withHumanized(String humanized) {
        this.humanized = humanized;
        return this;
    }

    public ListItemBuilder withAttributeValues(Map<Attribute, Set<String>> attributeValues) {
        this.attributeValues = attributeValues;
        return this;
    }

    @Override
    public ListItemBuilder withAttribute(Attribute attribute, Set<String> values) {
        attributeValues.put(attribute, values);
        return this;
    }

    @Override
    public ListItemBuilder withAttribute(Attribute attribute, String value) {
        attributeValues.put(attribute, Set.of(value));
        return this;
    }

    public ListItem build() {
        ListItem listItem = new ListItem();
        listItem.setName(name);
        listItem.setHumanized(humanized);
        listItem.setAttributeValues(attributeValues);
        return listItem;
    }
}
