package ru.yandex.autotests.metrika.appmetrica.tests.b2b.misc;

import com.google.common.base.Preconditions;
import com.google.common.collect.ImmutableList;
import org.hamcrest.Matcher;
import org.hamcrest.core.IsAnything;
import org.hamcrest.core.StringEndsWith;
import org.hamcrest.core.StringStartsWith;
import ru.yandex.autotests.metrika.appmetrica.data.Application;
import ru.yandex.autotests.metrika.appmetrica.data.Tables;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.exceptions.AppMetricaException;
import ru.yandex.autotests.metrika.appmetrica.parameters.TableReportParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.MetadataSteps;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.metrika.api.constructor.response.DimensionMetaExternal;
import ru.yandex.metrika.api.constructor.response.MetricMetaExternal;

import java.util.*;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import static java.lang.String.format;
import static java.util.Arrays.asList;
import static java.util.stream.Collectors.toList;
import static org.apache.commons.lang3.RandomUtils.nextInt;
import static org.hamcrest.Matchers.*;
import static org.hamcrest.core.IsAnything.anything;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.*;
import static ru.yandex.autotests.metrika.appmetrica.data.Tables.*;
import static ru.yandex.autotests.metrika.appmetrica.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties.apiProperties;
import static ru.yandex.autotests.metrika.appmetrica.steps.MetadataSteps.Predicates.Dimension.*;
import static ru.yandex.autotests.metrika.appmetrica.tests.b2b.misc.B2BAppParams.app;


public class B2BParameters {

    private static final UserSteps onTesting = UserSteps.builder()
            .withBaseUrl(apiProperties().getApiTesting())
            .withUser(Users.SUPER_LIMITED)
            .build();

    private static final B2BMtmobgigaParams MTMOBGIGA_PARAMS =
            new B2BMtmobgigaParams(app(YANDEX_REALTY))
                    // в clicks и в tracking_events семплинг работает по разному,
                    // можно вернуть дефолтный семплинг после релиза
                    .withClickEventsApp(app(YANDEX_REALTY).withAccuracy("1.00"))
                    .withReengagementEventsApp(app(BERU).withAccuracy("1.00"))
                    .withMobmetCampaignsApp(app(YANDEX_REALTY).withAccuracy("1.00"))
                    .withAnrEventsApp(app(KINOPOISK))
                    .withRevenueApp(app(YANDEX_MUSIC))
                    // в методе buildQuery настройки ecom-а переопределяются на sample
                    // то есть мы не тестируем еком с нормальными данными
                    .withEcomApp(app(YANDEX_MUSIC))
                    .withSkadApp(app(YANDEX_BROWSER_IOS)
                            .withDate("2021-08-20")
                            .withAccuracy("1.00"));

    // Пока сгенерировали тестовые ecom данные только для яндекс музыки.
    // Потом заменим на настоящие, когда кто-нибудь начнёт их присылать.
    private static final ImmutableList<String> YANDEX_MUSIC_CURRENCIES =
            ImmutableList.of("gas", "wood", "work", "electricity", "illegal");

