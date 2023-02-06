package ru.yandex.metrika.cdp.api.validation.builders;

import java.util.List;

import ru.yandex.metrika.cdp.dto.schema.Attribute;
import ru.yandex.metrika.cdp.dto.schema.CustomList;
import ru.yandex.metrika.cdp.dto.schema.ListItem;

public final class CustomListBuilder implements NameAwareBuilder<CustomList, CustomListBuilder> {
    String name;
    String humanized;
    List<Attribute> attributes;
    List<ListItem> items;

    private CustomListBuilder() {
    }

    public static CustomListBuilder aCustomList() {
        return new CustomListBuilder();
    }

    public CustomListBuilder withName(String name) {
        this.name = name;
        return this;
    }

    public CustomListBuilder withHumanized(String humanized) {
        this.humanized = humanized;
        return this;
    }

    public CustomListBuilder withAttributes(List<Attribute> attributes) {
        this.attributes = attributes;
        return this;
    }

    public CustomListBuilder withItems(List<ListItem> items) {
        this.items = items;
        return this;
    }

    public CustomList build() {
        CustomList customList = new CustomList();
        customList.setName(name);
        customList.setHumanized(humanized);
        customList.setAttributes(attributes);
        customList.setItems(items);
        return customList;
    }
}
