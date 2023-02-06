package ru.yandex.autotests.metrika.tests.ft.management.offlineconversion;

import org.apache.commons.lang3.tuple.ImmutablePair;
import org.apache.commons.lang3.tuple.Pair;
import org.hamcrest.Matchers;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.irt.testutils.RandomUtils;
import ru.yandex.autotests.irt.testutils.beandiffer.matchvariation.DefaultMatchVariation;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.management.v1.offlineconversion.BasicOfflineConversionUploadingData;
import ru.yandex.autotests.metrika.data.management.v1.offlineconversion.CallsOfflineConversionUploadingData;
import ru.yandex.autotests.metrika.data.management.v1.offlineconversion.OfflineConversionType;
import ru.yandex.autotests.metrika.data.management.v1.offlineconversion.OfflineConversionUploadingData;
import ru.yandex.autotests.metrika.data.parameters.management.v1.OfflineConversionParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.offlineconversion.OfflineConversionUploading;
import ru.yandex.metrika.api.management.client.external.offlineconversion.OfflineConversionUploadingStatus;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.IntStream;

import static com.google.common.collect.ImmutableList.of;
import static java.util.stream.Collectors.toList;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.common.users.Users.*;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.OfflineConversionType.BASIC;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.OfflineConversionType.CALLS;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.offlineconversion.OfflineConversionUploadingTestData.createBaseData1Row;
import static ru.yandex.autotests.metrika.tests.ft.management.offlineconversion.OfflineConversionUploadingTestData.createBaseData2Rows;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.metrika.api.management.client.external.offlineconversion.OfflineConversionUploadingClientIdType.CLIENT_ID;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.OFFLINE_CONVERSION)
@Title("Получение загрузок офлайн конверсий")
@RunWith(Parameterized.class)
public class OfflineConversionUploadingGetTest<T extends OfflineConversionUploadingData> {

    private static final String COMMENT = RandomUtils.getString(20);

    private static final List<List<BasicOfflineConversionUploadingData>> BASIC_DATA = of(
            createBaseData1Row(BASIC, CLIENT_ID),
            createBaseData2Rows(BASIC, CLIENT_ID)
    );

    private static final List<List<CallsOfflineConversionUploadingData>> CALLS_DATA = of(
            createBaseData1Row(CALLS, CLIENT_ID),
            createBaseData2Rows(CALLS, CLIENT_ID)
    );

    private static UserSteps ownerUser;
    private static Long counterId;
    private static Map<OfflineConversionType<?>, List<Pair<Long, List<? extends OfflineConversionUploadingData>>>> uploadingInfos = new HashMap<>();

    private UserSteps user;

    @Parameterized.Parameter
    public OfflineConversionType<T> type;

    @Parameterized.Parameter(1)
    public User userParam;

    @Parameterized.Parameters(name = "Тип {0}, пользователь {1}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .values(BASIC, CALLS)
                .values(SUPER_USER, SUPPORT, MANAGER, MANAGER_DIRECT, USER_DELEGATE_PERMANENT, USER_DELEGATOR)
                .build();
    }

    @BeforeClass
    public static void initClass() {
        ownerUser = new UserSteps().withUser(USER_DELEGATOR);
        counterId = ownerUser.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter())
                .getId();

        uploadingInfos.put(BASIC, BASIC_DATA.stream()
                .map(data -> ImmutablePair.<Long, List<? extends OfflineConversionUploadingData>>of(
                        ownerUser.onManagementSteps().onOfflineConversionSteps()
                                .upload(BASIC, counterId, data, new OfflineConversionParameters()
                                        .withClientIdType(CLIENT_ID)
                                        .withIgnoreVisitJoinThreshold(1)
                                        .withComment(COMMENT))
                                .getId(),
                        data
                ))
                .collect(toList())
        );

        uploadingInfos.put(CALLS, CALLS_DATA.stream()
                .map(data -> ImmutablePair.<Long, List<? extends OfflineConversionUploadingData>>of(
                        ownerUser.onManagementSteps().onOfflineConversionSteps()
                                .upload(CALLS, counterId, data, new OfflineConversionParameters()
                                        .withClientIdType(CLIENT_ID)
                                        .withIgnoreCallsVisitJoinThreshold(1)
                                        .withComment(COMMENT))
                                .getId(),
                        data
                ))
                .collect(toList())
        );
    }

    @Before
    public void init() {
        user = new UserSteps().withUser(userParam);
    }

    @Test
    public void checkGetSingle() {
        Long id = uploadingInfos.get(type).get(0).getKey();
        List<? extends OfflineConversionUploadingData> data = uploadingInfos.get(type).get(0).getValue();

        OfflineConversionUploading uploading = user.onManagementSteps().onOfflineConversionSteps()
                .getUploading(type, counterId, id);

        assertThat("вернулась корректная загрузка", uploading, beanEquivalent(new OfflineConversionUploading()
                .withId(id)
                .withSourceQuantity((long) data.size())
                .withLineQuantity((long) data.size())
                .withStatus(OfflineConversionUploadingStatus.UPLOADED)
                .withComment(COMMENT)
        ).withVariation(new DefaultMatchVariation()
                .forFields("createTime")
                .useMatcher(notNullValue())
        ));
    }

    @Test
    public void checkGetList() {
        List<OfflineConversionUploading> uploadings = user.onManagementSteps().onOfflineConversionSteps()
                .getUploadings(type, counterId);

        assertThat("вернулся корректный список загрузок", uploadings, Matchers.<Iterable<OfflineConversionUploading>>allOf(
                iterableWithSize(uploadingInfos.get(type).size()),
                containsInAnyOrder(IntStream
                        .range(0, uploadingInfos.get(type).size())
                        .mapToObj(idx -> beanEquivalent(new OfflineConversionUploading()
                                .withId(uploadingInfos.get(type).get(idx).getKey())
                                .withSourceQuantity((long) uploadingInfos.get(type).get(idx).getRight().size())
                                .withLineQuantity((long) uploadingInfos.get(type).get(idx).getRight().size())
                                .withStatus(OfflineConversionUploadingStatus.UPLOADED)
                                .withClientIdType(CLIENT_ID)
                                .withComment(COMMENT)
                        ).withVariation(new DefaultMatchVariation()
                                .forFields("createTime")
                                .useMatcher(notNullValue())
                        ))
                        .collect(toList())
                )
        ));
    }

    @AfterClass
    public static void cleanupClass() {
        ownerUser.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }
}
