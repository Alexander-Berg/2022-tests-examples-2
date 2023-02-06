package ru.yandex.autotests.metrika.tests.b2b.metrika.usercentric;

import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;

import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;

public class UserCentricParamsHolder {
    private FreeFormParameters tail = makeParameters();
    private String date1;
    private String date2;
    private Counter counter;

    public FreeFormParameters getTail() {
        return tail;
    }

    public String getDate1() {
        return date1;
    }

    public String getDate2() {
        return date2;
    }

    public Counter getCounter() {
        return counter;
    }

    public void setDate1(String date1) {
        this.date1 = date1;
    }

    public void setDate2(String date2) {
        this.date2 = date2;
    }

    public void setCounter(Counter counter) {
        this.counter = counter;
    }

    public UserCentricParamsHolder withDate1(final String date1) {
        this.date1 = date1;
        return this;
    }

    public UserCentricParamsHolder withDate2(final String date2) {
        this.date2 = date2;
        return this;
    }

    public UserCentricParamsHolder withCounter(final Counter counter) {
        this.counter = counter;
        return this;
    }
}
