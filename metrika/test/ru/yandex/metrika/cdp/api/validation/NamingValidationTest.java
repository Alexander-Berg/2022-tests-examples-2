package ru.yandex.metrika.cdp.api.validation;

import org.junit.Test;

import ru.yandex.metrika.cdp.api.validation.builders.NameAwareBuilder;

import static org.junit.Assert.assertThat;

public abstract class NamingValidationTest<T, B extends NameAwareBuilder<T, B>> extends AbstractValidationTest<T, B> {

    private final String nameLocation;

    protected NamingValidationTest(String nameLocation) {
        this.nameLocation = nameLocation;
    }

    public NamingValidationTest() {
        nameLocation = "name";
    }

    @Test
    public void testNotMatcherByPatternName() {
        var item = minimalValidBuilder().withName("не валидное имя").build();
        assertThat(item, notValidAtLocation(nameLocation));
    }

    @Test
    public void testEmptyName() {
        var item = minimalValidBuilder().withName("").build();
        assertThat(item, notValidAtLocation(nameLocation));
    }

    @Test
    public void testNullName() {
        var item = minimalValidBuilder().withName(null).build();
        assertThat(item, notValidAtLocation(nameLocation));
    }

    @Test
    public void testTooLongName() {
        var item = minimalValidBuilder().withName("a".repeat(256)).build();
        assertThat(item, notValidAtLocation(nameLocation));
    }

    @Test
    public void testTooLongHumanized() {
        var item = minimalValidBuilder().withHumanized("a".repeat(4097)).build();
        assertThat(item, notValidAtLocation("humanized"));
    }
}
