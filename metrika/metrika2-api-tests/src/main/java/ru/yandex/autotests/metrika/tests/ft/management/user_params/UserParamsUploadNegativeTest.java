package ru.yandex.autotests.metrika.tests.ft.management.user_params;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.autotests.irt.testutils.rules.parameters.ParametersIgnoreRule;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.userparams.UserParamsUploadingAction;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.function.Function;

import static java.util.Arrays.asList;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.UserParamsParameters.userParamsAction;
import static ru.yandex.autotests.metrika.errors.ManagementError.EMPTY_FILE;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.addParameters;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.user_params.UserParamsTestData.*;
import static ru.yandex.metrika.api.management.client.external.userparams.UserParamsUploadingAction.DELETE_KEYS;
import static ru.yandex.metrika.api.management.client.external.userparams.UserParamsUploadingAction.UPDATE;
import static ru.yandex.metrika.api.management.client.external.userparams.UserParamsUploadingContentIdType.CLIENT_ID;

/**
 * Created by ava1on on 18.04.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.USER_PARAMETERS)
@Title("Параметры посетителей: загрузка параметров посетителей (негативные тесты)")
@RunWith(Parameterized.class)
public class UserParamsUploadNegativeTest {
    @Rule
    public ParametersIgnoreRule parametersIgnoreRule = new ParametersIgnoreRule();

    private static UserSteps user = new UserSteps();
    private static Long counterId;

    @Parameter
    public UserParamsUploadingAction action;

    @Parameter(1)
    public String name;

    @Parameter(2)
    public IExpectedError error;

    @Parameter(3)
    public String content;

    @Parameterized.Parameters(name = "действие: {0}, кейс: {1}")
    public static Collection<Object[]> createParameters() {
        return MultiplicationBuilder.<UserParamsUploadingAction, UserParamsUploadingAction, Object[]>builder(
                asList(UserParamsUploadingAction.values()), () -> new Object[]{})
                .apply(UPDATE::equals, addParameters(toArray(
                        createEmptyContent(EMPTY_FILE),
                        createContentWithoutData(EMPTY_FILE, CLIENT_ID))))
                .apply(DELETE_KEYS::equals, addParameters(toArray(
                        createEmptyContent(EMPTY_FILE),
                        createDeleteContentWithoutData(EMPTY_FILE))))
                .build(Function.identity(), Function.identity());
    }

    @BeforeClass
    public static void init() {
        counterId = user.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(getDefaultCounter()).getId();
    }

    @Test
    public void checkTryCreateUploading() {
        user.onManagementSteps().onUserParamsSteps().uploadFileAndExpectError(error, counterId, content,
                userParamsAction(action));
    }

    @AfterClass
    public static void cleanUp() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndIgnoreStatus(counterId);
    }
}
