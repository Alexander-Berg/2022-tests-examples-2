package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.application;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.actions.EditAction;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData;
import ru.yandex.autotests.metrika.appmetrica.wrappers.ApplicationCreationInfoWrapper;
import ru.yandex.autotests.metrika.appmetrica.wrappers.GrantWrapper;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.management.ApplicationUpdateInfo;
import ru.yandex.metrika.mobmet.model.MobmetGrantE;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER_2;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.APP_EMPTY_CATEGORY;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.FORBIDDEN;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.*;
import static ru.yandex.metrika.api.management.client.external.GrantType.EDIT;
import static ru.yandex.metrika.api.management.client.external.GrantType.VIEW;

/**
 * Created by graev on 24/01/2017.
 */
@Features(Requirements.Feature.Management.APPLICATION)
@Stories({
        Requirements.Story.Application.EDIT
})
@Title("Редактирование приложения (негативный)")
@RunWith(Parameterized.class)
public class EditApplicationNegativeTest {

    private static final TestData.GrantCreator GRANTS = TestData.GrantCreator.forUser(SIMPLE_USER);

    @Parameterized.Parameter
    public User owner;

    @Parameterized.Parameter(1)
    public User user;

    @Parameterized.Parameter(2)
    public ApplicationCreationInfoWrapper appToAdd;

    @Parameterized.Parameter(3)
    public GrantWrapper grant;

    @Parameterized.Parameter(4)
    public EditAction<Application, ApplicationUpdateInfo> editAction;

    @Parameterized.Parameter(5)
    public IExpectedError expectedError;

    private UserSteps userSteps;

    private UserSteps ownerSteps;

    private Application addedApplication;

    @Parameterized.Parameters(name = "Создатель {0}; Пользователь {1}; {3}; {4}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(param(SIMPLE_USER_2, SIMPLE_USER, GRANTS.grant(VIEW), changeApplicationName(), FORBIDDEN))
                .add(param(SIMPLE_USER_2, SIMPLE_USER, GRANTS.agencyViewGrant(), changeApplicationName(), FORBIDDEN))
                .add(param(SIMPLE_USER_2, SIMPLE_USER, GRANTS.grant(EDIT), changeCategory(null), APP_EMPTY_CATEGORY))
                .build();
    }

    @Before
    public void setup() {
        userSteps = UserSteps.onTesting(user);
        ownerSteps = UserSteps.onTesting(owner);

        addedApplication = ownerSteps.onApplicationSteps().addApplication(appToAdd.get());

        ownerSteps.onGrantSteps().createGrantIfAny(addedApplication.getId(), grant);
    }

    @Test
    public void checkEditingFails() {
        userSteps.onApplicationSteps().editApplicationAndExpectError(addedApplication.getId(),
                editAction.getUpdate(addedApplication), expectedError);
    }

    @After
    public void teardown() {
        ownerSteps.onGrantSteps().deleteGrantIgnoringResult(addedApplication.getId(), grant);
        ownerSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(addedApplication.getId());
    }

    private static Object[] param(User owner, User user, MobmetGrantE grant, EditAction<Application, ApplicationUpdateInfo> editAction, IExpectedError expectedError) {
        return toArray(owner, user, new ApplicationCreationInfoWrapper(getDefaultApplication()), new GrantWrapper(grant), editAction, expectedError);
    }
}
