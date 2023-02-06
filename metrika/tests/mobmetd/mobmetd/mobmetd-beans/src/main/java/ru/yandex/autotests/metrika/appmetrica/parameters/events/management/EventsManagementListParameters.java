package ru.yandex.autotests.metrika.appmetrica.parameters.events.management;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.autotests.metrika.appmetrica.parameters.TSEventParameters;

public class EventsManagementListParameters extends TSEventParameters {

    @FormParameter("only_filtered")
    private Boolean onlyFiltered;

    public Boolean getOnlyFiltered() {
        return onlyFiltered;
    }

    public void setOnlyFiltered(Boolean onlyFiltered) {
        this.onlyFiltered = onlyFiltered;
    }

    public EventsManagementListParameters withOnlyFiltered(Boolean onlyDropped) {
        this.onlyFiltered = onlyDropped;
        return this;
    }

}
