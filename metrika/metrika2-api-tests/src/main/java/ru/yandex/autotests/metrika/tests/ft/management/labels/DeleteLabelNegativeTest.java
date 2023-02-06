package ru.yandex.autotests.metrika.tests.ft.management.labels;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static com.google.common.collect.ImmutableList.of;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.Matchers.hasItem;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.metrika.data.common.users.Users.MANAGER;
import static ru.yandex.autotests.metrika.data.common.users.Users.SUPPORT;
import static ru.yandex.autotests.metrika.errors.ManagementError.ACCESS_DENIED;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultLabel;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by vananos  on 13.07.2016
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.LABELS)
@Title("Проверка невозможности удаления метки пользователями: менеджер, саппорт")
@RunWith(Parameterized.class)
public class DeleteLabelNegativeTest {
    @Parameter(0)
    public String userRole;

    @Parameter(1)
    public User userAccount;

    private UserSteps userOwner = new UserSteps();
    private UserSteps userWithoutPermission;
    private long labelId;

    @Parameters(name = "Роль: {0}, пользователь: {1}")
    public static Collection<Object[]> createParameters() {
        return of(
                toArray("Менеджер", MANAGER),
                toArray("Саппорт", SUPPORT));
    }

    @Before
    public void setup() {
        userWithoutPermission = new UserSteps().withUser(userAccount);
        labelId = userOwner.onManagementSteps().onLabelsSteps().addLabelAndExpectSuccess(getDefaultLabel()).getId();
    }

    @Test
    public void labelShouldNotBeDeleted() {
        userWithoutPermission.onManagementSteps().onLabelsSteps()
                .deleteLabelAndExpectError(ACCESS_DENIED, labelId);
        List<Long> labels = userOwner.onManagementSteps().onLabelsSteps().getLabels();

        assertThat("добавленная метка присутствует в списке доступным меток", labels, hasItem(labelId));
    }

    @After
    public void tearDown() {
        userOwner.onManagementSteps().onLabelsSteps().deleteLabelAndExpectSuccess(labelId);
    }
}
