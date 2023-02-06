package ru.yandex.metrika.faced.tests.summaryreport;

import java.util.Arrays;
import java.util.Collection;
import java.util.List;

import org.junit.After;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContext;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.test.context.TestSecurityContextHolder;

import ru.yandex.metrika.api.management.client.external.summaryreport.SummaryReportSubscriptionStatus;
import ru.yandex.metrika.api.management.client.external.summaryreport.SummaryReportTelegramSubscription;
import ru.yandex.metrika.api.management.client.external.summaryreport.TelegramAuthorizationData;
import ru.yandex.metrika.api.management.client.subscriptions.SubscriptionListType;
import ru.yandex.metrika.auth.MetrikaUserDetails;

import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import static ru.yandex.metrika.faced.users.FacedTestUsers.SIMPLE_USER_NAME;
import static ru.yandex.metrika.faced.users.FacedTestUsers.usersByUsername;

@RunWith(Parameterized.class)
public class SummaryReportTelegramLinkTest extends SummaryReportBaseTest {
    @Parameterized.Parameter(0)
    public TelegramAuthorizationData authData;

    @Parameterized.Parameter(1)
    public MetrikaUserDetails user;

    @Parameterized.Parameter(2)
    public String lang;

    @Parameterized.Parameters
    public static Collection<Object[]> createParameters() {
        return Arrays.asList(new Object[][]{
                {getBaseAuthData(), usersByUsername.get(SIMPLE_USER_NAME), getRandomLanguage()},
        });
    }

    @Before
    @Override
    public void setup() throws Exception {
        super.setup();
        Authentication authentication = new UsernamePasswordAuthenticationToken(user, user.getPassword(), user.getAuthorities());
        SecurityContext context = SecurityContextHolder.createEmptyContext();
        context.setAuthentication(authentication);
        TestSecurityContextHolder.setContext(context);
    }

    @Test
    public void linkUser() throws Exception {

        authData.setHash(getAuthHash(authData.getDataCheckString()));
        SummaryReportTelegramSubscription subscription = summarySteps.linkTelegramAndExpectSuccess(
                mockMvc,
                lang,
                authData
        );

        checkSubscription(subscription, SubscriptionListType.EDIT, authData.getTelegramUid(), authData.getUsername(), lang, List.of(), user.getUid());
    }

    @Test
    public void linkWithWrongHash() throws Exception {
        authData.setHash(getAuthHash(authData.getDataCheckString()) + "_");
        summarySteps.linkTelegramAndExpect(
                mockMvc,
                lang,
                authData,
                status().isForbidden()
        );
    }

    @Test
    public void tryGetNonExistingSubscription() throws Exception {
        SummaryReportTelegramSubscription subscription = summarySteps.getSubscriptionAndExpectSuccess(mockMvc);

        Assert.assertEquals(subscription.getStatus(), SummaryReportSubscriptionStatus.INACTIVE);
    }

    @After
    public void cleanup() throws Exception {
        summarySteps.cancelSummarySubscriptionAndExpectSuccess(mockMvc);
        SecurityContextHolder.clearContext();
        TestSecurityContextHolder.clearContext();
    }
}
