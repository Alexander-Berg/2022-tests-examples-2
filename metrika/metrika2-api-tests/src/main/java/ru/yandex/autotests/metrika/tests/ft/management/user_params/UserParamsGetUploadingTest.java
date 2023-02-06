package ru.yandex.autotests.metrika.tests.ft.management.user_params;

import com.google.common.collect.ImmutableMap;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.autotests.metrika.Requirements;
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
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import static com.google.common.collect.ImmutableList.of;
import static java.util.stream.Collectors.toMap;
import static org.hamcrest.Matchers.containsInAnyOrder;
import static org.hamcrest.Matchers.iterableWithSize;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.irt.testutils.matchers.CompositeMatcher.matchEvery;
import static ru.yandex.autotests.metrika.data.common.users.Users.*;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.UserParamsParameters.userParamsAction;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.user_params.UserParamsTestData.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.metrika.api.management.client.external.userparams.UserParamsUploadingAction.UPDATE;
import static ru.yandex.metrika.api.management.client.external.userparams.UserParamsUploadingContentIdType.CLIENT_ID;
import static ru.yandex.metrika.api.management.client.external.userparams.UserParamsUploadingContentIdType.USER_ID;
/**
 * Created by ava1on on 18.04.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.USER_PARAMETERS)
@Title("Параметры посетителей: получение загрузок")
@RunWith(Parameterized.class)
public class UserParamsGetUploadingTest {
    private static final UserParamsUploadingAction ACTION = UPDATE;

    private static final Map<UserParamsUploadingContentIdType, List<String>> UPLOADINGS = ImmutableMap
            .<UserParamsUploadingContentIdType, List<String>>builder()
            .put(CLIENT_ID, of(
                    createContent1Row(CLIENT_ID),
                    createContent2Rows(CLIENT_ID)
            ))
            .put(USER_ID, of(
                    createContent1Row(USER_ID),
                    createContent2Rows(USER_ID)
            ))
            .build();

    private static UserSteps owner = new UserSteps().withUser(USER_DELEGATOR);
    private static Long counterId;
    private static Map<UserParamsUploadingContentIdType, List<Long>> uploadingIds;

    private static UserSteps user;

    @Parameter
    public static User userParam;

    @Parameter(1)
    public UserParamsUploadingContentIdType contentIdType;

    @Parameterized.Parameters(name = "пользователь: {0}, тип: {1}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .values(SUPER_USER, SUPPORT, MANAGER, MANAGER_DIRECT, USER_DELEGATE_PERMANENT, USER_DELEGATOR)
                .values(CLIENT_ID, USER_ID)
                .build();
    }

    @BeforeClass
    public static void init() {
        counterId = owner.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(getDefaultCounter()).getId();

        uploadingIds = UPLOADINGS.entrySet().stream().collect(toMap(data -> data.getKey(),
                data -> data.getValue().stream()
                        .map(content -> owner.onManagementSteps().onUserParamsSteps()
                                .uploadFileAndConfirm(counterId, data.getKey(), content, userParamsAction(ACTION)).getId())
                        .collect(Collectors.toList())));
    }

    @Before
    public void setup() {
        user = new UserSteps().withUser(userParam);
    }

    @Test
    public void checkGetSingleUploading() {
        UserParamsUploading uploading = user.onManagementSteps().onUserParamsSteps().getUploading(counterId,
                uploadingIds.get(contentIdType).get(0));

        assertThat("вернулась корректная загрузка", uploading, beanEquivalent(
                getExpectedUploading(UPLOADINGS.get(contentIdType).get(0), ACTION, contentIdType)));
    }

    @Test
    public void checkListUploading() {
        List<UserParamsUploading> uploadings = user.onManagementSteps().onUserParamsSteps().getUploadings(counterId)
                .stream()
                .filter(s -> s.getContentIdType().equals(contentIdType))
                .collect(Collectors.toList());

        assertThat("вернулся корректный список загрузок", uploadings, matchEvery(
                iterableWithSize(UPLOADINGS.get(contentIdType).size()),
                containsInAnyOrder(IntStream.range(0, UPLOADINGS.get(contentIdType).size())
                        .mapToObj(i -> beanEquivalent(getExpectedUploading(
                                UPLOADINGS.get(contentIdType).get(i), ACTION, contentIdType)))
                        .collect(Collectors.toList())
                ))
        );
    }

    @AfterClass
    public static void cleanUp() {
        owner.onManagementSteps().onCountersSteps().deleteCounterAndIgnoreStatus(counterId);
    }
}
