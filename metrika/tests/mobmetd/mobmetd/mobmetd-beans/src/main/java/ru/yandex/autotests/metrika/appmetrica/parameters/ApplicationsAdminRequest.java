package ru.yandex.autotests.metrika.appmetrica.parameters;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class ApplicationsAdminRequest extends AbstractFormParameters {

    @FormParameter("application_id")
    private Long appId;
    @FormParameter("name")
    private String name;
    @FormParameter("owner_login")
    private String ownerLogin;
    @FormParameter("owner_uid")
    private Long ownerUid;
    @FormParameter("api_key128")
    private String apiKey128;
    @FormParameter("status")
    private String status;
    @FormParameter("tracking_id")
    private String trackingId;

    public Long getAppId() {
        return appId;
    }

    public void setAppId(Long appId) {
        this.appId = appId;
    }

    public ApplicationsAdminRequest withAppId(Long appId) {
        this.appId = appId;
        return this;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public ApplicationsAdminRequest withName(String name) {
        this.name = name;
        return this;
    }

    public String getOwnerLogin() {
        return ownerLogin;
    }

    public void setOwnerLogin(String ownerLogin) {
        this.ownerLogin = ownerLogin;
    }

    public ApplicationsAdminRequest withOwnerLogin(String ownerLogin) {
        this.ownerLogin = ownerLogin;
        return this;
    }

    public Long getOwnerUid() {
        return ownerUid;
    }

    public void setOwnerUid(Long ownerUid) {
        this.ownerUid = ownerUid;
    }

    public ApplicationsAdminRequest withOwnerUid(Long ownerUid) {
        this.ownerUid = ownerUid;
        return this;
    }

    public String getApiKey128() {
        return apiKey128;
    }

    public void setApiKey128(String apiKey128) {
        this.apiKey128 = apiKey128;
    }

    public ApplicationsAdminRequest withApiKey128(String apiKey128) {
        this.apiKey128 = apiKey128;
        return this;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public ApplicationsAdminRequest withStatus(String status) {
        this.status = status;
        return this;
    }

    public String getTrackingId() {
        return trackingId;
    }

    public void setTrackingId(String trackingId) {
        this.trackingId = trackingId;
    }

    public ApplicationsAdminRequest withTrackingId(String trackingId) {
        this.trackingId = trackingId;
        return this;
    }
}
