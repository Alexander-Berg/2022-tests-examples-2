package ru.yandex.autotests.metrika.tests.ft.management.labels;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData;
import ru.yandex.metrika.api.management.client.label.Label;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static org.hamcrest.Matchers.hasItem;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by proxeter on 24.07.2014.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.LABELS)
@Title("Проверка получения списка меток пользователей")
public class LabelsListTest {

    /**
     * Шаги
     */
    private UserSteps user;

    private Long labelId;
    private Label label;
    private Label addedLabel;

    @Before
    public void before() {
        user = new UserSteps();
        label = ManagementTestData.getDefaultLabel();
        addedLabel = user.onManagementSteps().onLabelsSteps().addLabelAndExpectSuccess(label);
        labelId = addedLabel.getId();
    }

    @Test
    @Title("Метка: получение списка меток пользователя")
    public void labelsListTest() {
        List<Long> labels =
                user.onManagementSteps().onLabelsSteps().getLabels();

        assertThat("Добавленная метка присутствует в списке доступных счетчиков", labels, hasItem(labelId));
    }

    @After
    public void after() {
        user.onManagementSteps().onLabelsSteps().deleteLabelAndExpectSuccess(labelId);
    }

}
