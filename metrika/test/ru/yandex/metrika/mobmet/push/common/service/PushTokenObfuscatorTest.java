package ru.yandex.metrika.mobmet.push.common.service;

import java.util.Collections;

import org.apache.commons.lang3.StringUtils;
import org.junit.Test;

import ru.yandex.metrika.mobmet.push.common.ConfigBasedPushRestriction;
import ru.yandex.metrika.mobmet.push.common.PushRestrictionStrategy;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.CoreMatchers.not;
import static org.hamcrest.MatcherAssert.assertThat;

/**
 * Created by graev on 14/03/2017.
 */
public class PushTokenObfuscatorTest {
    private static final long ALLOWED_APP = 42;

    private static final long FORBIDDEN_APP = 46;

    private static final String INITIAL_TOKEN = "Meaningful token";

    private final PushTokenObfuscator obfuscator = new PushTokenObfuscator(restriction());

    @Test
    public void testTokenForAllowedApp() {
        final String processed = obfuscator.transform(ALLOWED_APP, INITIAL_TOKEN);
        assertThat("Token for allowed app should stay the same", processed, equalTo(INITIAL_TOKEN));
    }

    @Test
    public void testTokenForForbiddenApp() {
        final String processed = obfuscator.transform(FORBIDDEN_APP, INITIAL_TOKEN);
        assertThat("Token for forbidden app should change", processed, not(equalTo(INITIAL_TOKEN)));
    }

    @Test
    public void testTokenHasXOnly() {
        final String processed = obfuscator.transform(FORBIDDEN_APP, INITIAL_TOKEN);
        assertThat("Obfuscated token should contain only 'X' symbol", processed,
                equalTo(StringUtils.repeat('X', INITIAL_TOKEN.length())));
    }

    private static PushRestrictionStrategy restriction() {
        final ConfigBasedPushRestriction restriction = new ConfigBasedPushRestriction();
        restriction.setAllowAppId(Collections.singletonList(ALLOWED_APP));
        return restriction;
    }

}
