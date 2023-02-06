package ru.yandex.autotests.metrika.appmetrica.parameters.profile.events;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class ProfileSessionsParametersBase extends AbstractFormParameters {

    @FormParameter("appId")
    private long appId;

    @FormParameter("date1")
    private String date1;

    @FormParameter("date2")
    private String date2;

    @FormParameter("limit")
    private Integer limit;

    @FormParameter("offset")
    private Integer offset;

    @FormParameter("device")
    private String device;

    @FormParameter("profileOrigin")
    private String profileOrigin;

    public long getAppId() {
        return appId;
    }

    public ProfileSessionsParametersBase withAppId(long appId) {
        this.appId = appId;
        return this;
    }

    public String getDate1() {
        return date1;
    }

    public ProfileSessionsParametersBase withDate1(String date1) {
        this.date1 = date1;
        return this;
    }

    public String getDate2() {
        return date2;
    }

    public ProfileSessionsParametersBase withDate2(String date2) {
        this.date2 = date2;
        return this;
    }

    public int getLimit() {
        return limit;
    }

    public ProfileSessionsParametersBase withLimit(int limit) {
        this.limit = limit;
        return this;
    }

    public int getOffset() {
        return offset;
    }

    public ProfileSessionsParametersBase withOffset(int offset) {
        this.offset = offset;
        return this;
    }

    public String getDevice() {
        return device;
    }

    public ProfileSessionsParametersBase withDevice(String device) {
        this.device = device;
        return this;
    }

    public String getProfileOrigin() {
        return profileOrigin;
    }

    public ProfileSessionsParametersBase withProfileOrigin(String profileOrigin) {
        this.profileOrigin = profileOrigin;
        return this;
    }

}
