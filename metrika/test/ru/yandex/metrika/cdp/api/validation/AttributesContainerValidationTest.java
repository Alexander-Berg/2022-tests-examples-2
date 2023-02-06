package ru.yandex.metrika.cdp.api.validation;

import java.util.Set;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.springframework.beans.factory.annotation.Autowired;

import ru.yandex.metrika.cdp.api.InMemoryListsChecker;
import ru.yandex.metrika.cdp.api.validation.builders.AttributesContainerBuilder;
import ru.yandex.metrika.cdp.dto.schema.AttributesContainer;
import ru.yandex.metrika.cdp.dto.schema.ListType;

import static org.junit.Assert.assertThat;
import static ru.yandex.metrika.cdp.api.validation.util.AttributesCreationUtil.CUSTOM_LIST_ITEM_NAME;
import static ru.yandex.metrika.cdp.api.validation.util.AttributesCreationUtil.CUSTOM_LIST_NAME;
import static ru.yandex.metrika.cdp.api.validation.util.AttributesCreationUtil.attributeLocation;
import static ru.yandex.metrika.cdp.api.validation.util.AttributesCreationUtil.attributeWithListType;
import static ru.yandex.metrika.cdp.api.validation.util.AttributesCreationUtil.dateAttribute;
import static ru.yandex.metrika.cdp.api.validation.util.AttributesCreationUtil.emailAttribute;
import static ru.yandex.metrika.cdp.api.validation.util.AttributesCreationUtil.numericAttribute;

public abstract class AttributesContainerValidationTest<T extends AttributesContainer, B extends AttributesContainerBuilder<T, B>> extends AbstractValidationTest<T, B> {

    protected static final String NOT_AN_EMAIL = "some_thing_that_is_clearly_not_an_email!!! XD@@@@";

    @Autowired
    protected InMemoryListsChecker listsChecker;

    private final boolean allowNotPredefinedTypes;

    protected AttributesContainerValidationTest(boolean allowNotPredefinedTypes) {
        this.allowNotPredefinedTypes = allowNotPredefinedTypes;
    }

    public AttributesContainerValidationTest() {
        allowNotPredefinedTypes = true;
    }

    @Before
    @Override
    public void setUp() {
        super.setUp();

        listsChecker.add(1, ListType.CUSTOM, CUSTOM_LIST_NAME, CUSTOM_LIST_ITEM_NAME);
    }

    @After
    public void tearDown() {
        listsChecker.remove(1, ListType.CUSTOM, CUSTOM_LIST_NAME);
    }

    @Test
    public void testCustomAttributeBefore1970() {
        var dateAttribute = dateAttribute();
        var contactRow = minimalValidBuilder().withAttribute(dateAttribute, "1969-01-01").build();
        assertThat(contactRow, notValidAtLocation(attributeLocation(dateAttribute)));
    }

    @Test
    public void testNotValidNumberInCustomAttribute() {
        var numericAttribute = numericAttribute();
        var contactRow = minimalValidBuilder().withAttribute(numericAttribute, "abc").build();
        assertThat(contactRow, notValidAtLocation(attributeLocation(numericAttribute)));
    }

    @Test
    public void testNotValidDateInCustomAttribute() {
        var dateAttribute = dateAttribute();
        var contactRow = minimalValidBuilder().withAttribute(dateAttribute, "abc").build();
        assertThat(contactRow, notValidAtLocation(attributeLocation(dateAttribute)));
    }

    @Test
    public void testNotValidEmailInCustomAttribute() {
        var emailAttribute = emailAttribute();
        var contactRow = minimalValidBuilder().withAttribute(emailAttribute, NOT_AN_EMAIL).build();
        assertThat(contactRow, notValidAtLocation(attributeLocation(emailAttribute)));
    }

    @Test
    public void testNotValidCustomAttributeWithListType() {
        var attributeWithListType = attributeWithListType("unknownCustomList");
        var contactRow = minimalValidBuilder().withAttribute(attributeWithListType, CUSTOM_LIST_ITEM_NAME).build();
        assertThat(contactRow, notValidAtLocation(attributeLocation(attributeWithListType)));
    }

    @Test
    public void testCustomAttributeValueWithListType() {
        var attributeWithListType = attributeWithListType(CUSTOM_LIST_NAME);
        var contactRow = minimalValidBuilder().withAttribute(attributeWithListType, CUSTOM_LIST_ITEM_NAME).build();
        assertThat(contactRow, allowNotPredefinedTypes ? validationMatchers.valid() : notValidAtLocation(attributeLocation(attributeWithListType)));
    }

    @Test
    public void testNotValidCustomAttributeValueWithListType() {
        var attributeWithListType = attributeWithListType(CUSTOM_LIST_NAME);
        var contactRow = minimalValidBuilder().withAttribute(attributeWithListType, "unknownListItem").build();
        assertThat(contactRow, notValidAtLocation(attributeLocation(attributeWithListType)));
    }

    @Test
    public void testValidMultivalueValueAttributeWithMultipleValues() {
        var dateAttribute = dateAttribute();
        dateAttribute.setMultivalued(true);
        var contactRow = minimalValidBuilder().withAttribute(dateAttribute, Set.of("2020-01-01", "2020-02-02")).build();
        assertThat(contactRow, validationMatchers.valid());
    }

    @Test
    public void testNotValidSingleValueAttributeWithMultipleValues() {
        var dateAttribute = dateAttribute();
        var contactRow = minimalValidBuilder().withAttribute(dateAttribute, Set.of("2020-01-01", "2020-02-02")).build();
        assertThat(contactRow, notValidAtLocation(attributeLocation(dateAttribute)));
    }


}