    public static final List<Matcher<String>> NO_DATA_DIMENSIONS = ImmutableList.<Matcher<String>>builder()
            // Нет данных просто потому что нет. Наверное надо выбрать другое приложение для тестирования
            // или просто обновить даты
            .add(StringEndsWith.endsWith("crashEnvironmentKey"))
            .add(StringEndsWith.endsWith("crashEnvironmentValue"))
            .add(StringEndsWith.endsWith("errorEnvironmentKey"))
            .add(StringEndsWith.endsWith("errorEnvironmentValue"))
            .add(StringEndsWith.endsWith("anrEnvironmentKey"))
            .add(StringEndsWith.endsWith("anrEnvironmentValue"))
            .add(StringEndsWith.endsWith("ym:d:pushOpens"))
            .add(StringEndsWith.endsWith("ym:d:crashesCount"))
            .add(StringEndsWith.endsWith("limitAdTracking"))
            .add(StringEndsWith.endsWith("ym:pc:messageLangOrEmpty"))
            .add(StringEndsWith.endsWith("limitAdTracking"))
            // По-хорошему нужны приложения у которых одновременно есть и iOS и Android и они везде символизируют
            // креши
            .add(StringEndsWith.endsWith("ym:anr:anrBinaryName"))
            .add(StringEndsWith.endsWith("ym:anr2:anrBinaryName"))
            .add(StringEndsWith.endsWith("ym:er:errorBinaryName"))
            .add(StringEndsWith.endsWith("ym:er2:errorBinaryName"))
            .add(StringEndsWith.endsWith("ym:cr:crashBinaryName"))
            .add(StringEndsWith.endsWith("ym:cr2:crashBinaryName"))
            .add(StringEndsWith.endsWith("ym:er:errorFileName"))
            .add(StringEndsWith.endsWith("ym:er2:errorFileName"))
            // MOBMET-12293, баг в ClickHouse
            .add(StringEndsWith.endsWith("ym:r2:regionCityName"))
            // Может быть надо добавить .withTypeNullValue у атрибута, но пока нети нормальных данных
            .add(StringEndsWith.endsWith("ecomQuantityUnit"))
            .add(StringEndsWith.endsWith("ecomReferrerType"))
            // При желании можно повсюду делать вилку на iOS/Android приложение и тестировать
            // рекламный идентификатор/подбирать для тестов приложение с двумя платформами,
            // но эта группировка "как бы" NDA, поэтому не так страшно.
            .add(StringEndsWith.endsWith("ym:er:iosIFA"))
            .add(StringEndsWith.endsWith("ym:er2:iosIFA"))
            .add(StringEndsWith.endsWith("ym:er2:googleAID"))
            .add(StringEndsWith.endsWith("ym:cr:iosIFA"))
            .add(StringEndsWith.endsWith("ym:cr2:iosIFA"))
            .add(StringEndsWith.endsWith("ym:anr:iosIFA"))
            .add(StringEndsWith.endsWith("ym:anr2:iosIFA"))
            .add(StringEndsWith.endsWith("ym:o:iosIFA"))
            .add(StringEndsWith.endsWith("ym:pc:iosIFA"))
            .add(StringEndsWith.endsWith("ym:re:iosIFA"))
            .add(StringEndsWith.endsWith("ym:re:googleAID"))
            .add(StringEndsWith.endsWith("ym:rets:iosIFA"))
            .add(StringEndsWith.endsWith("ym:rets:googleAID"))
            .add(StringEndsWith.endsWith("ym:r:googleAID"))
            .add(StringEndsWith.endsWith("ym:r2:googleAID"))
            .add(StringEndsWith.endsWith("ym:ec:googleAID"))
            .add(StringEndsWith.endsWith("ym:ec2:googleAID"))
            .add(StringEndsWith.endsWith("ym:m:iosIFA"))
            .add(StringEndsWith.endsWith("ym:uf:iosIFA"))
            .add(StringEndsWith.endsWith("ym:sf:iosIFA"))
            // Из-за слабой популярности WinPhone не существует проверочных данных
            .add(StringEndsWith.endsWith("ym:o:operatingSystemMinorVersionInfo"))
            .add(StringEndsWith.endsWith("ym:pc:operatingSystemMinorVersionInfo"))
            .add(StringEndsWith.endsWith("ym:i:operatingSystemMinorVersionInfo"))
            .add(StringEndsWith.endsWith("ym:re:operatingSystemMinorVersionInfo"))
            .add(StringEndsWith.endsWith("ym:rets:operatingSystemMinorVersionInfo"))
            .add(StringEndsWith.endsWith("ym:r:operatingSystemMinorVersionInfo"))
            .add(StringEndsWith.endsWith("ym:r2:operatingSystemMinorVersionInfo"))
            .add(StringEndsWith.endsWith("ym:ec:operatingSystemMinorVersionInfo"))
            .add(StringEndsWith.endsWith("ym:ec2:operatingSystemMinorVersionInfo"))
            // И о новых крешах под Windows тоже ничего не известно
            .add(StringEndsWith.endsWith("ym:cr:operatingSystemMinorVersionInfo"))
            .add(StringEndsWith.endsWith("ym:cr2:operatingSystemMinorVersionInfo"))
            .add(StringEndsWith.endsWith("ym:er:operatingSystemMinorVersionInfo"))
            .add(StringEndsWith.endsWith("ym:er2:operatingSystemMinorVersionInfo"))
            .add(StringEndsWith.endsWith("ym:anr:operatingSystemMinorVersionInfo"))
            .add(StringEndsWith.endsWith("ym:anr2:operatingSystemMinorVersionInfo"))
            // В проде пока что искуственные тестовые данные, на которых сложно сделать рабочий b2b-тест.
            .add(StringStartsWith.startsWith("ym:ec:"))
            .add(StringStartsWith.startsWith("ym:ec2:"))
            // Пока нет данных с этими атрибутами skadnetwork
            .add(StringEndsWith.endsWith("ym:sk:adNetworkAdName"))
            .add(StringEndsWith.endsWith("ym:sk:adNetworkAdID"))
            .add(StringEndsWith.endsWith("ym:sk:adNetworkCampaignID"))
            .add(StringEndsWith.endsWith("ym:sk:adNetworkCampaignName"))
            .add(StringEndsWith.endsWith("ym:sk:adNetworkDate"))
            .add(StringEndsWith.endsWith("ym:sk:adNetworkDateTime"))
            .add(StringEndsWith.endsWith("ym:sk:adNetworkAdsetID"))
            .add(StringEndsWith.endsWith("ym:sk:adNetworkAdsetName"))
            .add(StringEndsWith.endsWith("ym:sk:fidelityType"))
            .add(StringEndsWith.endsWith("ym:sk:cvEventType"))
            .add(StringEndsWith.endsWith("ym:sk:cvEventLabel"))
            .add(StringEndsWith.endsWith("ym:sk:cvEventType"))
            .add(StringEndsWith.endsWith("ym:sk:cvEcomType"))
            .add(StringEndsWith.endsWith("ym:sk:cvCurrency"))
            // https://st.yandex-team.ru/MOBMET-15111#6135eb38eabf5310f9880583
            .add(StringEndsWith.endsWith("ym:r:paramsLevel4"))
            .add(StringEndsWith.endsWith("ym:r:paramsLevel5"))
            .add(StringEndsWith.endsWith("ym:r2:paramsLevel4"))
            .add(StringEndsWith.endsWith("ym:r2:paramsLevel5"))
            .build();

