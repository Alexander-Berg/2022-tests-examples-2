package ru.yandex.autotests.metrika.tests.ft.management.user_params;

import org.junit.*;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.irt.testutils.rules.parameters.IgnoreParameters;
import ru.yandex.autotests.irt.testutils.rules.parameters.ParametersIgnoreRule;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.userparams.UserParamsUploading;
import ru.yandex.metrika.api.management.client.external.userparams.UserParamsUploadingAction;
import ru.yandex.metrika.api.management.client.external.userparams.UserParamsUploadingContentIdType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.Collections;
import java.util.function.Function;

import static java.util.Arrays.asList;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.Matchers.anything;
import static org.junit.runners.Parameterized.Parameter;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.common.users.Users.*;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.UserParamsParameters.userParamsAction;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.addParameters;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.user_params.UserParamsTestData.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.metrika.api.management.client.external.userparams.UserParamsUploadingContentIdType.CLIENT_ID;
import static ru.yandex.metrika.api.management.client.external.userparams.UserParamsUploadingContentIdType.USER_ID;

/**
 * Created by ava1on on 07.04.17.
 */

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.USER_PARAMETERS)
@Title("Параметры посетителей: загрузка параметров посетителей")
@RunWith(Parameterized.class)
public class UserParamsUploadTest {
    @Rule
    public ParametersIgnoreRule parametersIgnoreRule = new ParametersIgnoreRule();

    private static UserSteps owner = new UserSteps().withUser(USER_DELEGATOR);
    private static Long counterId;
    private UserParamsUploading uploading;

    @Parameter
    public static User userParam;

    @Parameter(1)
    public UserParamsUploadingContentIdType contentIdType;

    @Parameter(2)
    public String name;

    @Parameter(3)
    public String content;

    @Parameter(4)
    public UserParamsUploadingAction action;

    @Parameterized.Parameters(name = "пользователь: {0}, тип: {1}, кейс: {2}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .values(SUPER_USER, SUPPORT, USER_DELEGATE_PERMANENT, USER_DELEGATOR)
                .vectorValues(
                        MultiplicationBuilder.<UserParamsUploadingContentIdType, UserParamsUploadingContentIdType, Object[]>builder(
                               asList(UserParamsUploadingContentIdType.values()), () -> new Object[]{})
                                .apply(CLIENT_ID::equals, addParameters(toArray(
                                                createBaseContent(CLIENT_ID),
                                                createContentWithoutHeader(CLIENT_ID),
                                                createContentWith6LevelParameter(CLIENT_ID),
                                                createContentWithShuffledColumns(CLIENT_ID),
                                                createDeleteContent())))
                                .apply(USER_ID::equals, addParameters(toArray(
                                                createBaseContent(USER_ID),
                                                createContentWithoutHeader(USER_ID),
                                                createContentWith6LevelParameter(USER_ID),
                                                createContentWithShuffledColumns(USER_ID),
                                                createDeleteContent())))
                                .buildVectorValues(Function.identity(), Function.identity()))
                .build();
    }

    @BeforeClass
    public static void init() {
        counterId = owner.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter()).getId();
    }

    @Before
    public void setup() {
        UserSteps user = new UserSteps().withUser(userParam);
        uploading = user.onManagementSteps().onUserParamsSteps().uploadFile(counterId, content, userParamsAction(action));
    }

    @Test
    @IgnoreParameters(reason = "METR-25148 - заголовок считается отдельной строкой данных", tag = "METR-25148")
    public void checkCreateUploading() {
        assertThat("загрузка успешно создалась", uploading,
                beanEquivalent(getExpectedUploading(content, action, null)));
    }

    @AfterClass
    public static void cleanUp() {
        owner.onManagementSteps().onCountersSteps().deleteCounterAndIgnoreStatus(counterId);
    }

    @IgnoreParameters.Tag(name = "METR-25148")
    public static Collection<Object[]> ignoreParameters() {
        return Collections.singletonList(toArray(
                anything(), anything(), "столбцы в другом порядке", anything(), anything())
        );
    }
}
