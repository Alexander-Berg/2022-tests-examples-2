package ru.yandex.autotests.metrika.data.parameters.report.v1;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

/**
 * Created by konkov on 05.03.2015.
 */
public class ConfidenceParameters extends AbstractFormParameters {

    @FormParameter("with_confidence")
    private Boolean withConfidence;

    @FormParameter("exclude_insignificant")
    private Boolean excludeInsignificant;

    @FormParameter("confidence_level")
    private Double confidenceLevel;

    @FormParameter("max_deviation")
    private Double maxDeviation;

    public boolean getWithConfidence() {
        return withConfidence;
    }

    public void setWithConfidence(Boolean withConfidence) {
        this.withConfidence = withConfidence;
    }

    public Boolean getExcludeInsignificant() {
        return excludeInsignificant;
    }

    public void setExcludeInsignificant(Boolean excludeInsignificant) {
        this.excludeInsignificant = excludeInsignificant;
    }

    public Double getConfidenceLevel() {
        return confidenceLevel;
    }

    public void setConfidenceLevel(Double confidenceLevel) {
        this.confidenceLevel = confidenceLevel;
    }

    public Double getMaxDeviation() {
        return maxDeviation;
    }

    public void setMaxDeviation(Double maxDeviation) {
        this.maxDeviation = maxDeviation;
    }

    public ConfidenceParameters withWithConfidence(final Boolean withConfidence) {
        this.withConfidence = withConfidence;
        return this;
    }

    public ConfidenceParameters withExcludeInsignificant(final Boolean excludeInsignificant) {
        this.excludeInsignificant = excludeInsignificant;
        return this;
    }

    public ConfidenceParameters withConfidenceLevel(final Double confidenceLevel) {
        this.confidenceLevel = confidenceLevel;
        return this;
    }

    public ConfidenceParameters withMaxDeviation(final Double maxDeviation) {
        this.maxDeviation = maxDeviation;
        return this;
    }


}
