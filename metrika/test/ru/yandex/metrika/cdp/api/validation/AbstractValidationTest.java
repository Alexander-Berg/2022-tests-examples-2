package ru.yandex.metrika.cdp.api.validation;

import java.util.List;
import java.util.stream.Collectors;

import org.hamcrest.Matcher;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;

import ru.yandex.metrika.cdp.api.AbstractTest;
import ru.yandex.metrika.cdp.api.config.ValidatorConfig;
import ru.yandex.metrika.cdp.api.validation.builders.Builder;
import ru.yandex.metrika.cdp.api.validation.util.ValidationMatchers;
import ru.yandex.metrika.cdp.frontend.validation.ControllerValidationGroup;
import ru.yandex.metrika.cdp.validation.AttributesValidationSequence;
import ru.yandex.metrika.util.ApiInputValidator;

import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.hasItem;
import static org.junit.Assert.assertThat;
import static ru.yandex.metrika.cdp.api.validation.util.ValidationMatchers.withErrorLocation;
import static ru.yandex.metrika.cdp.api.validation.util.ValidationMatchers.withErrorLocationStartingWith;

@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration(classes = {
        ValidatorConfig.class,
        ValidationTestConfig.class
})
public abstract class AbstractValidationTest<T, B extends Builder<T>> extends AbstractTest {

    @Autowired
    private ApiInputValidator apiInputValidator;

    protected ValidationMatchers validationMatchers;

    @Before
    public void setUp() {
        validationMatchers = new ValidationMatchers(apiInputValidator, AttributesValidationSequence.class,
                ControllerValidationGroup.class);
    }

    @Test
    public void testValid() {
        var t = minimalValidBuilder().build();
        assertThat(t, validationMatchers.valid());
    }

    protected abstract B minimalValidBuilder();

    protected Matcher<T> notValidAtLocation(String location) {
        return validationMatchers.notValidAndErrors(hasItem(withErrorLocation(location)));
    }

    protected Matcher<T> notValidAtLocationStartingWith(String locationPrefix) {
        return validationMatchers.notValidAndErrors(hasItem(withErrorLocationStartingWith(locationPrefix)));
    }

    protected Matcher<T> notValidAtLocations(List<String> locations) {
        return validationMatchers.notValidAndErrors(
                allOf(locations.stream()
                        .map(location -> hasItem(withErrorLocation(location)))
                        .collect(Collectors.toList())
                )
        );
    }
}
