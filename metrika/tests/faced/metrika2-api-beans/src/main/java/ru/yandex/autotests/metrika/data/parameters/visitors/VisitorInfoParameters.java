package ru.yandex.autotests.metrika.data.parameters.visitors;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class VisitorInfoParameters extends AbstractFormParameters {
    @FormParameter("id")
    private Long id;
    @FormParameter("userIDHash")
    private String userIdHash;
    @FormParameter("userIDHash64")
    private String userIdHash64;
    @FormParameter("first_visit_date")
    private String firstVisitDate;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getUserIdHash() {
        return userIdHash;
    }

    public void setUserIdHash(String userIdHash) {
        this.userIdHash = userIdHash;
    }

    public String getUserIdHash64() {
        return userIdHash64;
    }

    public void setUserIdHash64(String userIdHash64) {
        this.userIdHash64 = userIdHash64;
    }

    public String getFirstVisitDate() {
        return firstVisitDate;
    }

    public void setFirstVisitDate(String firstVisitDate) {
        this.firstVisitDate = firstVisitDate;
    }

    public VisitorInfoParameters withId(Long id) {
        this.setId(id);
        return this;
    }

    public VisitorInfoParameters withUserIdHash(String userIdHash) {
        this.userIdHash = userIdHash;
        return this;
    }

    public VisitorInfoParameters withUserIdHash64(String userIdHash64) {
        this.userIdHash64 = userIdHash64;
        return this;
    }

    public VisitorInfoParameters withFirstVisitDate(String firstVisitDate) {
        this.firstVisitDate = firstVisitDate;
        return this;
    }


    public static VisitorInfoParameters userIdHash(String userIdHash) {
        return new VisitorInfoParameters().withUserIdHash(userIdHash);
    }

    public static VisitorInfoParameters userIdHash64(String userIdHash64) {
        return new VisitorInfoParameters().withUserIdHash64(userIdHash64);
    }

    public static VisitorInfoParameters firstVisitDate(String firstVisitDate) {
        return new VisitorInfoParameters().withFirstVisitDate(firstVisitDate);
    }
}
