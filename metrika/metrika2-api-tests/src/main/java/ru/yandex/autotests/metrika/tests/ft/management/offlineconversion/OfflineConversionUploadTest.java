package ru.yandex.autotests.metrika.tests.ft.management.offlineconversion;

import java.util.Collection;
import java.util.function.BiFunction;
import java.util.function.Function;
import java.util.stream.Stream;

import com.google.common.collect.ImmutableList;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.apache.commons.lang3.tuple.Pair;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.irt.testutils.beandiffer.matchvariation.DefaultMatchVariation;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.data.management.v1.offlineconversion.OfflineConversionType;
import ru.yandex.autotests.metrika.data.management.v1.offlineconversion.OfflineConversionUploadingData;
import ru.yandex.autotests.metrika.data.parameters.management.v1.OfflineConversionParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.offlineconversion.OfflineConversionUploading;
import ru.yandex.metrika.api.management.client.external.offlineconversion.OfflineConversionUploadingClientIdType;
import ru.yandex.metrika.api.management.client.external.offlineconversion.OfflineConversionUploadingStatus;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static com.google.common.collect.ImmutableList.of;
import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.management.v1.offlineconversion.OfflineConversionType.BASIC;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.offlineconversion.OfflineConversionUploadingTestData.createBaseContent;
import static ru.yandex.autotests.metrika.tests.ft.management.offlineconversion.OfflineConversionUploadingTestData.createContentWithAllValuesEmpty;
import static ru.yandex.autotests.metrika.tests.ft.management.offlineconversion.OfflineConversionUploadingTestData.createContentWithChangedHeaderCase;
import static ru.yandex.autotests.metrika.tests.ft.management.offlineconversion.OfflineConversionUploadingTestData.createContentWithEmptyLines;
import static ru.yandex.autotests.metrika.tests.ft.management.offlineconversion.OfflineConversionUploadingTestData.createContentWithEmptyNonOptionalValues;
import static ru.yandex.autotests.metrika.tests.ft.management.offlineconversion.OfflineConversionUploadingTestData.createContentWithEmptyOptionalValues;
import static ru.yandex.autotests.metrika.tests.ft.management.offlineconversion.OfflineConversionUploadingTestData.createContentWithIncorrectValues;
import static ru.yandex.autotests.metrika.tests.ft.management.offlineconversion.OfflineConversionUploadingTestData.createContentWithNonWordCharsInHeader;
import static ru.yandex.autotests.metrika.tests.ft.management.offlineconversion.OfflineConversionUploadingTestData.createContentWithShuffledColumns;
import static ru.yandex.autotests.metrika.tests.ft.management.offlineconversion.OfflineConversionUploadingTestData.createContentWithSpecialValues;
import static ru.yandex.autotests.metrika.tests.ft.management.offlineconversion.OfflineConversionUploadingTestData.createContentWithUntrimmedValues;
import static ru.yandex.autotests.metrika.tests.ft.management.offlineconversion.OfflineConversionUploadingTestData.createContentWithWhitespaceNonOptionalValues;
import static ru.yandex.autotests.metrika.tests.ft.management.offlineconversion.OfflineConversionUploadingTestData.createContentWithWhitespaceOptionalValues;
import static ru.yandex.autotests.metrika.tests.ft.management.offlineconversion.OfflineConversionUploadingTestData.createContentWithoutOptionalColumns;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.metrika.api.management.client.external.offlineconversion.OfflineConversionUploadingClientIdType.CLIENT_ID;
import static ru.yandex.metrika.api.management.client.external.offlineconversion.OfflineConversionUploadingClientIdType.USER_ID;
import static ru.yandex.metrika.api.management.client.external.offlineconversion.OfflineConversionUploadingClientIdType.YCLID;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.OFFLINE_CONVERSION)
@Title("Загрузка офлайн конверсий")
@RunWith(Parameterized.class)
public class OfflineConversionUploadTest<T extends OfflineConversionUploadingData> {

    private static UserSteps user;
    private static Long counterId;

    @Parameterized.Parameter
    public OfflineConversionType<T> type;

    @Parameterized.Parameter(1)
    public OfflineConversionUploadingClientIdType clientIdType;

    @Parameterized.Parameter(2)
    public String name;

    @Parameterized.Parameter(3)
    public String content;

