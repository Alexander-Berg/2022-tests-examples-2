package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.partner.postback;

import java.util.Collection;
import java.util.List;

import com.google.common.collect.ImmutableList;
import org.apache.commons.lang3.ArrayUtils;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.actions.EditAction;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.GrantWrapper;
import ru.yandex.autotests.metrika.appmetrica.wrappers.PartnerWrapper;
import ru.yandex.autotests.metrika.appmetrica.wrappers.PostbackTemplateWrapper;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.model.MobmetGrantE;
import ru.yandex.metrika.mobmet.model.redirect.PostbackMethod;
import ru.yandex.metrika.mobmet.model.redirect.PostbackTemplate;
import ru.yandex.metrika.mobmet.model.redirect.TrackingPartner;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.core.IsCollectionContaining.hasItem;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.User.LOGIN;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.changePostbackTemplateName;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.changePostbackTemplateParams;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultPartner;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultPostbackTemplate;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.postPostbackBody;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.postPostbackHeaders;

/**
 * Created by graev on 23/12/2016.
 */
@Features(Requirements.Feature.Management.Partner.POSTBACK_TEMPLATE)
@Stories({
        Requirements.Story.Partner.PostbackTemplate.EDIT
})
@RunWith(Parameterized.class)
@Title("Редактирование шаблона постбека")
public final class EditPostbackTemplateTest {

    @Parameterized.Parameter
    public User owner;

    @Parameterized.Parameter(1)
    public User user;

    @Parameterized.Parameter(2)
    public GrantWrapper grant;

    @Parameterized.Parameter(3)
    public PostbackTemplateWrapper templateToAdd;

    @Parameterized.Parameter(4)
    public EditAction<PostbackTemplate, PostbackTemplate> editAction;

    private UserSteps ownerSteps;

    private UserSteps userSteps;

    private Long appId;

    private Long partnerId;

    private PostbackTemplate editedTemplate;

    private PostbackTemplate expectedTemplate;

    @Parameterized.Parameters(name = "Создатель {0}. Пользователь {1}. {2}. {3}. {4}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                param(SIMPLE_USER, SIMPLE_USER),
                param(SIMPLE_USER, SIMPLE_USER, null, defaultPostbackTemplate(), changePostbackTemplateParams(
                        PostbackMethod.POST, postPostbackHeaders(), postPostbackBody()))
        );
    }

    @Before
    public void setup() {
        ownerSteps = UserSteps.onTesting(owner);
        userSteps = UserSteps.onTesting(user);

        TrackingPartner addedPartner = ownerSteps.onPartnerSteps().createPartner(new PartnerWrapper(defaultPartner()));
        partnerId = addedPartner.getId();

        final Application addedApplication = ownerSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();

        ownerSteps.onGrantSteps().createGrantIfAny(appId, grant, partnerId);

        templateToAdd.getTemplate().setPartnerId(partnerId);
        PostbackTemplate addedTemplate = ownerSteps.onPostbackTemplateSteps().createTemplate(templateToAdd);

        expectedTemplate = editAction.edit(addedTemplate);
        editedTemplate = userSteps.onPostbackTemplateSteps().editPostbackTemplate(
                new PostbackTemplateWrapper(editAction.getUpdate(addedTemplate)));
    }

    @Test
    public void checkPostbackTemplateInfo() {
        assertThat("отредактированный шаблон постбека эквивалентен ожидаемому", editedTemplate,
                equivalentTo(expectedTemplate));
    }

    @Test
    public void checkActualPostbackTemplateInfo() {
        final PostbackTemplate actual = userSteps.onPostbackTemplateSteps().getPostbackTemplate(editedTemplate.getId());
        assertThat("актуальный шаблон постбека эквивалентен ожидаемому", actual,
                equivalentTo(expectedTemplate));
    }

    @Test
    public void checkPostbackTemplateList() {
        final List<PostbackTemplate> templates = userSteps.onPostbackTemplateSteps().getPostbackTemplateList(partnerId);
        assertThat("список шаблонов постбеков содержит шаблон, эквивалентный ожидаемому", templates,
                hasItem(equivalentTo(expectedTemplate)));
    }

    @After
    public void teardown() {
        ownerSteps.onPostbackTemplateSteps().deleteTemplateIgnoringResult(editedTemplate.getId());
        ownerSteps.onPartnerSteps().deletePartnerIgnoringResult(partnerId);
        if (grant.getGrant() != null) {
            ownerSteps.onGrantSteps().deleteGrantIgnoringResult(appId, user.get(LOGIN));
        }
        ownerSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }

    private static Object[] param(User owner, User user) {
        return param(owner, user, null, defaultPostbackTemplate(), changePostbackTemplateName());
    }

    private static Object[] param(User owner, User user, MobmetGrantE grant, PostbackTemplate template,
                                  EditAction<PostbackTemplate, PostbackTemplate> editAction) {
        return ArrayUtils.toArray(owner, user, new GrantWrapper(grant), new PostbackTemplateWrapper(template), editAction);
    }
}
