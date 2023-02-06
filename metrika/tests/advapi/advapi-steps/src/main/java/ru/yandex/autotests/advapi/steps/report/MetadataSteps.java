package ru.yandex.autotests.advapi.steps.report;

import com.google.common.collect.ImmutableSet;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.apache.commons.lang3.tuple.Pair;
import org.hamcrest.Matcher;
import ru.yandex.advapi.InternalMetadataGETSchema;
import ru.yandex.advapi.InternalMetadataPresetsGETSchema;
import ru.yandex.autotests.advapi.data.metadata.GroupEnum;
import ru.yandex.autotests.advapi.data.metadata.ParametrizationTypeEnum;
import ru.yandex.autotests.advapi.data.metadata.SubTable;
import ru.yandex.autotests.advapi.data.metadata.TableEnum;
import ru.yandex.autotests.advapi.parameters.CommonParameters;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.commons.clients.http.FreeFormParameters;
import ru.yandex.metrika.api.constructor.presets.PresetExternal;
import ru.yandex.metrika.api.constructor.response.DimensionMetaExternal;
import ru.yandex.metrika.api.constructor.response.MetricMetaExternal;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.Collection;
import java.util.Set;
import java.util.function.BiFunction;
import java.util.function.Function;
import java.util.function.Predicate;
import java.util.stream.Stream;

import static java.util.stream.Collectors.toList;
import static ru.yandex.autotests.advapi.parameters.ParametrizationParameters.parametrization;
import static ru.yandex.autotests.advapi.steps.report.MetadataSteps.Predicates.*;

/**
 * Created by konkov on 04.08.2014.
 * Шаги для работы с метаданными
 */
public class MetadataSteps extends BaseReportSteps {

    /**
     * Константы путей к ручкам
     */
    private static class Handles {
        private static final String INTERNAL_METADATA = "/internal/metadata";
        private static final String INTERNAL_METADATA_PRESETS = "/internal/metadata/presets";
        private static final String INTERNAL_METADATA_PRESET = "/internal/metadata/preset";
    }

    /**
     * Константы захардкоженных списков
     */
    private static class Lists {

        public static final Set<String> ADMETRIKA_METRICS = ImmutableSet.of(
                "am:e:allClicks",
                "am:e:allRenders",
                "am:e:clicks",
                "am:e:clicksPlanCompletion",
                "am:e:cpa<goal_id>",
                "am:e:cpa<goal_id>PostClick",
                "am:e:cpa<goal_id>PostView",
                "am:e:cpc",
                "am:e:cpcPlanCompletion",
                "am:e:cpm",
                "am:e:cpmPlanCompletion",
                "am:e:cpmu",
                "am:e:ctr",
                "am:e:ctrPlanCompletion",
                "am:e:ecommerce<currency>Revenue",
                "am:e:ecommerce<currency>RevenuePostClick",
                "am:e:ecommerce<currency>RevenuePostView",
                "am:e:fraudClicks",
                "am:e:fraudClicksPercent",
                "am:e:fraudRenders",
                "am:e:fraudRendersPercent",
                "am:e:fullscreenVideo",
                "am:e:fullscreenVideoPercent",
                "am:e:goal<goal_id>Conversion",
                "am:e:goal<goal_id>ConversionPostClick",
                "am:e:goal<goal_id>ConversionPostView",
                "am:e:goal<goal_id>Reaches",
                "am:e:goal<goal_id>ReachesPostClick",
                "am:e:goal<goal_id>ReachesPostView",
                "am:e:impressions",
                "am:e:measurableRenders",
                "am:e:measurableRendersPercent",
                "am:e:renderFrequency",
                "am:e:renders",
                "am:e:rendersPlanCompletion",
                "am:e:users",
                "am:e:videoComplete",
                "am:e:videoCompletePercent",
                "am:e:videoCompleteVisible",
                "am:e:videoCompleteVisiblePercent",
                "am:e:videoFirstQuartiles",
                "am:e:videoFirstQuartilesPercent",
                "am:e:videoFirstQuartilesVisible",
                "am:e:videoFirstQuartilesVisiblePercent",
                "am:e:videoMeasurableRendersPercent",
                "am:e:videoRenders",
                "am:e:videoSecondQuartiles",
                "am:e:videoSecondQuartilesPercent",
                "am:e:videoSecondQuartilesVisible",
                "am:e:videoSecondQuartilesVisiblePercent",
                "am:e:videoStarts",
                "am:e:videoStartsPercent",
                "am:e:videoStartsVisible",
                "am:e:videoStartsVisiblePercent",
                "am:e:videoThirdQuartiles",
                "am:e:videoThirdQuartilesPercent",
                "am:e:videoThirdQuartilesVisible",
                "am:e:videoThirdQuartilesVisiblePercent",
                "am:e:videoVisibility",
                "am:e:videoWithSound",
                "am:e:videoWithSoundPercent",
                "am:e:visibility"
        );

