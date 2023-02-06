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
 * Проверяем, что если в конфиге не прописать приложение, оно будет запрещено
 * <p>
 * Created by graev on 13/03/2017.
 */
@RunWith(Parameterized.class)
public class ConfigBasedPushRestrictionNegativeTest {

    private static final long ALLOWED_APP = 42;

    private static final long FORBIDDEN_APP = 46;

    @Parameterized.Parameter
    public ConfigBasedPushRestriction restriction;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(param(allowNone()))
                .add(param(allowAnotherApp()))
                .build();
    }

    @Test
    public void testAppIfForbidden() {
        assertThat("Application from config is forbidden",
                restriction.isAllowed(FORBIDDEN_APP), is(false));
    }

    private static Object[] param(ConfigBasedPushRestriction restriction) {
        return new Object[]{restriction};
    }

    private static ConfigBasedPushRestriction allowNone() {
        return new ConfigBasedPushRestriction();
    }

    private static ConfigBasedPushRestriction allowAnotherApp() {
        final ConfigBasedPushRestriction restriction = new ConfigBasedPushRestriction();
        restriction.setAllowAppId(Collections.singletonList(ALLOWED_APP));
        return restriction;
    }
}
