package ru.yandex.autotests.metrika.data.parameters.internal;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.autotests.metrika.data.common.counters.Counter;

import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;

/**
 * Created by ava1on on 14.09.16.
 */
public class GetAccuracyParameters extends AbstractFormParameters {

    @FormParameter("id")
    private Long id;

    @FormParameter("date1")
    private String date1;

    @FormParameter("date2")
    private String date2;

    @FormParameter("table")
    private String table = "visits";

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public void setId(Counter counter) {
        setId(counter.get(ID));
    }

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

    public String getTable() {
        return table;
    }

    public void setTable(String table) {
        this.table = table;
    }

    public GetAccuracyParameters withId(Long id) {
        this.setId(id);
        return this;
    }

    public GetAccuracyParameters withId(Counter counter) {
        this.setId(counter);
        return this;
    }

    public GetAccuracyParameters withDate1(String date1) {
        this.setDate1(date1);
        return this;
    }

    public GetAccuracyParameters withDate2(String date2) {
        this.setDate2(date2);
        return this;
    }

    public GetAccuracyParameters withTable(String table) {
        this.setTable(table);
        return this;
    }
}
