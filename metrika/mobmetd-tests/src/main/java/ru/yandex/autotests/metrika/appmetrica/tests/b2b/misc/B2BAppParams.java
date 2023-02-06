package ru.yandex.autotests.metrika.appmetrica.tests.b2b.misc;

import ru.yandex.autotests.metrika.appmetrica.data.Application;

import static ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties.apiProperties;

public class B2BAppParams {

    private static final String DEFAULT_DATE_1 = apiProperties().getDefaultStartDate();
    private static final String DEFAULT_DATE_2 = apiProperties().getDefaultEndDate();
    public static final String DEFAULT_ACCURACY = "0.05";

    private Application application;
    private String date1;
    private String date2;
    private String accuracy;

    private B2BAppParams(Application application,
                         String date1,
                         String date2,
                         String accuracy) {
        this.application = application;
        this.date1 = date1;
        this.date2 = date2;
        this.accuracy = accuracy;
    }

    public static B2BAppParams app(Application application) {
        return new B2BAppParams(application, DEFAULT_DATE_1, DEFAULT_DATE_2, DEFAULT_ACCURACY);
    }

    public Application getApplication() {
        return application;
    }

    public B2BAppParams withApplication(Application application) {
        this.application = application;
        return this;
    }

    public String getAccuracy() {
        return accuracy;
    }

    public B2BAppParams withAccuracy(String accuracy) {
        this.accuracy = accuracy;
        return this;
    }

    public String getDate1() {
        return date1;
    }

    public String getDate2() {
        return date2;
    }

    public B2BAppParams withDate(String date) {
        this.date1 = date;
        this.date2 = date;
        return this;
    }

    public B2BAppParams withDate1(String date1) {
        this.date1 = date1;
        return this;
    }

    public B2BAppParams withDate2(String date2) {
        this.date2 = date2;
        return this;
    }
}
