package ru.yandex.metrika.cdp.api.validation;

import ru.yandex.metrika.cdp.api.validation.builders.ListItemBuilder;
import ru.yandex.metrika.cdp.dto.schema.ListItem;

public class ListItemAttributesValidationTest extends AttributesContainerValidationTest<ListItem, ListItemBuilder> {
    public ListItemAttributesValidationTest() {
        super(false);
    }

    @Override
    public ListItemBuilder minimalValidBuilder() {
        return ListItemBuilder.aListItem().withName("name");
    }
}
