package ru.yandex.autotests.metrika.tests.ft.management.user_params;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.userparams.UserParamsUploading;
import ru.yandex.metrika.api.management.client.external.userparams.UserParamsUploadingAction;
import ru.yandex.metrika.api.management.client.external.userparams.UserParamsUploadingContentIdType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.UserParamsParameters.userParamsAction;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.user_params.UserParamsTestData.createContent1Row;
import static ru.yandex.autotests.metrika.tests.ft.management.user_params.UserParamsTestData.getUploadingToChange;
import static ru.yandex.metrika.api.management.client.external.userparams.UserParamsUploadingContentIdType.CLIENT_ID;

/**
 * Created by ava1on on 18.04.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.USER_PARAMETERS)
@Title("Параметры посетителей: редактирование загрузки")
public class UserParamsEditUploadingTest {
    private final UserParamsUploadingAction ACTION = UserParamsUploadingAction.UPDATE;
    private final UserParamsUploadingContentIdType TYPE = CLIENT_ID;

    private static UserSteps user = new UserSteps();

    private Long counterId;
    private UserParamsUploading editedUploading;
    private UserParamsUploading expectedUploading;

    @Before
    public void setup() {
        counterId = user.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(getDefaultCounter()).getId();

        UserParamsUploading uploading = user.onManagementSteps().onUserParamsSteps()
                .uploadFile(counterId, createContent1Row(TYPE), userParamsAction(ACTION));

        expectedUploading = getUploadingToChange(uploading, "updatedComment");

        editedUploading = user.onManagementSteps().onUserParamsSteps().editUploading(counterId, uploading.getId(),
                expectedUploading);
    }

    @Test
    public void checkEditUploading() {
        assertThat("измененная загрузка соответствует загруженной", editedUploading,
                beanEquivalent(expectedUploading));
    }

    @After
    public void tearDown() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndIgnoreStatus(counterId);
    }
}
