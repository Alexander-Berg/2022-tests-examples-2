package ru.yandex.autotests.metrika.data.parameters;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.BytimeReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ComparisonReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.data.report.v1.enums.GroupEnum;

import java.util.function.BiFunction;
import java.util.function.Function;

/**
 * Created by konkov on 17.08.2016.
 */
public final class ParametersUtils {
    private ParametersUtils() {}

    public static BiFunction<String, String, IFormParameters> dateParameters() {
        return (date1, date2) ->
                new TableReportParameters()
                        .withDate1(date1)
                        .withDate2(date2);
    }

    public static BiFunction<String, String, IFormParameters> comparisonDateParameters() {
        return (date1, date2) ->
                new ComparisonReportParameters()
                        .withDate1_a(date1)
                        .withDate2_a(date2)
                        .withDate1_b(date1)
                        .withDate2_b(date2);
    }

    public static BiFunction<String, String, IFormParameters> segmentAdateParameters() {
        return (date1, date2) ->
                new ComparisonReportParameters()
                        .withDate1_a(date1)
                        .withDate2_a(date2);
    }

    public static BiFunction<String, String, IFormParameters> segmentBdateParameters() {
        return (date1, date2) ->
                new ComparisonReportParameters()
                        .withDate1_b(date1)
                        .withDate2_b(date2);
    }

    public static BiFunction<String, String, IFormParameters> byTimeDateParameters() {
        return (date1, date2) ->
                new BytimeReportParameters()
                        .withDate1(date1)
                        .withDate2(date2)
                        .withGroup(GroupEnum.ALL);
    }

    public static Function<String, IFormParameters> filtersParameters() {
        return (filters) ->
                new TableReportParameters()
                        .withFilters(filters);
    }

    public static Function<String, IFormParameters> comparisonFiltersParameters() {
        return (filters) ->
                new ComparisonReportParameters()
                        .withFilters_a(filters)
                        .withFilters_b(filters);
    }
}
