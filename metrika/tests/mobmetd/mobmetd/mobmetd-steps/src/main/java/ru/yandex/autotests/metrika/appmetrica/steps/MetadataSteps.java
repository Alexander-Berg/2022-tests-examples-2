package ru.yandex.autotests.metrika.appmetrica.steps;

import org.apache.commons.lang3.tuple.ImmutablePair;
import org.apache.commons.lang3.tuple.Pair;
import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1MetadataConstructorDocumentedAttributesApiGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1MetadataConstructorDocumentedMetricsApiGETSchema;
import ru.yandex.autotests.metrika.appmetrica.data.Table;
import ru.yandex.autotests.metrika.appmetrica.data.Tables;
import ru.yandex.autotests.metrika.appmetrica.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.MetadataSteps.Predicates.Dimension;
import ru.yandex.autotests.metrika.appmetrica.steps.MetadataSteps.Predicates.Metric;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution;
import ru.yandex.metrika.api.constructor.response.DimensionMetaExternal;
import ru.yandex.metrika.api.constructor.response.MetricMetaExternal;

import java.net.URL;
import java.util.Arrays;
import java.util.Collection;
import java.util.function.BiFunction;
import java.util.function.Function;
import java.util.function.Predicate;
import java.util.stream.Stream;

import static java.util.stream.Collectors.toList;
import static ru.yandex.autotests.metrika.appmetrica.data.Tables.fromNamespace;
import static ru.yandex.autotests.metrika.appmetrica.steps.MetadataSteps.Predicates.any;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.ALLOW;

/**
 * Created by konkov on 04.05.2016.
 */
public class MetadataSteps extends AppMetricaBaseSteps {


    public MetadataSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @ParallelExecution(ALLOW)
    public Collection<DimensionMetaExternal> getAllDimensions() {
        return getDimensions(any());
    }

    @ParallelExecution(ALLOW)
    public Collection<DimensionMetaExternal> getDimensionsIn(Collection<Tables> tables) {
        return getDimensions(Dimension.tables(tables));
    }

    @ParallelExecution(ALLOW)
    public Collection<DimensionMetaExternal> getDimensionsExcept(Collection<Tables> tables) {
        return getDimensions(Dimension.tables(tables).negate());
    }

    @ParallelExecution(ALLOW)
    public Collection<DimensionMetaExternal> getDimensions(Predicate<DimensionMetaExternal> predicate) {
        return get(StatV1MetadataConstructorDocumentedAttributesApiGETSchema.class,
                "/stat/v1/metadata/constructor_documented_attributes_api").getAttributes().stream()
                .filter(predicate)
                .collect(toList());
    }

    @ParallelExecution(ALLOW)
    public Collection<MetricMetaExternal> getAllMetrics() {
        return getMetrics(any());
    }

    @ParallelExecution(ALLOW)
    public Collection<MetricMetaExternal> getMetricsIn(Collection<Tables> tables) {
        return getMetrics(Metric.tables(tables));
    }

    @ParallelExecution(ALLOW)
    public Collection<MetricMetaExternal> getMetricsExcept(Collection<Tables> exceptTables) {
        return getMetrics(Metric.tables(exceptTables).negate());
    }

    @ParallelExecution(ALLOW)
    public Collection<MetricMetaExternal> getMetrics(Predicate<MetricMetaExternal> predicate) {
        return get(StatV1MetadataConstructorDocumentedMetricsApiGETSchema.class,
                "/stat/v1/metadata/constructor_documented_metrics_api").getMetrics().stream()
                .filter(predicate)
                .collect(toList());
    }

    public static class Predicates {

        public static <T> Predicate<T> any() {
            return m -> true;
        }

        public static <T> Predicate<T> or(Predicate<T> p1, Predicate<T> p2) {
            return param -> p1.test(param) || p2.test(param);
        }

        public static class Metric {

            public static Predicate<MetricMetaExternal> knownTable() {
                return m -> Stream.of(Tables.values()).anyMatch(t -> m.getDim().startsWith(t.getNamespace()));
            }

            public static Predicate<MetricMetaExternal> table(Table table) {
                return m -> m.getDim().startsWith(table.getNamespace());
            }

            public static Predicate<MetricMetaExternal> tables(Collection<Tables> tables) {
                return m -> tables.stream().anyMatch(table -> m.getDim().startsWith(table.getNamespace()));
            }

            public static Predicate<MetricMetaExternal> sameTable(DimensionMetaExternal dimension) {
                return table(fromNamespace(dimension.getDim()));
            }
        }

        public static class Dimension {
            public static Predicate<DimensionMetaExternal> knownTable() {
                return m -> Stream.of(Tables.values()).anyMatch(t -> m.getDim().startsWith(t.getNamespace()));
            }

            public static Predicate<DimensionMetaExternal> table(Table table) {
                return m -> m.getDim().startsWith(table.getNamespace());
            }

            public static Predicate<DimensionMetaExternal> tables(Collection<Tables> tables) {
                return m -> tables.stream().anyMatch(table -> m.getDim().startsWith(table.getNamespace()));
            }

            public static Predicate<DimensionMetaExternal> tables(Tables... tables) {
                return m -> Arrays.stream(tables).anyMatch(table -> m.getDim().startsWith(table.getNamespace()));
            }

            public static Predicate<DimensionMetaExternal> sameTable(MetricMetaExternal metric) {
                return table(fromNamespace(metric.getDim()));
            }

            public static Predicate<DimensionMetaExternal> dimension(Matcher<String> matcher) {
                return m -> matcher.matches(m.getDim());
            }

            public static Predicate<MetricMetaExternal> metric(Matcher<String> matcher) {
                return m -> matcher.matches(m.getDim());
            }
        }

    }

    public static class Modifiers {
        public static BiFunction<MetricMetaExternal, FreeFormParameters,
                Stream<Pair<MetricMetaExternal, FreeFormParameters>>> setMetricParameters(IFormParameters parameters) {
            return (m, p) ->
                    Stream.of(ImmutablePair.of(m, FreeFormParameters.makeParameters().append(p).append(parameters)));
        }

        public static BiFunction<DimensionMetaExternal, FreeFormParameters,
                Stream<Pair<DimensionMetaExternal, FreeFormParameters>>> setDimensionParameters(IFormParameters parameters) {
            return (d, p) ->
                    Stream.of(ImmutablePair.of(d, FreeFormParameters.makeParameters().append(p).append(parameters)));
        }

        public static BiFunction<MetricMetaExternal, FreeFormParameters,
                Stream<Pair<MetricMetaExternal, FreeFormParameters>>> setMetricParameter(Function<MetricMetaExternal, IFormParameters> converter) {
            return (m, p) ->
                    Stream.of(ImmutablePair.of(m, FreeFormParameters.makeParameters().append(p).append(converter.apply(m))));
        }

        public static BiFunction<DimensionMetaExternal, FreeFormParameters,
                Stream<Pair<DimensionMetaExternal, FreeFormParameters>>> setDimensionParameter(Function<DimensionMetaExternal, IFormParameters> converter) {
            return (d, p) ->
                    Stream.of(ImmutablePair.of(d, FreeFormParameters.makeParameters().append(p).append(converter.apply(d))));
        }

    }
}
