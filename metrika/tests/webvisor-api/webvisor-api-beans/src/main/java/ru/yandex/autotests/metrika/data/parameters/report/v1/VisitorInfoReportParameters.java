package ru.yandex.autotests.metrika.data.parameters.report.v1;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class VisitorInfoReportParameters extends CommonReportParameters {

    @FormParameter("userIDHash")
    private String userIDHash;

    @FormParameter("userIDHash64")
    private String userIDHash64;

    @FormParameter("first_visit_date")
    private String firstVisitDate;

    public String getUserIDHash() {
        return userIDHash;
    }

    public void setUserIDHash(String userIDHash) {
        this.userIDHash = userIDHash;
    }

    public String getUserIDHash64() {
        return userIDHash64;
    }

    public void setUserIDHash64(String userIDHash64) {
        this.userIDHash64 = userIDHash64;
    }
    public String getFirstVisitDate() {
        return firstVisitDate;
    }

    public void setFirstVisitDate(String firstVisitDate) {
        this.firstVisitDate = firstVisitDate;
    }

    public VisitorInfoReportParameters withUserIDHash(String userIDHash) {
        this.setUserIDHash(userIDHash);
        return this;
    }

    public VisitorInfoReportParameters withUserIDHash64(String userIDHash64) {
        this.setUserIDHash64(userIDHash64);
        return this;
    }

    public VisitorInfoReportParameters withFirstVisitDate(String firstVisitDate) {
        this.setFirstVisitDate(firstVisitDate);
        return this;
    }

}
