package ru.yandex.autotests.metrika.data.parameters.management.v1;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.autotests.metrika.data.management.v1.segments.enums.SegmentsSortEnum;

/**
 * Created by konkov on 02.11.2015.
 */
public class SegmentsStatParameters extends AbstractFormParameters {

    @FormParameter("offset")
    private Integer offset;

    @FormParameter("per_page")
    private Integer perPage;

    @FormParameter("sort")
    private SegmentsSortEnum sort;

    @FormParameter("reverse")
    private Boolean reverse;

    public Integer getOffset() {
        return offset;
    }

    public void setOffset(Integer offset) {
        this.offset = offset;
    }

    public Integer getPerPage() {
        return perPage;
    }

    public void setPerPage(Integer perPage) {
        this.perPage = perPage;
    }

    public SegmentsSortEnum getSort() {
        return sort;
    }

    public void setSort(SegmentsSortEnum sort) {
        this.sort = sort;
    }

    public Boolean getReverse() {
        return reverse;
    }

    public void setReverse(Boolean reverse) {
        this.reverse = reverse;
    }

    public SegmentsStatParameters withReverse(final Boolean reverse) {
        this.reverse = reverse;
        return this;
    }

    public SegmentsStatParameters withSort(final SegmentsSortEnum sort) {
        this.sort = sort;
        return this;
    }

    public SegmentsStatParameters withPerPage(final Integer perPage) {
        this.perPage = perPage;
        return this;
    }

    public SegmentsStatParameters withOffset(final Integer offset) {
        this.offset = offset;
        return this;
    }

}
