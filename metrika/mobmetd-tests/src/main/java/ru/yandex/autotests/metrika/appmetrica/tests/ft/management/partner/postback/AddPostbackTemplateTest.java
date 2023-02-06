package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.partner.postback;

import java.util.Collection;
import java.util.List;

import com.google.common.collect.ImmutableList;
import com.rits.cloning.Cloner;
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
import ru.yandex.metrika.mobmet.model.redirect.PostbackMethod;
import ru.yandex.metrika.mobmet.model.redirect.PostbackTemplate;
import ru.yandex.metrika.mobmet.model.redirect.TrackingPartner;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.core.IsCollectionContaining.hasItem;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER_2;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.GrantCreator.forUser;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultPartner;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultPostbackTemplate;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.postPostbackBody;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.postPostbackHeaders;
import static ru.yandex.autotests.metrika.appmetrica.wrappers.PartnerWrapper.wrap;
import static ru.yandex.metrika.api.management.client.external.GrantType.AGENCY_EDIT;
import static ru.yandex.metrika.api.management.client.external.GrantType.EDIT;

/**
 * Created by graev on 26/12/2016.
 */
@Features(Requirements.Feature.Management.Partner.POSTBACK_TEMPLATE)
@Stories({
        Requirements.Story.Partner.PostbackTemplate.ADD
})
@RunWith(Parameterized.class)
@Title("Добавление шаблона постбека")
public final class AddPostbackTemplateTest {

    private static final TestData.GrantCreator GRANTS = forUser(SIMPLE_USER);

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
                param(SIMPLE_USER, SIMPLE_USER),
                param(SIMPLE_USER_2, SIMPLE_USER, GRANTS.grant(EDIT)),
                param(SIMPLE_USER_2, SIMPLE_USER, GRANTS.grant(AGENCY_EDIT)),
                oldFormatParam(),
                param(SIMPLE_USER, SIMPLE_USER, null, defaultPostbackTemplate()
                        .withMethod(PostbackMethod.POST)
                        .withHeaders(postPostbackHeaders())
                        .withBody(postPostbackBody()))
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
        addedTemplate = userSteps.onPostbackTemplateSteps().createTemplate(templateToAdd);
    }

    @Test
    public void checkPostbackTemplateInfo() {
        assertThat("добавленный шаблон постбека эквивалентен ожидаемому", addedTemplate,
                equivalentTo(expectedTemplate));
    }

    @Test
    public void checkActualPostbackTemplateInfo() {
        final PostbackTemplate actual = userSteps.onPostbackTemplateSteps().getPostbackTemplate(addedTemplate.getId());
        assertThat("актуальный шаблон постбека эквивалентен ожидаемому", actual,
                equivalentTo(expectedTemplate));
    }

    @Test
    public void checkPostbackTemplateList() {
        final List<PostbackTemplate> templates = userSteps.onPostbackTemplateSteps().getPostbackTemplateList(partnerId);
        assertThat("список шаблонов постбеков содержит шаблон, эквивалентный ожидаемому",
                templates, hasItem(equivalentTo(expectedTemplate)));
    }

    @After
    public void teardown() {
        ownerSteps.onPostbackTemplateSteps().deleteTemplateIgnoringResult(addedTemplate.getId());
        ownerSteps.onPartnerSteps().deletePartnerIgnoringResult(partnerId);
        ownerSteps.onGrantSteps().deleteGrantIgnoringResult(appId, grant);
        ownerSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }

    private static Object[] oldFormatParam() {
        PostbackTemplate request = defaultPostbackTemplate()
                .withMethod(null)
                .withHeaders(null);
        PostbackTemplate expected = new Cloner()
                .deepClone(request)
                .withMethod(PostbackMethod.GET)
                .withHeaders(ImmutableList.of());
        return param(SIMPLE_USER, SIMPLE_USER, null, request, expected);
    }

    private static Object[] param(User owner, User user) {
        return param(owner, user, null, defaultPostbackTemplate());
    }

    private static Object[] param(User owner, User user, MobmetGrantE grant) {
        return param(owner, user, grant, defaultPostbackTemplate());
    }

    private static Object[] param(User owner, User user, MobmetGrantE grant, PostbackTemplate template) {
        return param(owner, user, grant, template, template);
    }

    private static Object[] param(User owner, User user, MobmetGrantE grant,
                                  PostbackTemplate request, PostbackTemplate expected) {
        return toArray(owner, user, new GrantWrapper(grant), new PostbackTemplateWrapper(request), expected);
    }

}
