package ru.yandex.autotests.metrika.data.parameters.report.v1;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;

/**
 * @author zgmnkv
 */
public class CrossDeviceReportParameters extends TableReportParameters {

    @FormParameter("idle_period")
    private Integer idlePeriod;

    @FormParameter("conversion_period")
    private Integer conversionPeriod;

    @FormParameter("visit_ranges")
    private String visitRanges;

    @FormParameter("ecommerce")
    private Boolean ecommerce;

    public Integer getIdlePeriod() {
        return idlePeriod;
    }

    public void setIdlePeriod(Integer idlePeriod) {
        this.idlePeriod = idlePeriod;
    }

    public CrossDeviceReportParameters withIdlePeriod(Integer idlePeriod) {
        this.idlePeriod = idlePeriod;
        return this;
    }

    public Integer getConversionPeriod() {
        return conversionPeriod;
    }

    public void setConversionPeriod(Integer conversionPeriod) {
        this.conversionPeriod = conversionPeriod;
    }

    public CrossDeviceReportParameters withConversionPeriod(Integer conversionPeriod) {
        this.conversionPeriod = conversionPeriod;
        return this;
    }

    public String getVisitRanges() {
        return visitRanges;
    }

    public void setVisitRanges(String visitRanges) {
        this.visitRanges = visitRanges;
    }

    public CrossDeviceReportParameters withVisitRanges(String visitRanges) {
        this.visitRanges = visitRanges;
        return this;
    }

    public Boolean getEcommerce() {
        return ecommerce;
    }

    public void setEcommerce(Boolean ecommerce) {
        this.ecommerce = ecommerce;
    }

    public CrossDeviceReportParameters withEcommerce(Boolean ecommerce) {
        this.ecommerce = ecommerce;
        return this;
    }
}
