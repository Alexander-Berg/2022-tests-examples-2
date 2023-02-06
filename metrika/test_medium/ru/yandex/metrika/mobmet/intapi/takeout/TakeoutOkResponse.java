package ru.yandex.metrika.mobmet.intapi.takeout;

import java.util.List;

import ru.yandex.metrika.mobmet.intapi.takeout.model.Application;
import ru.yandex.metrika.mobmet.intapi.takeout.model.Label;
import ru.yandex.metrika.mobmet.intapi.takeout.model.Partner;

public class TakeoutOkResponse {
    private List<Application> applications;
    private List<Partner> mediaSources;
    private List<Label> labels;

    public List<Application> getApplications() {
        return applications;
    }

    public void setApplications(List<Application> applications) {
        this.applications = applications;
    }

    public List<Partner> getMediaSources() {
        return mediaSources;
    }

    public void setMediaSources(List<Partner> mediaSources) {
        this.mediaSources = mediaSources;
    }

    public List<Label> getLabels() {
        return labels;
    }

    public void setLabels(List<Label> labels) {
        this.labels = labels;
    }
}