    /**
     * Мы часто меняем какие-то атрибуты. После нового релиза такие отменённые тесты надо включать назад.
     * То есть в идеале эта секция должна быть пустой.
     */
    public static Collection<Object[]> ignoredParamsAsRecentlyChanged() {
        return asList(new Object[][]{
                {startsWith("ym:a:"), anything(), anything(), anything()},
        });
    }

    /**
     * Хак, чтобы сломанные атрибуты по возможности тянулись из одного места
     */
    public static boolean isIgnored(String dimension, String metric) {
        return isNoDataDimension(dimension) ||
                ignoredParamsAsRecentlyChanged().stream()
                        .map(matchers -> Arrays.stream(matchers).map(Matcher.class::cast).collect(Collectors.toList()))
                        .peek(matchers -> Preconditions.checkArgument(matchers.get(2) instanceof IsAnything))
                        .anyMatch(matchers -> matchers.get(0).matches(dimension) && matchers.get(1).matches(metric));
    }

    public static boolean isNoDataDimension(String dimension) {
        return NO_DATA_DIMENSIONS.stream().anyMatch(m -> m.matches(dimension));
    }

    public static Collection<Object[]> createFor(DimensionsDomain dimensionsDomain, Collection<Tables> tables) {
        Collection<MetricMetaExternal> metrics = onTesting.onMetadataSteps().getMetricsIn(tables);
        Collection<DimensionMetaExternal> dimensions = onTesting.onMetadataSteps().getDimensionsIn(tables);
        return createDimensionAndMetricsTestParams(metrics, dimensions, dimensionsDomain);
    }

    public static Collection<Object[]> createWithout(DimensionsDomain dimensionsDomain, Collection<Tables> exceptTables) {
        Collection<MetricMetaExternal> metrics = onTesting.onMetadataSteps().getMetricsExcept(exceptTables);
        Collection<DimensionMetaExternal> dimensions = onTesting.onMetadataSteps().getDimensionsExcept(exceptTables);
        return createDimensionAndMetricsTestParams(metrics, dimensions, dimensionsDomain);
    }

    public static Collection<Object[]> createDimensionsForProfiles(DimensionsDomain dimensionsDomain) {
        Collection<MetricMetaExternal> metrics = onTesting.onMetadataSteps().getMetricsIn(asList(PROFILES, DEVICES));
        Collection<DimensionMetaExternal> dimensions = onTesting.onMetadataSteps().getDimensionsIn(asList(PROFILES, DEVICES));
        return createDimensionTestParams(metrics, dimensions, dimensionsDomain);
    }

