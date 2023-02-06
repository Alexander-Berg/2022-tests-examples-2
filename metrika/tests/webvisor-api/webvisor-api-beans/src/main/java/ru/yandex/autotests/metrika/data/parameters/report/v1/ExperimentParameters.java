package ru.yandex.autotests.metrika.data.parameters.report.v1;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.autotests.metrika.data.common.counters.Counter;

import static ru.yandex.autotests.metrika.data.common.counters.Counter.EXPERIMENT_ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.GOAL_ID;

/**
 * Created by konkov on 28.08.2015.
 */
public class ExperimentParameters extends AbstractFormParameters {

    @FormParameter("experiment_ab")
    private String experimentId;

    public String getExperimentId() {
        return experimentId;
    }

    public void setExperimentId(String experimentId) {
        this.experimentId = experimentId;
    }

    public ExperimentParameters withExperimentId(final String experimentId) {
        this.experimentId = experimentId;
        return this;
    }

    public static ExperimentParameters experimentId(String experimentId) {
        return new ExperimentParameters().withExperimentId(experimentId);
    }

    public static ExperimentParameters experimentId(Long experimentId) {
        return experimentId(String.valueOf(experimentId));
    }

    public static ExperimentParameters experimentId(Counter counter) {
        return experimentId(counter.get(EXPERIMENT_ID));
    }
}
