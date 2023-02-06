package ru.yandex.autotests.metrika.reportwrappers;

import com.google.common.collect.ImmutableList;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataDrilldownGETSchema;
import ru.yandex.metrika.api.constructor.response.DrillDownRow;
import ru.yandex.metrika.segments.site.parametrization.Attribution;

import java.util.Collections;
import java.util.List;

import static java.util.stream.Collectors.toList;
import static ru.yandex.autotests.metrika.converters.DimensionToHumanReadableStringMapper.dimensionToHumanReadableStringMapper;
import static ru.yandex.autotests.metrika.utils.Utils.extractDimensionValue;
import static ru.yandex.autotests.metrika.utils.Utils.getSlice;

/**
 * Created by omaz on 13.07.16.
 */
public class DrilldownReport extends CommonReport<StatV1DataDrilldownGETSchema> {

    public DrilldownReport(StatV1DataDrilldownGETSchema rawReport) {
        super(rawReport);
    }

    @Override
    public Long getTotalRows() {
        return rawReport.getTotalRows();
    }

    @Override
    public Long getSampleSize() {
        return rawReport.getSampleSize();
    }

    @Override
    public Long getSampleSpace() {
        return rawReport.getSampleSpace();
    }

    @Override
    public Boolean getSampled() {
        return rawReport.getSampled();
    }

    @Override
    public Double getSampleShare() {
        return rawReport.getSampleShare();
    }

    @Override
    public List<String> getSort() {
        return rawReport.getQuery().getSort();
    }

    @Override
    public Boolean getWithConfidence() {
        return rawReport.getWithConfidence();
    }

    @Override
    public Boolean getExcludeInsignificant() {
        return rawReport.getExcludeInsignificant();
    }

    @Override
    public Attribution getAttribution() {
        return rawReport.getQuery().getAttribution();
    }

    @Override
    public List<String> getQueryDimensions() {
        return rawReport.getQuery().getDimensions();
    }

    @Override
    public List<String> getQueryMetrics() {
        return rawReport.getQuery().getMetrics();
    }

    @Override
    public List<List<String>> getDimensions() {
        return rawReport.getData().stream()
                .map(DrillDownRow::getDimension)
                .map(dimensionToHumanReadableStringMapper())
                .map(ImmutableList::of)
                .collect(toList());
    }

    @Override
    public List<List<String>> getDimensionsId() {
        return rawReport.getData().stream()
                .map(DrillDownRow::getDimension)
                .map(d -> (String) extractDimensionValue(d))
                .map(ImmutableList::of)
                .collect(toList());
    }

    @Override
    public List<String> getDimension(String dimensionName) {
        return getDimensions().stream()
                .map(row -> row.get(0))
                .collect(toList());
    }

    @Override
    public List<String> getDimensionId(String dimensionName) {
        return getDimensionsId().stream()
                .map(row -> row.get(0))
                .collect(toList());
    }

    @Override
    public List<List<String>> getDimensionsWithConfidence(String metricName) {
        int metricIndex = getMetricIndex(rawReport.getQuery().getMetrics(), metricName);

        return rawReport.getData().stream()
                .filter(row -> row.getMetricsConfidenceFlags().get(metricIndex))
                .map(DrillDownRow::getDimension)
                .map(dimensionToHumanReadableStringMapper())
                .map(ImmutableList::of)
                .collect(toList());
    }

    @Override
    public List<String> getDimensionWithConfidence(String dimensionName, String metricName) {
        List<List<String>> allDimensions = getDimensionsWithConfidence(metricName);
        return getSlice(allDimensions, 0);
    }

    @Override
    public List<List<List<Double>>> getMetrics() {
        return rawReport.getData().stream()
                .map(r -> r.getMetrics().stream()
                        .map(Collections::singletonList)
                        .collect(toList()))
                .collect(toList());
    }

    @Override
    public List<List<Double>> getMetric(String metricName) {
        return getMetrics().stream()
                .map(row -> row.get(getMetricIndex(rawReport.getQuery().getMetrics(), metricName)))
                .collect(toList());
    }

    @Override
    public List<List<Double>> getTotals() {
        return rawReport.getTotals().stream()
                .map(ImmutableList::of)
                .collect(toList());
    }

    @Override
    public List<List<List<Boolean>>> getConfidenceFlags() {
        return rawReport.getData().stream()
                .map(r -> r.getMetricsConfidenceFlags().stream()
                        .map(Collections::singletonList)
                        .collect(toList()))
                .collect(toList());
    }

    @Override
    public List<List<Boolean>> getConfidenceFlags(String metricName) {
        return getConfidenceFlags().stream()
                .map(row -> row.get(getMetricIndex(rawReport.getQuery().getMetrics(), metricName)))
                .collect(toList());
    }

    @Override
    public List<List<List<Long>>> getConfidenceThreshold() {
        return rawReport.getData().stream()
                .map(r -> r.getMetricsConfidenceThreshold().stream()
                        .map(Collections::singletonList)
                        .collect(toList()))
                .collect(toList());
    }

    @Override
    public List<List<Long>> getConfidenceThreshold(String metricName) {
        return getConfidenceThreshold().stream()
                .map(row -> row.get(getMetricIndex(rawReport.getQuery().getMetrics(), metricName)))
                .collect(toList());
    }
}