    @Parameterized.Parameters(name = "тип {0}, {2}, тип идентификатора клиента {1}")
    public static Collection<Object[]> getParameters() {
        return MultiplicationBuilder.<OfflineConversionType<?>, OfflineConversionType<?>, Object[]>builder(
                ImmutableList.copyOf(OfflineConversionType.values()), () -> new Object[]{})

                // all cases for basic type
                .apply(BASIC::equals, (type, typeObjects) -> MultiplicationBuilder.<OfflineConversionUploadingClientIdType, OfflineConversionUploadingClientIdType, Object[]>builder(

                        ImmutableList.copyOf(OfflineConversionUploadingClientIdType.values()), () -> new Object[]{})

                        // all cases for USER_ID
                        .apply(USER_ID::equals, cases((builder, clientIdType) ->
                                builder
                                        .add(createBaseContent(type, clientIdType))
                                        .add(createContentWithChangedHeaderCase(type, clientIdType))
                                        .add(createContentWithNonWordCharsInHeader(type, clientIdType))
                                        .add(createContentWithShuffledColumns(type, clientIdType))
                                        .add(createContentWithEmptyLines(type, clientIdType))
                                        .add(createContentWithUntrimmedValues(type, clientIdType))
                                        .add(createContentWithEmptyOptionalValues(type, clientIdType))
                                        .add(createContentWithWhitespaceOptionalValues(type, clientIdType))
                                        .add(createContentWithoutOptionalColumns(type, clientIdType))
                                        .add(createContentWithAllValuesEmpty(type, clientIdType))
                                        .addAll(createContentWithEmptyNonOptionalValues(type, clientIdType))
                                        .addAll(createContentWithWhitespaceNonOptionalValues(type, clientIdType))
                                        .addAll(createContentWithSpecialValues(type, clientIdType))
                                        .addAll(createContentWithIncorrectValues(type, clientIdType)))
                        )

                        // specific cases for CLIENT_ID
                        .apply(CLIENT_ID::equals, cases((builder, clientIdType) ->
                                builder
                                        .add(createBaseContent(type, clientIdType))
                                        .addAll(createContentWithEmptyNonOptionalValues(type, clientIdType, of(type.getClientIdColumn())))
                                        .addAll(createContentWithWhitespaceNonOptionalValues(type, clientIdType, of(type.getClientIdColumn())))
                                        .addAll(createContentWithSpecialValues(type, clientIdType, of(type.getClientIdColumn())))
                                        .addAll(createContentWithIncorrectValues(type, clientIdType, of(type.getClientIdColumn()))))
                        )

                        // specific cases for YCLID
                        .apply(YCLID::equals, cases((builder, clientIdType) ->
                                builder
                                        .add(createBaseContent(type, clientIdType))
                                        .addAll(createContentWithEmptyNonOptionalValues(type, clientIdType, of(type.getYclidColumn())))
                                        .addAll(createContentWithWhitespaceNonOptionalValues(type, clientIdType, of(type.getYclidColumn())))
                                        .addAll(createContentWithSpecialValues(type, clientIdType, of(type.getYclidColumn())))
                                        .addAll(createContentWithIncorrectValues(type, clientIdType, of(type.getYclidColumn()))))
                        )

                        .build(Function.identity(), Function.identity())
                        .stream()
                        .map(objs -> ImmutablePair.of(type, objs))
                )

                // specific cases for other types
                .apply(type -> !BASIC.equals(type), (type, objects) -> ImmutableList.<Object[]>builder()
                        .add(createBaseContent(type, USER_ID))
                        .addAll(createContentWithEmptyNonOptionalValues(type, USER_ID, type.getAdditionalColumns()))
                        .addAll(createContentWithWhitespaceNonOptionalValues(type, USER_ID, type.getAdditionalColumns()))
                        .addAll(createContentWithSpecialValues(type, USER_ID, type.getAdditionalColumns()))
                        .addAll(createContentWithIncorrectValues(type, USER_ID, type.getAdditionalColumns()))
                        .build()
                        .stream()
                        .map(objs -> ImmutableList.builder().add(USER_ID).add(objs).build().toArray())
                        .map(objs -> ImmutablePair.of(type, objs)))
                .build(Function.identity(), Function.identity());
    }

    private static BiFunction<OfflineConversionUploadingClientIdType, Object[], Stream<Pair<OfflineConversionUploadingClientIdType, Object[]>>> emptyCases() {
        return cases((builder, clientIdType) -> builder);
    }

    private static BiFunction<OfflineConversionUploadingClientIdType, Object[], Stream<Pair<OfflineConversionUploadingClientIdType, Object[]>>> cases(
            BiFunction<ImmutableList.Builder<Object[]>, OfflineConversionUploadingClientIdType, ImmutableList.Builder<Object[]>> buildFunction
    ) {
        return (clientIdType, clientIdTypeObjects) -> buildFunction.apply(ImmutableList.<Object[]>builder(), clientIdType)
                .build()
                .stream()
                .map(objs -> ImmutablePair.of(clientIdType, objs));
    }

    @BeforeClass
    public static void init() {
        user = new UserSteps();
        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter())
                .getId();
    }

    @AfterClass
    public static void cleanup() {
        user.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }

    @Test
    public void checkUpload() {
        OfflineConversionUploading uploading = user.onManagementSteps().onOfflineConversionSteps()
                .upload(type, counterId, content, BASIC.equals(type) ?
                        new OfflineConversionParameters().withClientIdType(clientIdType).withIgnoreVisitJoinThreshold(1) :
                        new OfflineConversionParameters().withClientIdType(clientIdType).withIgnoreCallsVisitJoinThreshold(1));

        assertThat(
                "загрузка корректно создалась",
                uploading,
                beanEquivalent(new OfflineConversionUploading()
                        .withLineQuantity(1L)
                        .withStatus(OfflineConversionUploadingStatus.UPLOADED)
                        .withClientIdType(clientIdType)
                ).withVariation(new DefaultMatchVariation()
                        .forFields("id", "createTime")
                        .useMatcher(notNullValue())
                )
        );
    }
}
