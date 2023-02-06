package ru.yandex.metrika.cdp.api.validation;

import ru.yandex.metrika.cdp.api.validation.builders.ListItemBuilder;
import ru.yandex.metrika.cdp.dto.schema.ListItem;

public class ListItemNamingValidationTest extends NamingValidationTest<ListItem, ListItemBuilder> {
    @Override
    public ListItemBuilder minimalValidBuilder() {
        return ListItemBuilder.aListItem().withName("name");
    }
}
