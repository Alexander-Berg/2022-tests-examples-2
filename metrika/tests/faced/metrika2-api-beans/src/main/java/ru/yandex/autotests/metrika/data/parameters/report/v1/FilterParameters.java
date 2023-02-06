package ru.yandex.autotests.metrika.data.parameters.report.v1;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

/**
 * Created by sourx on 27/02/2018.
 */
public class FilterParameters extends AbstractFormParameters {

    @FormParameter("filters")
    private String filters;

    public String getFilters() {
        return filters;
    }

    public void setFilters(String filters) {
        this.filters = filters;
    }

    public FilterParameters withFilters(final String filters) {
        this.filters = filters;
        return this;
    }

    public static FilterParameters filters(String filters) {
        return new FilterParameters().withFilters(filters);
    }
}