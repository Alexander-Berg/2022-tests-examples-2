package ru.yandex.autotests.topsites.data.parameters.report;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class TopSitesBaseParameters extends AbstractFormParameters {
    @FormParameter("month")
    private String month;
    @FormParameter("snapshot_id")
    private String snapshotId;

    public String getMonth() {
        return month;
    }

    public void setMonth(String month) {
        this.month = month;
    }

    public String getSnapshotId() {
        return snapshotId;
    }

    public void setSnapshotId(String snapshotId) {
        this.snapshotId = snapshotId;
    }


    public TopSitesBaseParameters withMonth(String month) {
        this.month = month;
        return this;
    }

    public TopSitesBaseParameters withSnapshotId(String snapshotId) {
        this.snapshotId = snapshotId;
        return this;
    }
}
