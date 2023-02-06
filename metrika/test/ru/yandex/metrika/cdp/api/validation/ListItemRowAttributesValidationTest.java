package ru.yandex.metrika.cdp.api.validation;

import ru.yandex.metrika.cdp.api.validation.builders.ListItemRowBuilder;
import ru.yandex.metrika.cdp.frontend.schema.rows.ListItemRow;


public class ListItemRowAttributesValidationTest extends AttributesContainerValidationTest<ListItemRow, ListItemRowBuilder> {


    public ListItemRowAttributesValidationTest() {
        super(false);
    }

    @Override
    public ListItemRowBuilder minimalValidBuilder() {
        return ListItemRowBuilder.aListItemRow().withCounterId(1).withName("name");
    }
}
