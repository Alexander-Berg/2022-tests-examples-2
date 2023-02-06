package ru.yandex.metrika.cdp.api.validation.builders;

import java.util.HashMap;
import java.util.Map;
import java.util.Set;

import ru.yandex.metrika.cdp.dto.schema.Attribute;
import ru.yandex.metrika.cdp.frontend.rows.RowsTestUtils;
import ru.yandex.metrika.cdp.frontend.schema.rows.ListItemRow;

public final class ListItemRowBuilder implements AttributesContainerBuilder<ListItemRow, ListItemRowBuilder>, NameAwareBuilder<ListItemRow, ListItemRowBuilder> {
    private String name;
    private String humanized;
    private int counterId;
    private long recordNumber;
    private Map<Attribute, Set<String>> attributeValues = new HashMap<>();

    private ListItemRowBuilder() {
    }

    public static ListItemRowBuilder aListItemRow() {
        return new ListItemRowBuilder();
    }

    public ListItemRowBuilder withName(String name) {
        this.name = name;
        return this;
    }

    public ListItemRowBuilder withHumanized(String humanized) {
        this.humanized = humanized;
        return this;
    }

    public ListItemRowBuilder withCounterId(int counterId) {
        this.counterId = counterId;
        return this;
    }

    public ListItemRowBuilder withRecordNumber(long recordNumber) {
        this.recordNumber = recordNumber;
        return this;
    }

    public ListItemRowBuilder withAttributeValues(Map<Attribute, Set<String>> attributeValues) {
        this.attributeValues = attributeValues;
        return this;
    }

    @Override
    public ListItemRowBuilder withAttribute(Attribute attribute, Set<String> values) {
        attributeValues.put(attribute, values);
        return this;
    }

    @Override
    public ListItemRowBuilder withAttribute(Attribute attribute, String value) {
        attributeValues.put(attribute, Set.of(value));
        return this;
    }

    public ListItemRow build() {
        ListItemRow listItemRow = new ListItemRow();

        RowsTestUtils.setCounterId(listItemRow, counterId);

        listItemRow.setName(name);
        listItemRow.setHumanized(humanized);
        listItemRow.setRecordNumber(recordNumber);
        listItemRow.setAttributeValues(attributeValues);
        return listItemRow;
    }
}
