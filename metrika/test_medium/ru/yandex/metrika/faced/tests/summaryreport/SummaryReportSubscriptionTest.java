package ru.yandex.metrika.faced.tests.summaryreport;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.List;
import java.util.stream.Stream;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContext;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.test.context.TestSecurityContextHolder;

import ru.yandex.metrika.api.management.client.external.GrantType;
import ru.yandex.metrika.api.management.client.external.summaryreport.SummaryReportTelegramSubscription;
import ru.yandex.metrika.api.management.client.external.summaryreport.TelegramAuthorizationData;
import ru.yandex.metrika.api.management.client.subscriptions.SubscriptionListType;
import ru.yandex.metrika.auth.MetrikaUserDetails;

import static ru.yandex.metrika.api.management.client.subscriptions.SubscriptionListType.EDIT;
import static ru.yandex.metrika.api.management.client.subscriptions.SubscriptionListType.LIST;
import static ru.yandex.metrika.api.management.client.subscriptions.SubscriptionListType.OWNER;
import static ru.yandex.metrika.api.management.client.subscriptions.SubscriptionListType.VIEW;
import static ru.yandex.metrika.faced.users.FacedTestUsers.SIMPLE_USER2_NAME;
import static ru.yandex.metrika.faced.users.FacedTestUsers.SIMPLE_USER_NAME;
import static ru.yandex.metrika.faced.users.FacedTestUsers.usersByUsername;

@RunWith(Parameterized.class)
public class SummaryReportSubscriptionTest extends SummaryReportBaseTest {
    private final TelegramAuthorizationData authData = getBaseAuthData();

    private final MetrikaUserDetails userGrantee = usersByUsername.get(SIMPLE_USER_NAME);
    private final MetrikaUserDetails userGrantor = usersByUsername.get(SIMPLE_USER2_NAME);
    private final String lang = "ru";

    @Parameterized.Parameter(0)
    public SubscriptionListType subscriptionType;

    @Parameterized.Parameter(1)
    public int ownedCountersCount;

    @Parameterized.Parameter(2)
    public int editCountersCount;

    @Parameterized.Parameter(3)
    public int viewCountersCount;

    private final List<Integer> ownedCounterIds = new ArrayList<>();

    private final List<Integer> editCounterIds = new ArrayList<>();

    private final List<Integer> viewCounterIds = new ArrayList<>();

    @Parameterized.Parameters
    public static Collection<Object[]> createParameters() {
        return Arrays.asList(new Object[][]{
                {OWNER, 1, 1, 1},
                {EDIT, 1, 1, 1},
                {LIST, 1, 1, 1},
                {OWNER, 5, 1, 1},
                {EDIT, 1, 2, 3}
        });
    }

    @Before
    @Override
    public void setup() throws Exception {
        super.setup();

        Authentication authentication = new UsernamePasswordAuthenticationToken(userGrantee, userGrantee.getPassword(), userGrantee.getAuthorities());
        SecurityContext context = SecurityContextHolder.createEmptyContext();
        context.setAuthentication(authentication);
        TestSecurityContextHolder.setContext(context);

        authData.setHash(getAuthHash(authData.getDataCheckString()));

        summarySteps.linkTelegramAndExpectSuccess(
                mockMvc,
                lang,
                authData
        );

        for (int i = 0; i < ownedCountersCount; ++i) {
            ownedCounterIds.add(createCounter(userGrantee));
        }

        for (int i = 0; i < editCountersCount; ++i) {
            int counterId = createCounter(userGrantor);
            editCounterIds.add(counterId);
            addGrant(userGrantor, userGrantee, counterId, GrantType.edit);
        }

        for (int i = 0; i < viewCountersCount; ++i) {
            int counterId = createCounter(userGrantor);
            viewCounterIds.add(counterId);
            addGrant(userGrantor, userGrantee, counterId, GrantType.view);
        }
    }

    @Test
    public void testSubscriptionEdit() throws Exception {
        List<Integer> expectedCounterIds = getCountersBySubscription();

        SummaryReportTelegramSubscription subscription =
                summarySteps.editSubscriptionAndExpectSuccess(mockMvc, subscriptionType, subscriptionType == LIST ? expectedCounterIds: List.of());

        checkSubscription(
                subscription, subscriptionType,
                authData.getTelegramUid(), authData.getUsername(),
                lang, expectedCounterIds, userGrantee.getUid()
        );
    }

    private List<Integer> getCountersBySubscription() {
        List<Integer> result = new ArrayList<>();
        if (subscriptionType == LIST) {
            result.addAll(ownedCounterIds);
            result.addAll(viewCounterIds);
        }
        if (subscriptionType == OWNER || subscriptionType == EDIT || subscriptionType == VIEW) {
            result.addAll(ownedCounterIds);
        }
        if (subscriptionType == EDIT || subscriptionType == VIEW) {
            result.addAll(editCounterIds);
        }
        if (subscriptionType == VIEW) {
            result.addAll(viewCounterIds);
        }
        return result.stream().limit(MAX_COUNTERS_PER_SUBSCRIPTION).toList();
    }

    @After
    public void cleanup() throws Exception {
        summarySteps.cancelSummarySubscriptionAndExpectSuccess(mockMvc);
        Stream.concat(
                ownedCounterIds.stream(),
                Stream.concat(
                        viewCounterIds.stream(),
                        editCounterIds.stream()
                )
        ).forEach(this::deleteCounter);
    }

}
