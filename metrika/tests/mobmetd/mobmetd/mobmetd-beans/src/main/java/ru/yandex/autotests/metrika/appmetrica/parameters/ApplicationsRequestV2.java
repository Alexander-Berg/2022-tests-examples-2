package ru.yandex.autotests.metrika.appmetrica.parameters;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class ApplicationsRequestV2 extends AbstractFormParameters {

    @FormParameter("include_agency_apps")
    private Boolean includeAgencyApps;

    @FormParameter("sort")
    private AppListV2SortParameter sort = AppListV2SortParameter.name;

    @FormParameter("reverse")
    private boolean reverse;

    @FormParameter("limit")
    private Long limit;

    @FormParameter("offset")
    private Long offset;

    @FormParameter("search_string")
    private String searchString;

    @FormParameter("label_id")
    private Long labelId;

    public Boolean getIncludeAgencyApps() {
        return includeAgencyApps;
    }

    public void setIncludeAgencyApps(Boolean includeAgencyApps) {
        this.includeAgencyApps = includeAgencyApps;
    }

    public ApplicationsRequestV2 withIncludeAgencyApps(Boolean includeAgencyApps) {
        this.includeAgencyApps = includeAgencyApps;
        return this;
    }

    public AppListV2SortParameter getSort() {
        return sort;
    }

    public void setSort(AppListV2SortParameter sort) {
        this.sort = sort;
    }

    public ApplicationsRequestV2 withSort(AppListV2SortParameter sort) {
        this.sort = sort;
        return this;
    }

    public boolean isReverse() {
        return reverse;
    }

    public void setReverse(boolean reverse) {
        this.reverse = reverse;
    }

    public ApplicationsRequestV2 withReverse(boolean reverse) {
        this.reverse = reverse;
        return this;
    }

    public Long getLimit() {
        return limit;
    }

    public void setLimit(Long limit) {
        this.limit = limit;
    }

    public ApplicationsRequestV2 withLimit(Long limit) {
        this.limit = limit;
        return this;
    }

    public Long getOffset() {
        return offset;
    }

    public void setOffset(Long offset) {
        this.offset = offset;
    }

    public ApplicationsRequestV2 withOffset(Long offset) {
        this.offset = offset;
        return this;
    }

    public String getSearchString() {
        return searchString;
    }

    public void setSearchString(String searchString) {
        this.searchString = searchString;
    }

    public ApplicationsRequestV2 withSearchString(String searchString) {
        this.searchString = searchString;
        return this;
    }

    public Long getLabelId() {
        return labelId;
    }

    public void setLabelId(Long labelId) {
        this.labelId = labelId;
    }

    public ApplicationsRequestV2 withLabelId(Long labelId) {
        this.labelId = labelId;
        return this;
    }
}
