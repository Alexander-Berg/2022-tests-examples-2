package ru.yandex.metrika.mobmet.push.common;

import java.util.Collections;

import org.junit.Before;
import org.junit.Test;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;

/**
 * Проверяем, что мы отдаем реальные Credentials только разрешенным приложениям
 * <p>
 * Created by graev on 14/03/2017.
 */
@SuppressWarnings("unchecked")
public class RestrictingPushCredentialsServiceTest {

    private static final long ALLOWED_APP = 42;

    private static final long FORBIDDEN_APP = 46;

    private ReadOnlyCredentialsService underlying;

    private RestrictingPushCredentialsService restricting;

    @Before
    public void setup() {
        underlying = mock(ReadOnlyCredentialsService.class);
        restricting = new RestrictingPushCredentialsService<>(underlying, restriction());
    }

    @Test
    public void testCredentialsForAllowedApp() {
        final CredentialsKey key = keyForApp(ALLOWED_APP);
        restricting.loadCredentials(key);
        verify(underlying).loadCredentials(key);
    }

    @Test
    public void testCredentialsForForbiddenApp() {
        final CredentialsKey key = keyForApp(FORBIDDEN_APP);
        restricting.loadCredentials(key);
        verify(underlying, never()).loadCredentials(key);
    }

    private static CredentialsKey keyForApp(long appId) {
        return () -> appId;
    }

    private static PushRestrictionStrategy restriction() {
        final ConfigBasedPushRestriction restriction = new ConfigBasedPushRestriction();
        restriction.setAllowAppId(Collections.singletonList(ALLOWED_APP));
        return restriction;
    }
}
