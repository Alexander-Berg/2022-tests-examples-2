package ru.yandex.autotests.metrika.data.parameters.report.v1;

import org.apache.commons.lang3.StringUtils;
import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.autotests.metrika.data.report.v1.enums.GroupEnum;
import ru.yandex.metrika.segments.site.parametrization.Attribution;

import java.util.Objects;

/**
 * Created by konkov on 15.05.2015.
 */
public class ParametrizationParameters extends AbstractFormParameters {

    @FormParameter("attribution")
    private String attribution;

    @FormParameter("group")
    private String group;

    @FormParameter("quantile")
    private String quantile;

    @FormParameter("experiment_ab")
    private String experiment;

    public String getAttribution() {
        return attribution;
    }

    public void setAttribution(String attribution) {
        this.attribution = attribution;
    }

    public void setAttribution(Attribution attribution) {
        setAttribution(Objects.toString(attribution, StringUtils.EMPTY).toLowerCase());
    }

    public String getGroup() {
        return group;
    }

    public void setGroup(String group) {
        this.group = group;
    }

    public void setGroup(GroupEnum group) {
        setGroup(Objects.toString(group, StringUtils.EMPTY).toLowerCase());
    }

    public String getQuantile() {
        return quantile;
    }

    public void setQuantile(String quantile) {
        this.quantile = quantile;
    }

    public void setQuantile(int quantile) {
        setQuantile(String.valueOf(quantile));
    }

    public String getExperiment() {
        return experiment;
    }

    public void setExperiment(String experiment) {
        this.experiment = experiment;
    }

    public void setExperiment(int experiment) {
        setExperiment(String.valueOf(experiment));
    }

    public ParametrizationParameters withQuantile(final String quantile) {
        setQuantile(quantile);
        return this;
    }

    public ParametrizationParameters withQuantile(final int quantile) {
        setQuantile(quantile);
        return this;
    }

    public ParametrizationParameters withAttribution(String attribution) {
        this.setAttribution(attribution);
        return this;
    }

    public ParametrizationParameters withAttribution(Attribution attribution) {
        this.setAttribution(attribution);
        return this;
    }

    public ParametrizationParameters withGroup(String group) {
        this.setGroup(group);
        return this;
    }

    public ParametrizationParameters withGroup(GroupEnum group) {
        this.setGroup(group);
        return this;
    }

    public ParametrizationParameters withExperiment(final String experiment) {
        setExperiment(experiment);
        return this;
    }

    public static ParametrizationParameters parametrization() {
        return new ParametrizationParameters();
    }

}