    public static Collection<Object[]> createDimensionsWithout(DimensionsDomain dimensionsDomain,
                                                               Collection<Tables> exceptTables) {
        Collection<MetricMetaExternal> metrics = onTesting.onMetadataSteps().getMetricsExcept(exceptTables);
        Collection<DimensionMetaExternal> dimensions = onTesting.onMetadataSteps().getDimensionsExcept(exceptTables);
        return createDimensionTestParams(metrics, dimensions, dimensionsDomain);
    }

    /**
     * @return коллекция массивов из четырёх элементов: api-имя группировки,
     * api-имя метрики, пустой фильтр и параметры запроса stat/v1/data
     */
    public static Collection<Object[]> createDimensionAndMetricsTestParams(Collection<MetricMetaExternal> metrics,
                                                                           Collection<DimensionMetaExternal> dimensions,
                                                                           DimensionsDomain dimensionsDomain) {
        return Stream.concat(
                        createMetricsParams(metrics, dimensions).stream(),
                        createDimensionParams(metrics, dimensions, dimensionsDomain).stream())
                .distinct()
                .map(B2BParameters::buildTestParams)
                .collect(toList());
    }

    private static Collection<Object[]> createDimensionTestParams(Collection<MetricMetaExternal> metrics,
                                                                  Collection<DimensionMetaExternal> dimensions,
                                                                  DimensionsDomain dimensionsDomain) {
        return createDimensionParams(metrics, dimensions, dimensionsDomain).stream()
                .map(B2BParameters::buildTestParams)
                .collect(toList());
    }

    /**
     * Проходим по всем метрикам и создаём параметры stat/v1/data
     */
    private static Collection<B2BParamsMeta> createMetricsParams(Collection<MetricMetaExternal> metrics,
                                                                 Collection<DimensionMetaExternal> dimensions) {
        return metrics.stream()
                .map(metric -> dimensions.stream()
                        .filter(MetadataSteps.Predicates.Dimension.sameTable(metric))
                        .filter(d -> !isNoDataDimension(d.getDim()))
                        .findFirst()
                        .map(d -> new B2BParamsMeta(d, metric))
                        .orElse(null))
                .filter(Objects::nonNull)
                .collect(Collectors.toList());
    }

    /**
     * Проходим по всем dimension и создаём параметры stat/v1/data
     */
    private static Collection<B2BParamsMeta> createDimensionParams(Collection<MetricMetaExternal> metrics,
                                                                   Collection<DimensionMetaExternal> dimensions,
                                                                   DimensionsDomain dimensionsDomain) {
        return dimensions.stream()
                .filter(dimensionsDomain::test)
                .filter(d -> !isNoDataDimension(d.getDim()))
                .map(d -> {
                    MetricMetaExternal metric = metrics.stream()
                            .filter(MetadataSteps.Predicates.Metric.sameTable(d))
                            .findFirst()
                            .orElseThrow(() -> new AppMetricaException(
                                    format("Для группировки %s не найдена метрика", d.getDim())));
                    return new B2BParamsMeta(d, metric);
                })
                .collect(Collectors.toList());
    }

