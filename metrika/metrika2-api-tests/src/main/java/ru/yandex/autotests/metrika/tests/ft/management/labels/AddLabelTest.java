package ru.yandex.autotests.metrika.tests.ft.management.labels;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.label.Label;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.core.IsEqual.equalTo;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultLabel;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by proxeter on 28.07.2014.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.LABELS)
@Title("Проверка добавления метки")
public class AddLabelTest {
    private UserSteps user;
    private Label label;
    private Label addedLabel;
    private Long labelId;

    @Before
    public void setup() {
        user = new UserSteps();
        label = getDefaultLabel();
        addedLabel = user.onManagementSteps().onLabelsSteps().addLabelAndExpectSuccess(label);
        labelId = addedLabel.getId();

    }

    @Test
    @Title("Добавленная метка должна быть в списке меток пользователя")
    public void addedLabelShouldBeInLabelList() {
        assertThat("имя созданной метки совпадает с ожидаемым", addedLabel.getName(), equalTo(label.getName()));
    }

    @After
    public void tearDown() {
        user.onManagementSteps().onLabelsSteps().deleteLabelAndExpectSuccess(labelId);
    }
}
