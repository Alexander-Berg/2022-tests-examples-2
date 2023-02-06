package ru.yandex.autotests.metrika.tests.ft.management.labels;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.label.Label;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static com.google.common.collect.ImmutableList.of;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.not;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.metrika.data.common.users.Users.*;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultLabel;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getLabelName;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by vananos  on 13.07.2016
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.LABELS)
@Title("Проверка возможности изменения метки пользователями: Владелец, Саппорт, Представитель")
@RunWith(Parameterized.class)
public class EditLabelPositiveTest {
    private static final User OWNER_ACCOUNT = USER_DELEGATOR;
    private static final User DELEGATE_ACCOUNT = USER_DELEGATE_PERMANENT;

    private static UserSteps userOwner = new UserSteps().withUser(OWNER_ACCOUNT);

    private UserSteps userWithPermission;
    private Long labelId;
    private Label label;

    @Parameter(0)
    public String userRole;

    @Parameter(1)
    public User userAccount;

    @Parameters(name = "Роль: {0}, Пользователь: {1}")
    public static Collection<Object[]> createParameters() {
        return of(
                toArray("Владелец", OWNER_ACCOUNT),
                toArray("Саппорт", SUPPORT),
                toArray("Представитель", DELEGATE_ACCOUNT)
        );
    }

    @Before
    public void setup() {
        userWithPermission = new UserSteps().withUser(userAccount);
        label = getDefaultLabel();
        labelId = userOwner.onManagementSteps().onLabelsSteps().addLabelAndExpectSuccess(label).getId();
    }

    @Test
    public void labelShouldBeEdited() {
        Label editedLabel = userWithPermission.onManagementSteps()
                .onLabelsSteps().editLabelAndExpectSuccess(labelId, getDefaultLabel().withName(getLabelName()));

        assertThat("наименование метки не должно совпадать с начальным",
                editedLabel.getName(), not(equalTo(label.getName())));
    }

    @After
    public void tearDown() {
        userOwner.onManagementSteps().onLabelsSteps().deleteLabelAndExpectSuccess(labelId);
    }
}