    private static TableReportParameters buildQuery(B2BParamsMeta params) {
        DimensionMetaExternal dim = params.getDimension();
        MetricMetaExternal metric = params.getMetric();

        B2BAppParams appParams = chooseApplication(params.getDimension(), metric);

        String dimAsString = getDim(appParams.getApplication(), dim);
        String metricAsString = getMetricDim(appParams.getApplication(), metric);

        TableReportParameters parameters = new TableReportParameters()
                .withDimension(dimAsString)
                .withMetric(metricAsString)
                .withId(appParams.getApplication())
                .withAccuracy(appParams.getAccuracy())
                .withDate1(appParams.getDate1())
                .withDate2(appParams.getDate2())
                .withLimit(10)
                .withLang("ru")
                .withRequestDomain("com");

        // Далее прочие хаки для крайних случаев

        // Для воронок добавляем условие воронки, чтобы в тестах не ворошить merge таблицу целиком
        if (tables(Tables.USER_FUNNELS_JOIN).test(dim)) {
            parameters.withFunnelPattern("" +
                    "cond(ym:uft, eventType=='EVENT_AD_INSTALL' AND sessionType=='foreground') " +
                    "cond(ym:uft, eventType=='EVENT_START' AND sessionType=='foreground')");
        }
        if (tables(SESSION_FUNNELS_JOIN).test(dim)) {
            parameters.withFunnelPattern("" +
                    "cond(ym:sft, eventType=='EVENT_AD_INSTALL' AND sessionType=='foreground') " +
                    "cond(ym:sft, eventType=='EVENT_START' AND sessionType=='foreground')");
        }

        if (dimension(allOf(
                anyOf(startsWith("ym:ce:"), startsWith("ym:ce2:")),
                anyOf(endsWith(":paramsLevel3"), endsWith(":paramsLevel4"), endsWith(":paramsLevel5")))).test(dim)) {
            return parameters
                    .withId(MTS_SERVICE)
                    .withAccuracy(B2BAppParams.DEFAULT_ACCURACY);
        }
        if (dimension(anyOf(startsWith("ym:r:params"), startsWith("ym:r2:params"))).test(dim)) {
            return parameters
                    .withId(BURGER_KING)
                    .withAccuracy("1.0");
        }
        if (dimension(endsWith(":isRevenueVerified")).test(dim)) {
            return parameters
                    .withId(MUNDUS)
                    .withAccuracy("1.0");
        }
        if (dimension(endsWith(":operatingSystemMinorVersionInfo")).test(dim)) {
            if (tables(REENGAGEMENTS, REMARKETING_TRAFFIC_SOURCES, MOBMET_CAMPAIGNS, TRAFFIC_SOURCES, CLICKS).test(dim)) {
                return parameters
                        .withId(MTS_SERVICE)
                        .withAccuracy("1.0");
            } else {
                return parameters
                        .withId(MTS_SERVICE)
                        .withAccuracy(B2BAppParams.DEFAULT_ACCURACY);
            }
        }
        if (dimension(endsWith(":eventLabelComment")).test(dim)) {
            return parameters
                    .withId(PUSH_SAMPLE)
                    .withAccuracy("1.00")
                    .withDate1("2019-12-20")
                    .withDate2("2019-12-20");
        }
        if (tables(Tables.POSTBACKS).test(dim)) {
            return parameters
                    .withId(YANDEX_TOLOKA)
                    .withAccuracy("1")
                    .withDate1(apiProperties().getPostbackStartDate())
                    .withDate2(apiProperties().getPostbackEndDate());
        }
        if (tables(Tables.REENGAGEMENTS, Tables.REMARKETING_TRAFFIC_SOURCES).test(dim)) {
            B2BAppParams reApp = MTMOBGIGA_PARAMS.getReengagementEventsApp();
            return parameters
                    .withId(reApp.getApplication())
                    .withAccuracy(reApp.getAccuracy())
                    .withDate1(reApp.getDate1())
                    .withDate2(reApp.getDate2());
        }
        if (tables(Tables.PROFILES, Tables.DEVICES).test(dim)) {
            return parameters.withAccuracy("0.01");
        }
        if (tables(ECOMMERCE_EVENTS, ECOMMERCE_EVENTS_JOIN).test(dim)) {
            return parameters
                    .withId(SAMPLE)
                    .withAccuracy("1")
                    .withDate1(apiProperties().getEcomStartDate())
                    .withDate2(apiProperties().getEcomEndDate());
        }

        return parameters;
    }

    private static String getDim(Application application, DimensionMetaExternal dim) {
        if (dim.getParameter() == null) {
            return dim.getDim();
        }
        Optional<String> customParametrized = getCustomParametrized(application, dim.getDim());
        return customParametrized.orElse(AttributeParam.getParametrizedDim(dim));
    }

    private static String getMetricDim(Application application, MetricMetaExternal metric) {
        if (metric.getParameters().isEmpty()) {
            return metric.getDim();
        }
        Optional<String> customParametrized = getCustomParametrized(application, metric.getDim());
        return customParametrized.orElse(AttributeParam.getParametrizedMetric(metric));
    }

