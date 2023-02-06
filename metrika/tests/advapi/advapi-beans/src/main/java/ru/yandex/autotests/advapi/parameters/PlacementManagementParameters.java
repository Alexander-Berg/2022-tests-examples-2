package ru.yandex.autotests.advapi.parameters;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class PlacementManagementParameters extends CommonParameters {

    @FormParameter("override")
    private Boolean override;

    @FormParameter("tracking")
    private Boolean tracking;

    @FormParameter("viewability")
    private Boolean viewability;

    public Boolean getOverride() {
        return override;
    }

    public void setOverride(Boolean override) {
        this.override = override;
    }

    public PlacementManagementParameters withOverride(Boolean override) {
        this.override = override;
        return this;
    }

    public Boolean getTracking() {
        return tracking;
    }

    public void setTracking(Boolean tracking) {
        this.tracking = tracking;
    }

    public PlacementManagementParameters withTracking(Boolean tracking) {
        this.tracking = tracking;
        return this;
    }

    public Boolean getViewability() {
        return viewability;
    }

    public void setViewability(Boolean viewability) {
        this.viewability = viewability;
    }

    public PlacementManagementParameters withViewability(Boolean viewability) {
        this.viewability = viewability;
        return this;
    }
}
