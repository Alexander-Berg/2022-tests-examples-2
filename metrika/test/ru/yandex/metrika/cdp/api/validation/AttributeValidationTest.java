package ru.yandex.metrika.cdp.api.validation;

import org.junit.Test;

import ru.yandex.metrika.cdp.api.validation.builders.AttributeBuilder;
import ru.yandex.metrika.cdp.dto.schema.Attribute;
import ru.yandex.metrika.cdp.dto.schema.AttributeType;

import static org.junit.Assert.assertThat;

public class AttributeValidationTest extends NamingValidationTest<Attribute, AttributeBuilder> {

    @Test
    public void testNullType() {
        var attribute = minimalValidBuilder().withType(null).build();
        assertThat(attribute, notValidAtLocation("type"));
    }

    @Test
    public void testAbsentMultivalue() {
        var attribute = minimalValidBuilder().withMultivalued(null).build();
        assertThat(attribute, notValidAtLocation("multivalued"));
    }

    @Override
    public AttributeBuilder minimalValidBuilder() {
        return AttributeBuilder.anAttribute()
                .withCounterId(1)
                .withName("name")
                .withType(AttributeType.TEXT)
                .withMultivalued(false);
    }
}
