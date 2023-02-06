package ru.yandex.autotests.metrika.tests.ft.management.labels;

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
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by proxeter on 28.07.2014.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.LABELS)
@Title("Проверка удаления метки")
public class DeleteLabelTest {
    private UserSteps user;

    private Long labelId;
    private Label label;

    @Before
    public void before() {
        user = new UserSteps();
        label = ManagementTestData.getDefaultLabel();
        labelId = user.onManagementSteps().onLabelsSteps().addLabelAndExpectSuccess(label).getId();
    }

    @Test
    @Title("Метка: 200 статус после удаления метки")
    public void deleteLabelTest() {
        user.onManagementSteps().onLabelsSteps().deleteLabelAndExpectSuccess(labelId);
    }

    @Test
    @Title("Метка: метка отствует в списке меток после удаления")
    public void deletedLabelNotAvailableTest() {
        user.onManagementSteps().onLabelsSteps().deleteLabelAndExpectSuccess(labelId);
        List<Long> labels = user.onManagementSteps().onLabelsSteps().getLabels();

        assertThat("Добавленная метка отсутствует в списке доступных счетчиков", labels,
                not(hasItem(labelId)));
    }
}
