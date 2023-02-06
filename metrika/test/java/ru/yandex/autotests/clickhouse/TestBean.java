package ru.yandex.autotests.clickhouse;

import ru.yandex.autotests.metrika.commons.beans.Column;
import ru.yandex.autotests.metrika.commons.beans.Position;

import java.util.Objects;

/**
 * Created by konkov on 02.02.2016.
 */
public class TestBean {

    @Position(1)
    @Column(name = "EventID", type = "UInt32")
    private Long eventID;

    @Position(2)
    @Column(name = "URL", type = "String")
    private String URL;

    @Position(3)
    @Column(name = "ParsedParams.Key1", type = "Array(String)")
    private String[] parsedParams_Key1;

    @Position(4)
    @Column(name = "ParsedParams.Key2", type = "Array(UInt32)")
    private Long[] parsedParams_Key2;

    public Long getEventID() {
        return eventID;
    }

    public void setEventID(Long eventID) {
        this.eventID = eventID;
    }

    public TestBean withEventID(Long eventID) {
        this.eventID = eventID;
        return this;
    }

    public String getURL() {
        return URL;
    }

    public void setURL(String URL) {
        this.URL = URL;
    }

    public TestBean withURL(String URL) {
        this.URL = URL;
        return this;
    }

    public String[] getParsedParams_Key1() {
        return parsedParams_Key1;
    }

    public void setParsedParams_Key1(String[] parsedParams_Key1) {
        this.parsedParams_Key1 = parsedParams_Key1;
    }

    public TestBean withParsedParams_Key1(String[] parsedParams_Key1) {
        this.parsedParams_Key1 = parsedParams_Key1;
        return this;
    }

    public Long[] getParsedParams_Key2() {
        return parsedParams_Key2;
    }

    public void setParsedParams_Key2(Long[] parsedParams_Key2) {
        this.parsedParams_Key2 = parsedParams_Key2;
    }

    public TestBean withParsedParams_Key2(Long[] parsedParams_Key2) {
        this.parsedParams_Key2 = parsedParams_Key2;
        return this;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        TestBean testBean = (TestBean) o;
        return Objects.equals(eventID, testBean.eventID) &&
                Objects.equals(URL, testBean.URL);
    }

    @Override
    public int hashCode() {
        return Objects.hash(eventID, URL);
    }

}