        public static final Set<String> ADMETRIKA_DIMENSIONS = ImmutableSet.of(
                "am:e:advType",
                "am:e:ageInterval",
                "am:e:browser",
                "am:e:creative",
                "am:e:datePeriod<group>",
                "am:e:deviceType",
                "am:e:domain",
                "am:e:gender",
                "am:e:income",
                "am:e:interest2d1",
                "am:e:interest2d2",
                "am:e:interest2d3",
                "am:e:operatingSystem",
                "am:e:operatingSystemRoot",
                "am:e:placement",
                "am:e:regionArea",
                "am:e:regionCity",
                "am:e:regionCitySize",
                "am:e:regionContinent",
                "am:e:regionCountry",
                "am:e:regionDistrict",
                "am:e:site"
        );
    }

    /**
     * предикаты для употребления со степами получения списков метрик, измерений, пресетов
     */
    public static class Predicates {

        /**
         * @return предикат - "любой", над любым типом
         */
        public static <T> Predicate<T> any() {
            return m -> true;
        }

        /**
         * @param matcher Hamcrest матчер, которому делегируется логика предиката
         * @return предикат над метаданными метрики, делегирующий вычисление в матчер над именем измерения
         */
        public static Predicate<MetricMetaExternal> metric(Matcher<String> matcher) {
            return m -> matcher.matches(m.getDim());
        }

        /**
         * @param predicate предикат над именем метрики
         * @return предикат над метаданными метрики, делегирующий вычисление предикату над именем метрики
         */
        public static Predicate<MetricMetaExternal> metric(Predicate<String> predicate) {
            return m -> predicate.test(m.getDim());
        }

        /**
         * @param matcher Hamcrest матчер, которому делегируется логика предиката
         * @return предикат над метаданными измерения, делегирующий вычисление в матчер над именем измерения
         */
        public static Predicate<DimensionMetaExternal> dimension(Matcher<String> matcher) {
            return m -> matcher.matches(m.getDim());
        }

        /**
         * @param predicate предикат над именем измерения
         * @return предикат над метаданными измерения, делегирующий вычисление предикату над именем измерения
         */
        public static Predicate<DimensionMetaExternal> dimension(Predicate<String> predicate) {
            return m -> predicate.test(m.getDim());
        }

        /**
         * @param matcher Hamcrest матчер, которому делегируется логика предиката
         * @return предикат над строкой, делегирующий вычисление матчеру
         */
        public static Predicate<String> matches(Matcher<String> matcher) {
            return matcher::matches;
        }

        /**
         * @param table таблица, неймспейс
         * @return предикат принадлежности имени метрики/измерения указанной таблице
         */
        public static Predicate<String> table(TableEnum table) {
            return s -> s.startsWith(table.getNamespace());
        }

        /**
         * @return предикат принадлежности имени метрики/измерения известной таблице
         */
        public static Predicate<String> knownTable() {
            return s -> TableEnum.stream().anyMatch(t -> s.startsWith(t.getNamespace()));
        }

        /**
         * @return предикат того, что метрика/измерение не содержит параметров
         */
        public static Predicate<String> nonParameterized() {
            return m -> ParametrizationTypeEnum.stream()
                    .allMatch(p -> !m.contains(p.getPlaceholder()));
        }

        /**
         * @param parametrization параметр метрики/измерения (параметризация)
         * @return предикат того, что метрика/измерение содержит указанный параметр
         */
        public static Predicate<String> parameterized(ParametrizationTypeEnum parametrization) {
            return m -> m.contains(parametrization.getPlaceholder());
        }

        /**
         * @return предикат того, что метрика поддерживает режим доверия к данным
         */
        public static Predicate<MetricMetaExternal> supportConfidence() {
            return m -> m.getSupportConfidence() != null && m.getSupportConfidence();
        }

        public static Predicate<String> admetrika() {
            return m -> Lists.ADMETRIKA_METRICS.contains(m)
                    || Lists.ADMETRIKA_DIMENSIONS.contains(m);
        }

        /**
         * @return предикат того, что измерение содержит url
         */
        public static Predicate<DimensionMetaExternal> url() {
            return m -> (StringUtils.equals(m.getType(), "url")
                    || StringUtils.equals(m.getType(), "url-part"))
                    && !m.getDim().endsWith("Hash");
        }

        public static class Dimension {
            /**
             * @param subTable подтаблица (множество)
             * @return предикат принадлежности измерения множеству
             */
            public static Predicate<DimensionMetaExternal> subTable(SubTable subTable) {
                return m -> StringUtils.equals(m.getSubTable(), subTable.toString());
            }
        }

