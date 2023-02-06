package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.application;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;
import ru.yandex.autotests.metrika.appmetrica.actions.EditAction;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.ApplicationCreationInfoWrapper;
import ru.yandex.autotests.metrika.appmetrica.wrappers.GrantWrapper;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.management.ApplicationCreationInfo;
import ru.yandex.metrika.mobmet.management.ApplicationUpdateInfo;
import ru.yandex.metrika.mobmet.model.MobmetGrantE;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER_2;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.*;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.TimeZoneInfo.getSingaporeTimeZone;
import static ru.yandex.metrika.api.management.client.external.GrantType.EDIT;

/**
 * Created by konkov on 14.09.2016.
 */
@Features(Requirements.Feature.Management.APPLICATION)
@Stories({
        Requirements.Story.Application.EDIT
})
@Title("Редактирование приложения")
@RunWith(Parameterized.class)
public class EditApplicationTest {

    private static final GrantCreator GRANTS = GrantCreator.forUser(SIMPLE_USER);

    @Parameter
    public User owner;

    @Parameter(1)
    public User user;

    @Parameter(2)
    public ApplicationCreationInfoWrapper appToAdd;

    @Parameter(3)
    public GrantWrapper grant;

    @Parameter(4)
    public EditAction<Application, ApplicationUpdateInfo> editAction;

    private UserSteps userSteps;

    private UserSteps ownerSteps;

    private Long appId;

    private Application expectedApplication;

    private Application editedApplication;

    @Parameters(name = "Создатель {0}; Пользователь {1}; {3}; {4}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(param(SIMPLE_USER, changeApplicationName()))
                .add(param(SIMPLE_USER, changeTimeZone(getSingaporeTimeZone())))
                .add(param(SIMPLE_USER, changeBundleId()))
                .add(param(SIMPLE_USER, changeTeamId()))
                .add(param(SIMPLE_USER, enableGdprAgreementAccepted()))
                .add(param(SIMPLE_USER, enableUseUniversalLinks()))
                .add(param(SIMPLE_USER, enableHideAddressSetting()))
                .add(param(SIMPLE_USER, changeCategory(getUpdatedApplicationCategory())))
                .add(param(SIMPLE_USER, changeNotificationEmail(getNotificationEmail())))
                .add(param(
                        getApplicationWithEmail(),
                        SIMPLE_USER, SIMPLE_USER, null,
                        changeNotificationEmail(getNotificationEmail())))
                .add(param(SIMPLE_USER_2, SIMPLE_USER, GRANTS.grant(EDIT), changeApplicationName()))
                .add(param(SIMPLE_USER_2, SIMPLE_USER, GRANTS.grant(EDIT), changeTimeZone(getSingaporeTimeZone())))
                .add(param(SIMPLE_USER_2, SIMPLE_USER, GRANTS.grant(EDIT), changeBundleId()))
                .add(param(SIMPLE_USER_2, SIMPLE_USER, GRANTS.grant(EDIT), changeTeamId()))
                .add(param(SIMPLE_USER_2, SIMPLE_USER, GRANTS.grant(EDIT), enableGdprAgreementAccepted()))
                .add(param(SIMPLE_USER_2, SIMPLE_USER, GRANTS.grant(EDIT), enableUseUniversalLinks()))
                .add(param(SIMPLE_USER_2, SIMPLE_USER, GRANTS.grant(EDIT), enableHideAddressSetting()))
                .add(param(SIMPLE_USER_2, SIMPLE_USER, GRANTS.grant(EDIT), changeCategory(getUpdatedApplicationCategory())))
                .add(param(SIMPLE_USER_2, SIMPLE_USER, GRANTS.grant(EDIT), changeNotificationEmail(getNotificationEmail())))
                .add(param(SIMPLE_USER_2, SIMPLE_USER, GRANTS.agencyEditGrant(), failToChangeApplicationName()))
                .add(param(SIMPLE_USER_2, SIMPLE_USER, GRANTS.agencyEditGrant(), failToChangeTimeZone(getSingaporeTimeZone())))
                .add(param(SIMPLE_USER_2, SIMPLE_USER, GRANTS.agencyEditGrant(), changeBundleId()))
                .add(param(SIMPLE_USER_2, SIMPLE_USER, GRANTS.agencyEditGrant(), changeTeamId()))
                .add(param(SIMPLE_USER_2, SIMPLE_USER, GRANTS.agencyEditGrant(), enableGdprAgreementAccepted()))
                .add(param(SIMPLE_USER_2, SIMPLE_USER, GRANTS.agencyEditGrant(), enableUseUniversalLinks()))
                .add(param(SIMPLE_USER_2, SIMPLE_USER, GRANTS.agencyEditGrant(), enableHideAddressSetting()))
                .add(param(SIMPLE_USER_2, SIMPLE_USER, GRANTS.agencyEditGrant(), changeCategory(getUpdatedApplicationCategory())))
                .add(param(SIMPLE_USER_2, SIMPLE_USER, GRANTS.agencyEditGrant(), changeNotificationEmail(getNotificationEmail())))
                .build();
    }

    @Before
    public void setup() {
        userSteps = UserSteps.onTesting(user);
        ownerSteps = UserSteps.onTesting(owner);

        Application addedApplication = ownerSteps.onApplicationSteps().addApplication(appToAdd.get());
        appId = addedApplication.getId();

        ownerSteps.onGrantSteps().createGrantIfAny(addedApplication.getId(), grant);

        expectedApplication = editAction.edit(addedApplication);
        editedApplication = userSteps.onApplicationSteps()
                .editApplication(appId, editAction.getUpdate(addedApplication));
    }

    @Test
    public void checkEditedApplication() {
        assertThat("отредактированное приложение эквивалентно измененному", editedApplication,
                equivalentTo(expectedApplication));
    }

    @Test
    public void checkApplication() {
        Application actualApplication = userSteps.onApplicationSteps().getApplication(appId);

        assertThat("актуальное приложение эквивалентно измененному", actualApplication,
                equivalentTo(expectedApplication));
    }

    @After
    public void teardown() {
        ownerSteps.onGrantSteps().deleteGrantIgnoringResult(appId, grant);
        ownerSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }

    private static Object[] param(User user, EditAction<Application, ApplicationUpdateInfo> editAction) {
        return param(user, user, null, editAction);
    }

    private static Object[] param(User owner, User user, MobmetGrantE grant,
                                  EditAction<Application, ApplicationUpdateInfo> editAction) {
        return param(getDefaultApplication(), owner, user, grant, editAction);
    }

    private static Object[] param(ApplicationCreationInfo application, User owner, User user,
                                  MobmetGrantE grant, EditAction<Application, ApplicationUpdateInfo> editAction) {
        return toArray(owner, user, new ApplicationCreationInfoWrapper(application),
                new GrantWrapper(grant), editAction);
    }
}
