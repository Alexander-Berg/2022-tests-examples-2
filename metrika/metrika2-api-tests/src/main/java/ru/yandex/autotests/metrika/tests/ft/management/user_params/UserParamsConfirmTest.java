package ru.yandex.autotests.metrika.tests.ft.management.user_params;

import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.userparams.UserParamsUploading;
import ru.yandex.metrika.api.management.client.external.userparams.UserParamsUploadingAction;
import ru.yandex.metrika.api.management.client.external.userparams.UserParamsUploadingContentIdType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.function.Function;

import static java.util.Arrays.asList;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.UserParamsParameters.userParamsAction;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.addParameters;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.user_params.UserParamsTestData.*;
import static ru.yandex.metrika.api.management.client.external.userparams.UserParamsUploadingContentIdType.CLIENT_ID;
import static ru.yandex.metrika.api.management.client.external.userparams.UserParamsUploadingContentIdType.USER_ID;

/**
 * Created by ava1on on 19.04.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.USER_PARAMETERS)
@Title("Параметры посетителей: подтверждение загрузки")
@RunWith(Parameterized.class)
public class UserParamsConfirmTest {
    private static UserSteps user = new UserSteps();
    private static Long counterId;

    private UserParamsUploading uploaded;
    private UserParamsUploading confirmed;

    @Parameter
    public UserParamsUploadingContentIdType contentIdType;

    @Parameter(1)
    public String name;

    @Parameter(2)
    public String content;

    @Parameter(3)
    public UserParamsUploadingAction action;

    @Parameterized.Parameters(name = "тип: {0}, кейс: {1}, действие: {3}")
    public static Collection<Object[]> createParameters() {
        return MultiplicationBuilder.<UserParamsUploadingContentIdType, UserParamsUploadingContentIdType, Object[]>builder(
                asList(UserParamsUploadingContentIdType.values()), () -> new Object[]{})
                .apply(CLIENT_ID::equals, addParameters(toArray(
                        createBaseContent(CLIENT_ID),
                        createDeleteContent())))
                .apply(USER_ID::equals, addParameters(toArray(
                        createContentWith6LevelParameter(USER_ID),
                        createDeleteContent())))
                .build(Function.identity(), Function.identity());
    }

    @BeforeClass
    public static void init() {
        counterId = user.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(getDefaultCounter()).getId();
    }

    @Before
    public void setup() {
        uploaded = user.onManagementSteps().onUserParamsSteps().uploadFile(counterId, content, userParamsAction(action));
        confirmed = user.onManagementSteps().onUserParamsSteps().confirm(counterId, contentIdType, uploaded);
    }

    @Test
    public void checkConfirmUploading() {
        assertThat("загрузка подтверждена", confirmed,
                beanEquivalent(uploaded));
    }

    @AfterClass
    public static void cleanUp() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndIgnoreStatus(counterId);
    }
}
