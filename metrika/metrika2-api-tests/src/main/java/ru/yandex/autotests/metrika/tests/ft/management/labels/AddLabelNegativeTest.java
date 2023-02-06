package ru.yandex.autotests.metrika.tests.ft.management.labels;

import org.apache.commons.lang3.StringUtils;
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
@Title("Проверка добавления метки (негативные)")
public class AddLabelNegativeTest {
    private UserSteps user;

    private Label label;
    private Long labelId;

    @Before
    public void setup() {
        user = new UserSteps();
        label = ManagementTestData.getDefaultLabel();
        labelId = user.onManagementSteps().onLabelsSteps().addLabelAndExpectSuccess(label).getId();
    }

    @Test
    @Title("Создание метки с уже существующим именем")
    public void addDuplicateLabelNameTest() {
        user.onManagementSteps().onLabelsSteps().addLabelAndExpectError(ManagementError.LABEL_ALREADY_EXIST, label);
    }

    @Test
    @Title("Создание метки со слишком длинным именем")
    public void addToLongLabelNameTest() {
        String toLongName = StringUtils.repeat("A", 256);
        Label tempLabel = ManagementTestData.getDefaultLabel();
        tempLabel.setName(toLongName);
        user.onManagementSteps().onLabelsSteps().addLabelAndExpectError(ManagementError.LABEL_NAME_TOO_LONG, tempLabel);
    }

    @Test
    @Title("Создание метки c недопустимыми символами в имени")
    public void addWithNotAllowedSymbolsInNameTest() {
        Label tempLabel = ManagementTestData.getDefaultLabel();
        tempLabel.setName("\uD83D\uDCC5");
        user.onManagementSteps().onLabelsSteps().addLabelAndExpectError(ManagementError.NOT_ALLOWED_SYMBOLS_IN_LABEL_NAME, tempLabel);
    }

    @After
    public void teardown() {
        user.onManagementSteps().onLabelsSteps().deleteLabelAndExpectSuccess(labelId);
    }
}
