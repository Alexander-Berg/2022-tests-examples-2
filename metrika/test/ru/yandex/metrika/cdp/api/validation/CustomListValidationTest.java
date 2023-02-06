package ru.yandex.metrika.cdp.api.validation;

import java.util.List;

import org.junit.Test;

import ru.yandex.metrika.cdp.api.validation.builders.CustomListBuilder;
import ru.yandex.metrika.cdp.dto.schema.CustomList;

import static org.junit.Assert.assertThat;
import static ru.yandex.metrika.cdp.api.validation.util.AttributesCreationUtil.CUSTOM_LIST_NAME;
import static ru.yandex.metrika.cdp.api.validation.util.AttributesCreationUtil.attributeWithListType;

public class CustomListValidationTest extends NamingValidationTest<CustomList, CustomListBuilder> {

    @Test
    public void testAttributeWithCustomType() {
        var attributeWithListType = attributeWithListType(CUSTOM_LIST_NAME);
        var customList = minimalValidBuilder().withAttributes(List.of(attributeWithListType)).build();
        assertThat(customList, notValidAtLocationStartingWith("attributes"));
    }

    @Test
    public void testAbsentItems() {
        var customList = minimalValidBuilder().withItems(null).build();
        assertThat(customList, validationMatchers.valid());
    }

    @Test
    public void testAbsentAttributes() {
        var customList = minimalValidBuilder().withAttributes(null).build();
        assertThat(customList, notValidAtLocation("attributes"));
    }

    @Override
    protected CustomListBuilder minimalValidBuilder() {
        return CustomListBuilder.aCustomList().withName("name").withAttributes(List.of()).withItems(List.of());
    }
}
