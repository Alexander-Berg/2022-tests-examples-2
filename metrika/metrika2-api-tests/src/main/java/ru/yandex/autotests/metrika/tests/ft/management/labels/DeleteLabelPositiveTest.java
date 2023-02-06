package ru.yandex.autotests.metrika.tests.ft.management.labels;

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
import static org.hamcrest.Matchers.not;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.metrika.data.common.users.Users.USER_DELEGATE_PERMANENT;
import static ru.yandex.autotests.metrika.data.common.users.Users.USER_DELEGATOR;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultLabel;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by proxeter on 28.07.2014.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.LABELS)
@Title("Проверка удаления метки пользователями: владелец, представитель")
@RunWith(Parameterized.class)
public class DeleteLabelPositiveTest {
    private static final User OWNER_ACCOUNT = USER_DELEGATOR;
    private static final User DELEGATE_ACCOUNT = USER_DELEGATE_PERMANENT;

    private static UserSteps userOwner = new UserSteps().withUser(OWNER_ACCOUNT);

    private UserSteps userWithPermission;
    private long labelId;

    @Parameter(0)
    public String userRole;

    @Parameter(1)
    public User userAccount;

    @Parameters(name = "Роль: {0}, Пользователь: {1}")
    public static Collection<Object[]> createParameters() {
        return of(
                toArray("Владелец", OWNER_ACCOUNT),
                toArray("Представитель", DELEGATE_ACCOUNT));
    }

    @Before
    public void setup() {
        userWithPermission = new UserSteps().withUser(userAccount);
        labelId = userOwner.onManagementSteps().onLabelsSteps().addLabelAndExpectSuccess(getDefaultLabel()).getId();
    }

    @Test
    public void labelShouldBeDeleted() {
        userWithPermission.onManagementSteps().onLabelsSteps().deleteLabelAndExpectSuccess(labelId);
        List<Long> labels = userOwner.onManagementSteps().onLabelsSteps().getLabels();
        assertThat("добавленная метка отсутствует в списке доступных меток", labels, not(hasItem(labelId)));
    }
}
