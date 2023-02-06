package ru.yandex.autotests.metrika.appmetrica.properties;

import java.net.MalformedURLException;
import java.net.URL;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import ru.qatools.properties.Property;
import ru.qatools.properties.PropertyLoader;
import ru.qatools.properties.Resource;

import ru.yandex.autotests.irt.testutils.beandiffer2.beanfield.BeanFieldPath;
import ru.yandex.autotests.metrika.appmetrica.exceptions.AppMetricaException;

import static java.lang.String.format;
import static java.util.stream.Collectors.toList;

@Resource.Classpath("appmetricaapi.properties")
public class AppMetricaApiProperties {

    private static final AppMetricaApiProperties INSTANCE = new AppMetricaApiProperties();

    public static AppMetricaApiProperties apiProperties() {
        return INSTANCE;
    }

    @Property("api.testing")
    private String apiTesting;

    @Property("api.reference")
    private String apiReference;

    @Property("api.production")
    private String apiProduction;

    @Property("b2b.ignoredFields")
    private String[] ignoredFields;

    @Property("b2b.ua.ignoredFields")
    private String[] uaIgnoredFields;

    @Property("b2b.defaultIgnoredFields")
    private String[] defaultIgnoredFields;

    @Property("b2b.default.startDate")
    private String defaultStartDate;
    @Property("b2b.default.endDate")
    private String defaultEndDate;

    @Property("b2b.postback.startDate")
    private String postbackStartDate;
    @Property("b2b.postback.endDate")
    private String postbackEndDate;

    @Property("b2b.push.startDate")
    private String pushStartDate;
    @Property("b2b.push.endDate")
    private String pushEndDate;

    @Property("b2b.ca.startDate")
    private String caStartDate;
    @Property("b2b.ca.endDate")
    private String caEndDate;

    @Property("b2b.ua.startDate")
    private String uaStartDate;
    @Property("b2b.ua.endDate")
    private String uaEndDate;

    @Property("b2b.re.startDate")
    private String reStartDate;
    @Property("b2b.re.endDate")
    private String reEndDate;

    @Property("b2b.ecom.startDate")
    private String ecomStartDate;
    @Property("b2b.ecom.endDate")
    private String ecomEndDate;

    @Property("api.report-semaphore-name")
    private String reportSemaphoreName;

    @Property("api.report-semaphore-permits")
    private int reportSemaphorePermits;

    @Property("api.parallel-parameters.threads")
    private int parallelParametersThreads;

    @Property("api.check-empty-body-requests")
    private boolean checkEmptyBodyRequests;

    private AppMetricaApiProperties() {
        PropertyLoader.newInstance().populate(this);
    }

    public String getReportSemaphoreName() {
        return reportSemaphoreName;
    }

    public int getReportSemaphorePermits() {
        return reportSemaphorePermits;
    }

    public int getParallelParametersThreads() {
        return parallelParametersThreads;
    }

    public boolean isCheckEmptyBodyRequests() {
        return checkEmptyBodyRequests;
    }

    public URL getApiTesting() {
        try {
            return new URL(apiTesting);
        } catch (MalformedURLException e) {
            throw failWithIncorrectUrl(apiTesting, e);
        }
    }

    public URL getApiReference() {
        try {
            return new URL(apiReference);
        } catch (MalformedURLException e) {
            throw failWithIncorrectUrl(apiReference, e);
        }
    }

    public URL getApiProduction() {
        try {
            return new URL(apiProduction);
        } catch (MalformedURLException e) {
            throw failWithIncorrectUrl(apiProduction, e);
        }
    }

    private RuntimeException failWithIncorrectUrl(String url, MalformedURLException e) {
        throw new AppMetricaException(format("Некорректный URL: '%s'", url), e);
    }

    public BeanFieldPath[] getB2bIgnoredFields() {
        return extractFieldPaths(ignoredFields, defaultIgnoredFields);
    }

    private BeanFieldPath[] extractFieldPaths(String[] ignoredFields, String[] defaultIgnoredFields) {
        List<String> ignores = new ArrayList<>();

        if (ignoredFields != null) {
            Collections.addAll(ignores, ignoredFields);
        }

        if (defaultIgnoredFields != null) {
            for (String ignoredField : defaultIgnoredFields) {
                if (!ignores.contains(ignoredField)) {
                    ignores.add(ignoredField);
                }
            }
        }

        return ignores.stream()
                .map(s -> BeanFieldPath.newPath(s.split("/")))
                .collect(toList())
                .toArray(new BeanFieldPath[0]);
    }

    public String getDefaultStartDate() {
        return defaultStartDate;
    }

    public String getDefaultEndDate() {
        return defaultEndDate;
    }

    public String getPostbackStartDate() {
        return postbackStartDate;
    }

    public String getPostbackEndDate() {
        return postbackEndDate;
    }

    public String getPushStartDate() {
        return pushStartDate;
    }

    public String getPushEndDate() {
        return pushEndDate;
    }

    public String getCaStartDate() {
        return caStartDate;
    }

    public String getCaEndDate() {
        return caEndDate;
    }

    public String getUaStartDate() {
        return uaStartDate;
    }

    public String getUaEndDate() {
        return uaEndDate;
    }

    public String getReStartDate() {
        return reStartDate;
    }

    public String getReEndDate() {
        return reEndDate;
    }

    public String getEcomStartDate() {
        return ecomStartDate;
    }

    public String getEcomEndDate() {
        return ecomEndDate;
    }
}
