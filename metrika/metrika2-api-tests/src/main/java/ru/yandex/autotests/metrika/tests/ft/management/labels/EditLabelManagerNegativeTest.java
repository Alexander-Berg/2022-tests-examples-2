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

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.data.common.users.Users.MANAGER;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultLabel;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getLabelName;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by vananos 13.07.2016
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.LABELS)
@Title("Проверка невозможности изменения метки менеджером")
public class EditLabelManagerNegativeTest {
    private UserSteps userOwner = new UserSteps().withDefaultAccuracy();
    private UserSteps userManager = new UserSteps().withUser(MANAGER);
    private Long labelId;
    private Label label;

    @Before
    public void setup() {
        label = getDefaultLabel();
        labelId = userOwner.onManagementSteps().onLabelsSteps().addLabelAndExpectSuccess(label).getId();
    }

    @Test
    @Title("Метка: измененное наименование метки должно совпадать с заданным")
    public void labelNameTest() {
        userManager.onManagementSteps().onLabelsSteps()
                .editLabelAndExpectError(ManagementError.ACCESS_DENIED, labelId,
                        getDefaultLabel().withName(getLabelName()));
        Label currentLabel = userOwner.onManagementSteps().onLabelsSteps().getLabelInfo(labelId);

        assertThat("наименование метки должно совпадать с начальным", currentLabel.getName(), equalTo(label.getName()));
    }

    @Test
    @Title("Редактирование метки со слишком длинным именем")
    public void addToLongLabelNameTest() {
        String toLongName = StringUtils.repeat("A", 256);
        Label tempLabel = ManagementTestData.getDefaultLabel();
        tempLabel.setName(toLongName);
        userManager.onManagementSteps().onLabelsSteps().editLabelAndExpectError(ManagementError.LABEL_NAME_TOO_LONG, labelId, tempLabel);
    }

    @After
    public void tearDown() {
        userOwner.onManagementSteps().onLabelsSteps().deleteLabelAndExpectSuccess(labelId);
    }
}
