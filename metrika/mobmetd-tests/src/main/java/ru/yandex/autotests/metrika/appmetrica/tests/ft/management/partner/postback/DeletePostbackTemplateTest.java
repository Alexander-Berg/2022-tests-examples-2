package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.partner.postback;

import java.util.Collection;
import java.util.List;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
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
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.beans.HasPropertyWithValue.hasProperty;
import static org.hamcrest.core.IsCollectionContaining.hasItem;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.User.LOGIN;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.NOT_FOUND;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultPartner;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultPostbackTemplate;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.autotests.metrika.appmetrica.wrappers.PartnerWrapper.wrap;

/**
 * Created by graev on 23/12/2016.
 */
@Features(Requirements.Feature.Management.Partner.POSTBACK_TEMPLATE)
@Stories({
        Requirements.Story.Partner.PostbackTemplate.DELETE,
})
@RunWith(Parameterized.class)
@Title("Удаление шаблона постбека")
public final class DeletePostbackTemplateTest {
    @Parameterized.Parameter
    public User owner;

    @Parameterized.Parameter(1)
    public User user;

    @Parameterized.Parameter(2)
    public GrantWrapper grant;

    @Parameterized.Parameter(3)
    public PostbackTemplateWrapper templateToAdd;

    @Parameterized.Parameter(4)
    public PostbackTemplate expectedTemplate;

    private UserSteps ownerSteps;

    private UserSteps userSteps;

    private Long partnerId;

    private PostbackTemplate addedTemplate;

    private Long appId;

    @Parameterized.Parameters(name = "Создатель {0}. Пользователь {1}. {2}. {3}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                param(SIMPLE_USER, SIMPLE_USER)
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

        userSteps.onPostbackTemplateSteps().deleteTemplate(addedTemplate.getId());
    }

    @Test
    public void checkPostbackTemplateNotFound() {
        userSteps.onPostbackTemplateSteps().getPostbackTemplateAndExpectError(addedTemplate.getId(), NOT_FOUND);
    }

    @Test
    public void checkPostbackTemplateNotFoundInList() {
        final List<PostbackTemplate> templates = userSteps.onPostbackTemplateSteps().getPostbackTemplateList(partnerId);
        assertThat("список шаблонов постбеков содержит шаблон, эквивалентный ожидаемому",
                templates, not(hasItem(hasProperty("id", equalTo(expectedTemplate.getId())))));
    }

    @After
    public void teardown() {
        ownerSteps.onPostbackTemplateSteps().deleteTemplateIgnoringResult(addedTemplate.getId());
        ownerSteps.onPartnerSteps().deletePartnerIgnoringResult(partnerId);
        if (grant.getGrant() != null) {
            ownerSteps.onGrantSteps().deleteGrantIgnoringResult(appId, user.get(LOGIN));
        }
        ownerSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }

    private static Object[] param(User owner, User user) {
        return param(owner, user, null, defaultPostbackTemplate());
    }

    private static Object[] param(User owner, User user, MobmetGrantE grant, PostbackTemplate template) {
        return toArray(owner, user, new GrantWrapper(grant), new PostbackTemplateWrapper(template), template);
    }

}
