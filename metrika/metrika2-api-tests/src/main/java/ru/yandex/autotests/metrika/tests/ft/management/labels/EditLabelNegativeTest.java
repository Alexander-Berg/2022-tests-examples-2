package ru.yandex.autotests.metrika.tests.ft.management.labels;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.errors.ManagementError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData;
import ru.yandex.metrika.api.management.client.label.Label;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

/**
 * Created by sourx on 30.03.2016.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.LABELS)
@Title("Проверка изменения метки (негативные)")
public class EditLabelNegativeTest {
    private UserSteps user;

    private Label label;
    private Long labelId;
    private Long changebleLabelId;

    @Before
    public void setup() {
        user = new UserSteps();
        label = ManagementTestData.getDefaultLabel();
        labelId = user.onManagementSteps().onLabelsSteps().addLabelAndExpectSuccess(label).getId();
        changebleLabelId = user.onManagementSteps().onLabelsSteps()
                .addLabelAndExpectSuccess(ManagementTestData.getDefaultLabel()).getId();

    }

    @Test
    @Title("Переименование метки на имя уже существующей")
    public void editDuplicateLabelNameTest() {
        user.onManagementSteps().onLabelsSteps()
                .editLabelAndExpectError(ManagementError.LABEL_ALREADY_EXIST, changebleLabelId, label);
    }

    @After
    public void teardown() {
        user.onManagementSteps().onLabelsSteps().deleteLabelAndExpectSuccess(labelId);
        user.onManagementSteps().onLabelsSteps().deleteLabelAndExpectSuccess(changebleLabelId);
    }
}
