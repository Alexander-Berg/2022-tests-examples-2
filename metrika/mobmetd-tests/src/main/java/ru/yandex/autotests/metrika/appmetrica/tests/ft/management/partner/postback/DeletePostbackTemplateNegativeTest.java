package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.partner.postback;

import java.util.Collection;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData;
import ru.yandex.autotests.metrika.appmetrica.wrappers.GrantWrapper;
import ru.yandex.autotests.metrika.appmetrica.wrappers.PostbackTemplateWrapper;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.model.MobmetGrantE;
import ru.yandex.metrika.mobmet.model.redirect.PostbackTemplate;
import ru.yandex.metrika.mobmet.model.redirect.TrackingPartner;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER_2;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.FORBIDDEN;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.GrantCreator.forUser;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultPartner;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultPostbackTemplate;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.autotests.metrika.appmetrica.wrappers.PartnerWrapper.wrap;
import static ru.yandex.metrika.api.management.client.external.GrantType.AGENCY_EDIT;
import static ru.yandex.metrika.api.management.client.external.GrantType.AGENCY_VIEW;
import static ru.yandex.metrika.api.management.client.external.GrantType.EDIT;
import static ru.yandex.metrika.api.management.client.external.GrantType.VIEW;

/**
 * Created by graev on 23/12/2016.
 */
@Features(Requirements.Feature.Management.Partner.POSTBACK_TEMPLATE)
@Stories({
        Requirements.Story.Partner.PostbackTemplate.DELETE,
})
@RunWith(Parameterized.class)
@Title("Удаление шаблона постбека (негативный)")
public final class DeletePostbackTemplateNegativeTest {
    private static final TestData.GrantCreator GRANTS = forUser(SIMPLE_USER);

    @Parameterized.Parameter
    public User owner;

    @Parameterized.Parameter(1)
    public User user;

    @Parameterized.Parameter(2)
    public GrantWrapper grant;

    @Parameterized.Parameter(3)
    public PostbackTemplateWrapper templateToAdd;

    private UserSteps ownerSteps;

    private UserSteps userSteps;

    private Long partnerId;

    private PostbackTemplate addedTemplate;

    private Long appId;

    @Parameterized.Parameters(name = "Создатель {0}. Пользователь {1}. {2}. {3}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                param(SIMPLE_USER_2, SIMPLE_USER),
                param(SIMPLE_USER_2, SIMPLE_USER, GRANTS.grant(VIEW)),
                param(SIMPLE_USER_2, SIMPLE_USER, GRANTS.grant(EDIT)),
                param(SIMPLE_USER_2, SIMPLE_USER, GRANTS.grant(AGENCY_VIEW)),
                param(SIMPLE_USER_2, SIMPLE_USER, GRANTS.grant(AGENCY_EDIT))
        );
    }

    @Before
    public void setup() {
        ownerSteps = UserSteps.onTesting(owner);
        userSteps = UserSteps.onTesting(user);

        TrackingPartner addedPartner = ownerSteps.onPartnerSteps().createPartner(wrap(defaultPartner()));
        partnerId = addedPartner.getId();

        final Application addedApplication = ownerSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();

        ownerSteps.onGrantSteps().createGrantIfAny(appId, grant, partnerId);

        templateToAdd.getTemplate().setPartnerId(partnerId);
        addedTemplate = ownerSteps.onPostbackTemplateSteps().createTemplate(templateToAdd);
    }

    @Test
    public void checkPostbackDeletionFails() {
        userSteps.onPostbackTemplateSteps().deleteTemplateAndExpectError(addedTemplate.getId(), FORBIDDEN);
    }

    @After
    public void teardown() {
        ownerSteps.onPostbackTemplateSteps().deleteTemplateIgnoringResult(addedTemplate.getId());
        ownerSteps.onPartnerSteps().deletePartnerIgnoringResult(partnerId);
        ownerSteps.onGrantSteps().deleteGrantIgnoringResult(appId, grant);
        ownerSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }

    private static Object[] param(User owner, User user) {
        return param(owner, user, null);
    }

    private static Object[] param(User owner, User user, MobmetGrantE grant) {
        return param(owner, user, grant, defaultPostbackTemplate());
    }

    private static Object[] param(User owner, User user, MobmetGrantE grant, PostbackTemplate template) {
        return toArray(owner, user, new GrantWrapper(grant), new PostbackTemplateWrapper(template));
    }

}
