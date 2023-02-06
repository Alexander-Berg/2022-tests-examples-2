package ru.yandex.autotests.metrika.data.parameters.management.v1;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.metrika.api.management.client.external.offlineconversion.OfflineConversionUploadingClientIdType;

/**
 * @author zgmnkv
 */
public class OfflineConversionParameters extends BaseConversionParameters {

    @FormParameter("client_id_type")
    private String clientIdType;

    @FormParameter("new_goal_name")
    private String newGoalName;

    @FormParameter("ignore_visit_join_threshold")
    private Integer ignoreVisitJoinThreshold;

    @FormParameter("ignore_calls_visit_join_threshold")
    private Integer ignoreCallsVisitJoinThreshold;

    public String getClientIdType() {
        return clientIdType;
    }

    public void setClientIdType(OfflineConversionUploadingClientIdType clientIdType) {
        this.clientIdType = clientIdType.name();
    }

    public OfflineConversionParameters withClientIdType(OfflineConversionUploadingClientIdType clientIdType) {
        this.clientIdType = clientIdType.name();
        return this;
    }

    public OfflineConversionParameters withClientIdType(String clientIdType) {
        this.clientIdType = clientIdType;
        return this;
    }

    public String getNewGoalName() {
        return newGoalName;
    }

    public void setNewGoalName(String newGoalName) {
        this.newGoalName = newGoalName;
    }

    public OfflineConversionParameters withNewGoalName(String newGoalName) {
        this.newGoalName = newGoalName;
        return this;
    }

    public Integer getIgnoreVisitJoinThreshold() {
        return ignoreVisitJoinThreshold;
    }

    public void setIgnoreVisitJoinThreshold(Integer ignoreVisitJoinThreshold) {
        this.ignoreVisitJoinThreshold = ignoreVisitJoinThreshold;
    }

    public OfflineConversionParameters withIgnoreVisitJoinThreshold(Integer ignoreVisitJoinThreshold) {
        this.ignoreVisitJoinThreshold = ignoreVisitJoinThreshold;
        return this;
    }

    public Integer getIgnoreCallsVisitJoinThreshold() {
        return ignoreCallsVisitJoinThreshold;
    }

    public void setIgnoreCallsVisitJoinThreshold(Integer ignoreCallsVisitJoinThreshold) {
        this.ignoreCallsVisitJoinThreshold = ignoreCallsVisitJoinThreshold;
    }

    public OfflineConversionParameters withIgnoreCallsVisitJoinThreshold(Integer ignoreCallsVisitJoinThreshold) {
        this.ignoreCallsVisitJoinThreshold = ignoreCallsVisitJoinThreshold;
        return this;
    }
}
