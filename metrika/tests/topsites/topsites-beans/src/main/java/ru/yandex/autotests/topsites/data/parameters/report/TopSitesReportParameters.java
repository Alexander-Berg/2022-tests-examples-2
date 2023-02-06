package ru.yandex.autotests.topsites.data.parameters.report;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;

import java.util.List;

import static ru.yandex.autotests.topsites.data.parameters.ParamUtils.joinToString;

public class TopSitesReportParameters extends TopSitesBaseParameters {

    @FormParameter("limit")
    private Integer limit;

    @FormParameter("offset")
    private Integer offset;

    @FormParameter("type")
    private String type;

    @FormParameter("thematic")
    private String thematic;

    @FormParameter("regions")
    private String regions;

    @FormParameter("incomes")
    private String incomes;

    @FormParameter("device_categories")
    private String deviceCategories;

    @FormParameter("genders")
    private String genders;

    @FormParameter("ages")
    private String ages;

    @FormParameter("media_holding_id")
    private String mediaHoldingId;

    public Integer getLimit() {
        return limit;
    }

    public void setLimit(Integer limit) {
        this.limit = limit;
    }

    public TopSitesReportParameters withLimit(Integer limit) {
        this.limit = limit;
        return this;
    }

    public Integer getOffset() {
        return offset;
    }

    public void setOffset(Integer offset) {
        this.offset = offset;
    }

    public TopSitesReportParameters withOffset(Integer offset) {
        this.offset = offset;
        return this;
    }

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }

    public TopSitesReportParameters withType(String type) {
        this.type = type;
        return this;
    }

    public String getThematic() {
        return thematic;
    }

    public void setThematic(List<String> thematic) {
        this.thematic = joinToString(thematic);
    }

    public TopSitesReportParameters withThematic(List<String> thematic) {
        setThematic(thematic);
        return this;
    }

    public String getRegions() {
        return regions;
    }

    public void setRegions(List<Integer> regions) {
        this.regions = joinToString(regions);
    }

    public TopSitesReportParameters withRegions(List<Integer> regions) {
        setRegions(regions);
        return this;
    }

    public String getIncomes() {
        return incomes;
    }

    public void setIncomes(List<Income> incomes) {
        this.incomes = joinToString(incomes);
    }

    public TopSitesReportParameters withIncomes(List<Income> incomes) {
        setIncomes(incomes);
        return this;
    }

    public String getDeviceCategories() {
        return deviceCategories;
    }

    public void setDeviceCategories(List<DeviceCategory> deviceCategories) {
        this.deviceCategories = joinToString(deviceCategories);
    }

    public TopSitesReportParameters withDeviceCategories(List<DeviceCategory> deviceCategories) {
        setDeviceCategories(deviceCategories);
        return this;
    }

    public String getGenders() {
        return genders;
    }

    public void setGenders(List<Gender> genders) {
        this.genders = joinToString(genders);
    }

    public TopSitesReportParameters withGenders(List<Gender> genders) {
        setGenders(genders);
        return this;
    }

    public String getAges() {
        return ages;
    }

    public void setAges(List<Age> ages) {
        this.ages = joinToString(ages);
    }

    public TopSitesReportParameters withAges(List<Age> ages) {
        setAges(ages);
        return this;
    }

    public String getMediaHoldingId() {
        return mediaHoldingId;
    }

    public void setMediaHoldingId(String mediaHoldingId) {
        this.mediaHoldingId = mediaHoldingId;
    }

    public TopSitesReportParameters withMediaHolding(String mediaHoldingId) {
        setMediaHoldingId(mediaHoldingId);
        return this;
    }
}
