package ru.yandex.autotests.metrika.tests.ft.management.yclidconversion;

import java.util.Collection;
import java.util.List;
import java.util.stream.IntStream;
import java.util.stream.Stream;

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
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.management.v1.offlineconversion.OfflineConversionUploadingData;
import ru.yandex.autotests.metrika.data.management.v1.yclidconversion.YclidConversionUploadingData;
import ru.yandex.autotests.metrika.data.parameters.management.v1.OfflineConversionParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.offlineconversion.OfflineConversionUploading;
import ru.yandex.metrika.api.management.client.external.offlineconversion.OfflineConversionUploadingStatus;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static com.google.common.collect.ImmutableList.of;
import static java.util.stream.Collectors.toList;
import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.common.users.Users.MANAGER;
import static ru.yandex.autotests.metrika.data.common.users.Users.MANAGER_DIRECT;
import static ru.yandex.autotests.metrika.data.common.users.Users.SUPER_USER;
import static ru.yandex.autotests.metrika.data.common.users.Users.SUPPORT;
import static ru.yandex.autotests.metrika.data.common.users.Users.USER_DELEGATE_PERMANENT;
import static ru.yandex.autotests.metrika.data.common.users.Users.USER_DELEGATOR;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.yclidconversion.YclidConversionUploadingTestData.createBaseData1Row;
import static ru.yandex.autotests.metrika.tests.ft.management.yclidconversion.YclidConversionUploadingTestData.createBaseData2Rows;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.YCLID_CONVERSION)
@Title("Получение загрузок yclid конверсий")
@RunWith(Parameterized.class)
public class YclidConversionUploadingGetTest<T extends OfflineConversionUploadingData> {

    private static final String COMMENT = RandomUtils.getString(20);

    private static final List<List<YclidConversionUploadingData>> DATA = of(
            createBaseData1Row(),
            createBaseData2Rows()
    );

    private static UserSteps ownerUser;
    private static Long counterId;
    private static List<Pair<Long, List<YclidConversionUploadingData>>> uploadingInfo;
    @Parameterized.Parameter
    public User userParam;
    private UserSteps user;

    @Parameterized.Parameters(name = "Пользователь {0}")
    public static Collection<Object[]> createParameters() {
        return Stream.of(SUPER_USER, SUPPORT, MANAGER, MANAGER_DIRECT, USER_DELEGATE_PERMANENT, USER_DELEGATOR)
                .map(u -> new Object[]{u})
                .collect(toList());
    }

    @BeforeClass
    public static void initClass() {
        ownerUser = new UserSteps().withUser(USER_DELEGATOR);
        counterId = ownerUser.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter())
                .getId();

        uploadingInfo = DATA.stream()
                .map(data -> ImmutablePair.of(
                        ownerUser.onManagementSteps().onYclidConversionSteps()
                                .upload(counterId, data, new OfflineConversionParameters()
                                        .withIgnoreVisitJoinThreshold(1)
                                        .withComment(COMMENT)
                                )
                                .getId(),
                        data
                ))
                .collect(toList());
    }

    @AfterClass
    public static void cleanupClass() {
        ownerUser.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }

    @Before
    public void init() {
        user = new UserSteps().withUser(userParam);
    }

    @Test
    public void checkGetSingle() {
        Long id = uploadingInfo.get(0).getKey();
        List<YclidConversionUploadingData> data = uploadingInfo.get(0).getValue();

        OfflineConversionUploading uploading = user.onManagementSteps().onYclidConversionSteps()
                .getUploading(counterId, id);

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
        List<OfflineConversionUploading> uploadings = user.onManagementSteps().onYclidConversionSteps()
                .getUploadings(counterId);

        assertThat("вернулся корректный список загрузок", uploadings, Matchers.<Iterable<OfflineConversionUploading>>allOf(
                Matchers.iterableWithSize(uploadingInfo.size()),
                Matchers.containsInAnyOrder(IntStream
                        .range(0, uploadingInfo.size())
                        .mapToObj(idx -> beanEquivalent(new OfflineConversionUploading()
                                .withId(uploadingInfo.get(idx).getKey())
                                .withSourceQuantity((long) uploadingInfo.get(idx).getRight().size())
                                .withLineQuantity((long) uploadingInfo.get(idx).getRight().size())
                                .withStatus(OfflineConversionUploadingStatus.UPLOADED)
                                .withComment(COMMENT)
                        ).withVariation(new DefaultMatchVariation()
                                .forFields("createTime")
                                .useMatcher(notNullValue())
                        ))
                        .collect(toList())
                )
        ));
    }
}