    private static Optional<String> getCustomParametrized(Application application, String dim) {
        // Пока сгенерировали тестовые ecom данные только для яндекс музыки. Подставляем сгенерённые значения.
        // Потом заменим на настоящие, когда кто-нибудь начнёт их присылать.
        if (dim.startsWith(ECOMMERCE_EVENTS.getNamespace()) || dim.startsWith(ECOMMERCE_EVENTS_JOIN.getNamespace())) {
            if (dim.contains("<app_currency>")) {
                return Optional.of(AttributeParam.getParametrizedDim(dim, "app_currency",
                        YANDEX_MUSIC_CURRENCIES.get(nextInt(0, YANDEX_MUSIC_CURRENCIES.size()))));
            }

            if (dim.endsWith(":ecomCategoryParamValue<param_key>")) {
                return Optional.of(AttributeParam.getParametrizedDim(dim, "param_key", "cp_1"));
            }

            if (dim.endsWith(":ecomOrderParamValue<param_key>")) {
                return Optional.of(AttributeParam.getParametrizedDim(dim, "param_key", "op_1"));
            }

            if (dim.endsWith(":ecomOrderItemParamValue<param_key>")) {
                return Optional.of(AttributeParam.getParametrizedDim(dim, "param_key", "ip_1"));
            }
        }

        return Optional.empty();
    }

    private static B2BAppParams chooseApplication(DimensionMetaExternal dim, MetricMetaExternal met) {
        if (tables(Tables.DEEPLINKS).test(dim)) {
            return MTMOBGIGA_PARAMS.getOpenEventsApp();
        }
        if (tables(Tables.CRASH_EVENTS, Tables.CRASH_EVENTS_JOIN)
                .or(dimension(startsWith("ym:ge:crashDump")))
                .test(dim)) {
            return MTMOBGIGA_PARAMS.getCrashEventsApp();
        }
        if (tables(Tables.ERROR_EVENTS, Tables.ERROR_EVENTS_JOIN).test(dim) ||
                metric(anyOf(endsWith(":errors"), endsWith(":crashes"))).test(met)) {
            return MTMOBGIGA_PARAMS.getErrorEventsApp();
        }
        if (tables(Tables.ANR_EVENTS, Tables.ANR_EVENTS_JOIN).test(dim)) {
            return MTMOBGIGA_PARAMS.getAnrEventsApp();
        }
        if (tables(Tables.PUSH_CAMPAIGNS).test(dim)) {
            return MTMOBGIGA_PARAMS.getPushCampaignEventsApp();
        }
        if (tables(Tables.CLICKS).test(dim)) {
            return MTMOBGIGA_PARAMS.getClickEventsApp();
        }
        if (tables(Tables.INSTALLATIONS).test(dim)) {
            return MTMOBGIGA_PARAMS.getInstallationsApp();
        }
        if (tables(Tables.MOBMET_CAMPAIGNS, TRAFFIC_SOURCES).test(dim)) {
            return MTMOBGIGA_PARAMS.getMobmetCampaignsApp();
        }
        if (tables(Tables.REVENUE_EVENTS, Tables.REVENUE_EVENTS_JOIN).test(dim)) {
            return MTMOBGIGA_PARAMS.getRevenueApp();
        }
        if (tables(Tables.ECOMMERCE_EVENTS, Tables.ECOMMERCE_EVENTS_JOIN).test(dim)) {
            return MTMOBGIGA_PARAMS.getEcomApp();
        }
        if (tables(Tables.REENGAGEMENTS, Tables.REMARKETING_TRAFFIC_SOURCES).test(dim)) {
            return MTMOBGIGA_PARAMS.getReengagementEventsApp();
        }
        if (tables(SKADNETWORK_POSTBACKS).test(dim)) {
            return MTMOBGIGA_PARAMS.getSkadApp();
        }
        return MTMOBGIGA_PARAMS.getDefaultApplication();
    }

    private static Object[] buildTestParams(B2BParamsMeta params) {
        TableReportParameters parameters = buildQuery(params);
        return new Object[]{
                params.getDimension().getDim(),
                params.getMetric().getDim(),
                makeParameters().append(parameters),
                parameters.getId().toString()
        };
    }

    /**
     * Область определения тест сьюта (по группировкам)
     */
    public enum DimensionsDomain {
        ALL_DIMENSIONS {
            @Override
            public boolean test(DimensionMetaExternal dimensionMeta) {
                return true;
            }
        },
        FILTERABLE_DIMENSIONS {
            @Override
            public boolean test(DimensionMetaExternal dimensionMeta) {
                return dimensionMeta.getAllowFilters() == null || dimensionMeta.getAllowFilters();
            }
        };

        public abstract boolean test(DimensionMetaExternal dimensionMeta);
    }
}
