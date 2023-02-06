package ru.yandex.autotests.advapi.parameters;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class SitesManagementParameters extends CommonParameters {

    @FormParameter("filter")
    private String filter;

    public String getFilter() {
        return filter;
    }

    public void setFilter(String filter) {
        this.filter = filter;
    }

    public SitesManagementParameters withFilter(String filter) {
        this.filter = filter;
        return this;
    }
}
