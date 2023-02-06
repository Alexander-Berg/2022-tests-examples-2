package ru.yandex.metrika.mobmet.push.common;

import java.util.Collection;
import java.util.Collections;

import com.google.common.collect.ImmutableList;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import static org.hamcrest.CoreMatchers.is;
import static org.hamcrest.MatcherAssert.assertThat;

/**
 * Тестируем что конфиг не поломался
 * <p>
 * Created by graev on 13/03/2017.
 */
@RunWith(Parameterized.class)
public class ConfigBasedPushRestrictionTest {

    private static final long ALLOWED_APP = 42;

    @Parameterized.Parameter
    public ConfigBasedPushRestriction restriction;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(param(allowAll()))
                .add(param(allowApp()))
                .build();
    }

    @Test
    public void testAppIsAllowed() {
        assertThat("Application from config is allowed",
                restriction.isAllowed(ALLOWED_APP), is(true));
    }

    private static Object[] param(ConfigBasedPushRestriction restriction) {
        return new Object[]{restriction};
    }

    private static ConfigBasedPushRestriction allowAll() {
        final ConfigBasedPushRestriction restriction = new ConfigBasedPushRestriction();
        restriction.setAllowAny(true);
        return restriction;
    }

    private static ConfigBasedPushRestriction allowApp() {
        final ConfigBasedPushRestriction restriction = new ConfigBasedPushRestriction();
        restriction.setAllowAppId(Collections.singletonList(ALLOWED_APP));
        return restriction;
    }
}
