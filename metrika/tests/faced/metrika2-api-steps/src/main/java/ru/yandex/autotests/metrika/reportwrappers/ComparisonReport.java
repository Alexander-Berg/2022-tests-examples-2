package ru.yandex.autotests.metrika.reportwrappers;

import com.google.common.collect.ImmutableList;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataComparisonGETSchema;
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
public class ComparisonReport extends CommonReport<StatV1DataComparisonGETSchema> {

    public ComparisonReport(StatV1DataComparisonGETSchema rawReport) {
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
                .map(row -> row.getDimensions().stream()
                        .map(dimensionToHumanReadableStringMapper())
                        .collect(toList()))
                .collect(toList());
    }

    @Override
    public List<List<String>> getDimensionsId() {
        return rawReport.getData().stream()
                .map(row -> row.getDimensions().stream()
                        .map(d -> (String) extractDimensionValue(d))
                        .collect(toList()))
                .collect(toList());
    }

    @Override
    public List<String> getDimension(String dimensionName) {
        return getDimensions().stream()
                .map(row -> row.get(getDimensionIndex(rawReport.getQuery().getDimensions(), dimensionName)))
                .collect(toList());
    }

    @Override
    public List<String> getDimensionId(String dimensionName) {
        return getDimensionsId().stream()
                .map(row -> row.get(getDimensionIndex(rawReport.getQuery().getDimensions(), dimensionName)))
                .collect(toList());
    }

    @Override
    public List<List<String>> getDimensionsWithConfidence(String metricName) {
        int metricIndex = getMetricIndex(rawReport.getQuery().getMetrics(), metricName);

        return rawReport.getData().stream()
                .filter(row -> row.getMetrics().getAConfidenceFlags().get(metricIndex))
                .map(row -> row.getDimensions().stream()
                        .map(dimensionToHumanReadableStringMapper())
                        .collect(toList()))
                .collect(toList());
    }

    @Override
    public List<String> getDimensionWithConfidence(String dimensionName, String metricName) {
        int dimensionIndex = getDimensionIndex(rawReport.getQuery().getDimensions(), dimensionName);

        List<List<String>> allDimensions = getDimensionsWithConfidence(metricName);

        return getSlice(allDimensions, dimensionIndex);
    }

    @Override
    public List<List<List<Double>>> getMetrics() {
        return rawReport.getData().stream()
                .map(r -> ImmutableList.<List<Double>>builder()
                        .addAll(r.getMetrics().getA().stream()
                                .map(Collections::singletonList)
                                .collect(toList()))
                        .addAll(r.getMetrics().getB().stream()
                                .map(Collections::singletonList)
                                .collect(toList()))
                        .build())
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
        return ImmutableList.<List<Double>>builder()
                .addAll(rawReport.getTotals().getA().stream()
                        .map(Collections::singletonList)
                        .collect(toList()))
                .addAll(rawReport.getTotals().getB().stream()
                        .map(Collections::singletonList)
                        .collect(toList()))
                .build();
    }

    @Override
    public List<List<List<Boolean>>> getConfidenceFlags() {
        return rawReport.getData().stream()
                .map(r -> ImmutableList.<List<Boolean>>builder()
                        .addAll(r.getMetrics().getAConfidenceFlags().stream()
                                .map(Collections::singletonList)
                                .collect(toList()))
                        .addAll(r.getMetrics().getBConfidenceFlags().stream()
                                .map(Collections::singletonList)
                                .collect(toList()))
                        .build())
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
                .map(r -> ImmutableList.<List<Long>>builder()
                        .addAll(r.getMetrics().getAConfidenceThreshold().stream()
                                .map(Collections::singletonList)
                                .collect(toList()))
                        .addAll(r.getMetrics().getBConfidenceThreshold().stream()
                                .map(Collections::singletonList)
                                .collect(toList()))
                        .build())
                .collect(toList());
    }

    @Override
    public List<List<Long>> getConfidenceThreshold(String metricName) {
        return getConfidenceThreshold().stream()
                .map(row -> row.get(getMetricIndex(rawReport.getQuery().getMetrics(), metricName)))
                .collect(toList());
    }
}
