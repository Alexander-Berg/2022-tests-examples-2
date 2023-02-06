package ru.yandex.autotests.metrika.reportwrappers;

import org.apache.commons.lang3.NotImplementedException;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataBytimeGETSchema;
import ru.yandex.metrika.api.constructor.response.DynamicRow;
import ru.yandex.metrika.segments.site.parametrization.Attribution;

import java.util.List;

import static java.util.stream.Collectors.toList;
import static ru.yandex.autotests.metrika.converters.DimensionToHumanReadableStringMapper.dimensionToHumanReadableStringMapper;
import static ru.yandex.autotests.metrika.utils.Utils.extractDimensionValue;

/**
 * Created by omaz on 13.07.16.
 */
public class BytimeReport extends CommonReport<StatV1DataBytimeGETSchema> {

    public BytimeReport(StatV1DataBytimeGETSchema rawReport) {
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
        throw new NotImplementedException("confidence");
    }

    @Override
    public List<String> getDimensionWithConfidence(String dimensionName, String metricName) {
        throw new NotImplementedException("confidence");
    }

    @Override
    public List<List<List<Double>>> getMetrics() {
        return rawReport.getData().stream()
                .map(DynamicRow::getMetrics)
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
        return rawReport.getTotals();
    }

    @Override
    public List<List<List<Boolean>>> getConfidenceFlags() {
        throw new NotImplementedException("confidence");
    }

    @Override
    public List<List<Boolean>> getConfidenceFlags(String metricName) {
        throw new NotImplementedException("confidence");
    }

    @Override
    public List<List<List<Long>>> getConfidenceThreshold() {
        throw new NotImplementedException("confidence");
    }

    @Override
    public List<List<Long>> getConfidenceThreshold(String metricName) {
        throw new NotImplementedException("confidence");
    }
}