        public static class Metric {
            /**
             * @param subTable подтаблица (множество)
             * @return предикат принадлежности измерения множеству
             */
            public static Predicate<MetricMetaExternal> subTable(SubTable subTable) {
                return m -> StringUtils.equals(m.getSubTable(), subTable.toString());
            }
        }

        public static class Preset {
            /**
             * @param table таблица, неймспейс
             * @return предикат принадлежности пресета к указанной таблице
             */
            public static Predicate<PresetExternal> table(TableEnum table) {
                return p -> StringUtils.equals(p.getTable(), table.getValue());
            }
        }
    }

    public static class Modifiers {
        public static <T> BiFunction<T, FreeFormParameters,
                Stream<Pair<T, FreeFormParameters>>> setParameters(Function<T, IFormParameters> createFunction) {
            return (m, p) ->
                    Stream.of(ImmutablePair.of(m, FreeFormParameters.makeParameters()
                            .append(p).append(createFunction.apply(m))));
        }

        public static <T> BiFunction<T, FreeFormParameters,
                Stream<Pair<T, FreeFormParameters>>> setParameters(IFormParameters parameters) {
            return setParameters(t -> parameters);
        }

        public static <T> BiFunction<T, Object[], Stream<Pair<T, Object[]>>> addParameters(Object[][] params) {
            return (m, p) ->
                    Stream.of(params).map(c -> ImmutablePair.of(m, c));
        }

        public static <T> BiFunction<T, FreeFormParameters,
                Stream<Pair<T, FreeFormParameters>>> addGroups() {
            return (m, p) ->
                    Stream.of(GroupEnum.values())
                            .map(g -> ImmutablePair.of(m,
                                    FreeFormParameters.makeParameters()
                                            .append(p)
                                            .append(parametrization().withGroup(g))));
        }
    }

    @Step("Получить метрики, удовлетворяющие предикату")
    public Collection<String> getMetrics(Predicate<String> predicate) {
        return getMetricsRaw(metric(predicate));
    }

    @Step("Получить метрики, удовлетворяющие предикату")
    public Collection<String> getMetricsRaw(Predicate<MetricMetaExternal> predicate) {
        return getMetricsMeta(predicate)
                .stream()
                .map(MetricMetaExternal::getDim)
                .collect(toList());
    }

    @Step("Получить метаданные метрик, удовлетворяющие предикату")
    public Collection<MetricMetaExternal> getMetricsMeta(Predicate<MetricMetaExternal> predicate) {
        return getResponse(Handles.INTERNAL_METADATA, new CommonParameters().withTable("events"))
                .readResponse(InternalMetadataGETSchema.class)
                .getMetadata()
                .getMetrics()
                .stream()
                .filter(metric(knownTable()).and(predicate))
                .collect(toList());
    }

    @Step("Получить группировки, удовлетворяющие предикату")
    public Collection<String> getDimensions(Predicate<String> predicate) {
        return getDimensionsRaw(dimension(predicate));
    }

    @Step("Получить группировки, удовлетворяющие предикату")
    public Collection<String> getDimensionsRaw(Predicate<DimensionMetaExternal> predicate) {
        return getDimensionsMeta(predicate)
                .stream()
                .map(DimensionMetaExternal::getDim)
                .collect(toList());
    }

    @Step("Получить метаданные группировок, удовлетворяющих предикату")
    public Collection<DimensionMetaExternal> getDimensionsMeta(Predicate<DimensionMetaExternal> predicate) {
        return getResponse(Handles.INTERNAL_METADATA, new CommonParameters().withTable("events"))
                .readResponse(InternalMetadataGETSchema.class)
                .getMetadata()
                .getDimensions()
                .stream()
                .filter(dimension(knownTable()).and(predicate))
                .collect(toList());
    }

    @Step("Получить пресеты удовлетворяющие предикату")
    public Collection<PresetExternal> getPresetsMeta(Predicate<PresetExternal> predicate) {
        return getResponse(Handles.INTERNAL_METADATA_PRESETS)
                .readResponse(InternalMetadataPresetsGETSchema.class)
                .getPresets()
                .values()
                .stream()
                .filter(predicate)
                .collect(toList());
    }

    @Step("Получить пресеты удовлетворяющие предикату")
    public Collection<String> getPresetsRaw(Predicate<PresetExternal> predicate) {
        return getResponse(Handles.INTERNAL_METADATA_PRESETS)
                .readResponse(InternalMetadataPresetsGETSchema.class)
                .getPresets()
                .values()
                .stream()
                .filter(predicate)
                .map(PresetExternal::getName)
                .collect(toList());
    }
}

