package ru.yandex.autotests.metrika.appmetrica.utils;

import org.apache.commons.lang3.builder.EqualsBuilder;
import org.apache.commons.lang3.builder.HashCodeBuilder;
import ru.yandex.metrika.mobmet.model.redirect.AdwordsConversion;
import ru.yandex.metrika.mobmet.model.redirect.Campaign;

import static java.lang.String.format;

/**
 * Значение конверсии для партнера AdWords
 * <p>
 * Created by graev on 14/03/2017.
 */
public final class AdwordsConversionValues {
    private final String conversionId;

    private final String conversionLabel;

    private final String linkId;

    public static AdwordsConversionValues of(Campaign entity) {
        return new AdwordsConversionValues(
                entity.getAdwordsConversionId(),
                entity.getAdwordsConversionLabel(),
                entity.getAdwordsLinkId());
    }

    public static AdwordsConversionValues of(AdwordsConversion entity) {
        return new AdwordsConversionValues(entity.getConversionId(), entity.getConversionLabel(), entity.getLinkId());
    }

    private AdwordsConversionValues(String conversionId, String conversionLabel, String linkId) {
        this.conversionId = conversionId;
        this.conversionLabel = conversionLabel;
        this.linkId = linkId;
    }

    public static AdwordsConversionValues linkId(String linkId) {
        return new AdwordsConversionValues(null, null, linkId);
    }

    public static AdwordsConversionValues semiNew(String conversionId, String conversionLabel, String linkId) {
        return new AdwordsConversionValues(conversionId, conversionLabel, linkId);
    }

    public static AdwordsConversionValues deprecated(String conversionId, String conversionLabel) {
        return new AdwordsConversionValues(conversionId, conversionLabel, null);
    }

    public String getConversionId() {
        return conversionId;
    }

    public String getConversionLabel() {
        return conversionLabel;
    }

    public String getLinkId() {
        return linkId;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;

        if (o == null || getClass() != o.getClass()) return false;

        AdwordsConversionValues that = (AdwordsConversionValues) o;

        return new EqualsBuilder()
                .append(conversionId, that.conversionId)
                .append(conversionLabel, that.conversionLabel)
                .append(linkId, that.linkId)
                .isEquals();
    }

    @Override
    public int hashCode() {
        return new HashCodeBuilder(17, 37)
                .append(conversionId)
                .append(conversionLabel)
                .append(linkId)
                .toHashCode();
    }

    @Override
    public String toString() {
        return format("AdwordsConversion(%s, %s, %s)", conversionId, conversionLabel, linkId);
    }
}
