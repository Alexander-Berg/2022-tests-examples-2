package ru.yandex.autotests.metrika.data.parameters.management.v1;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.autotests.metrika.data.common.counters.Counter;

import java.util.Arrays;
import java.util.List;

import static ch.lambdaj.collection.LambdaCollections.with;
import static java.util.Arrays.asList;
import static java.util.stream.Collectors.toList;

/**
 * Created by konkov on 19.06.2015.
 */
public class ClientsParameters extends AbstractFormParameters {

    @FormParameter("date1")
    private String date1 = "3daysAgo";

    @FormParameter("date2")
    private String date2 = "2daysAgo";

    @FormParameter("counters")
    private String counters;

    public String getDate1() {
        return date1;
    }

    public void setDate1(String date1) {
        this.date1 = date1;
    }

    public String getDate2() {
        return date2;
    }

    public void setDate2(String date2) {
        this.date2 = date2;
    }

    public String getCounters() {
        return counters;
    }

    public void setCounters(Long... counters) {
        setCounters(asList(counters));
    }

    public void setCounters(List<Long> counters) {
        this.counters = with(counters).join(",");
    }

    public void setCounters(Counter... counters) {
        setCounters(Arrays.stream(counters).map(c -> c.get(Counter.ID)).collect(toList()));
    }

    public ClientsParameters withCounters(Long... counters) {
        setCounters(counters);
        return this;
    }

    public ClientsParameters withCounters(List<Long> counters) {
        setCounters(counters);
        return this;
    }

    public ClientsParameters withCounters(Counter... counters) {
        setCounters(counters);
        return this;
    }

    public ClientsParameters withDate2(String date2) {
        this.date2 = date2;
        return this;
    }

    public ClientsParameters withDate1(String date1) {
        this.date1 = date1;
        return this;
    }
}
