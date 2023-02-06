package ru.yandex.metrika.mobmet.push.common;

import java.util.Collections;
import java.util.Map;

import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.mobmet.push.common.campaigns.model.PushCampaignMessage;
import ru.yandex.metrika.mobmet.push.common.requests.InstantPushContext;
import ru.yandex.metrika.mobmet.push.common.service.PushBatch;

import static org.mockito.Matchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;

/**
 * Проверяем, что настройками можно определить, ходит ли пуш к провайдеру
 * <p>
 * Created by graev on 13/03/2017.
 */
public class RestrictingPushSenderTest {

    private static final long ALLOWED_APP = 42;

    private static final long FORBIDDEN_APP = 46;

    private PlatformPushSender underlying = mock(PlatformPushSender.class);

    private RestrictingPushSender restricting = new RestrictingPushSender(restriction(), underlying);

    @Before
    public void setup() {
        underlying = mock(PlatformPushSender.class);
        restricting = new RestrictingPushSender(restriction(), underlying);
    }

    @Test
    public void testAllowedPushForApp() {
        restricting.sendPushMessages(credentials(), batch(ALLOWED_APP), message());
        verify(underlying).sendPushMessages(any(), any(), any());
    }

    @Test
    public void testForbiddenPush() {
        restricting.sendPushMessages(credentials(), batch(FORBIDDEN_APP), message());
        verify(underlying, never()).sendPushMessages(any(), any(), any());
    }

    private static Map<PushMethod, PushCredentials> credentials() {
        return Collections.emptyMap();
    }

    private static PushBatch batch(long appId) {
        return new PushBatch(new InstantPushContext(null, appId), Collections.emptySet());
    }

    private static PushCampaignMessage message() {
        return new PushCampaignMessage();
    }

    private static PushRestrictionStrategy restriction() {
        final ConfigBasedPushRestriction restriction = new ConfigBasedPushRestriction();
        restriction.setAllowAppId(Collections.singletonList(ALLOWED_APP));
        return restriction;
    }
}
