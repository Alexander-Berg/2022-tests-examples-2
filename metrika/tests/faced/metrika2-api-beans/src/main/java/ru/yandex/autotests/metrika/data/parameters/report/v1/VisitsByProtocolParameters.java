package ru.yandex.autotests.metrika.data.parameters.report.v1;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class VisitsByProtocolParameters extends AbstractFormParameters {
    @FormParameter("id")
    private Long id;

    @FormParameter("robots")
    private Boolean robots;

    public VisitsByProtocolParameters(Long id, Boolean robots) {
        this.id = id;
        this.robots = robots;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Boolean getRobots() {
        return robots;
    }

    public void setRobots(Boolean robots) {
        this.robots = robots;
    }
}
