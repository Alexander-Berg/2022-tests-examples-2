package ru.yandex.metrika.clickhouse.steps;

import java.util.Collections;
import java.util.Comparator;
import java.util.LinkedList;
import java.util.List;

import org.joda.time.DateTime;
import org.joda.time.Period;

public class SuiteBriefResult {
    private final List<TestCaseBriefResult> results = new LinkedList<>();

    private DateTime startDateTime;
    private DateTime finishDateTime;

    public List<TestCaseBriefResult> getResults() {
        return results;
    }

    public String getStartDateTime() {
        return JodaUtils.DTF.print(startDateTime);
    }

    public String getFinishDateTime() {
        return JodaUtils.DTF.print(finishDateTime);
    }

    public String getDuration() {
        return JodaUtils.PF.print(new Period(startDateTime, finishDateTime));
    }

    public void add(TestCaseBriefResult briefResult) {
        results.add(briefResult);
    }

    public void start() {
        startDateTime = DateTime.now();
    }

    public void finish() {
        finishDateTime = DateTime.now();
    }

    public void sort() {
        Collections.sort(results, Comparator.comparing(TestCaseBriefResult::getDestination)
                .thenComparing(TestCaseBriefResult::getHandle));
    }
}
