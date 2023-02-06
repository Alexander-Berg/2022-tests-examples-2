package ru.yandex.qatools.monitoring;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import static java.util.stream.Collectors.groupingBy;
import static java.util.stream.Collectors.toList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 24/11/16
 */
public class TestResult {
    private List<TestCaseResult> results = new ArrayList<>();

    public TestResult addResult(TestCaseResult result) {
        this.results.add(result);
        return this;
    }

    public List<TestCaseResult> getResults() {
        return results;
    }

    public Map<TestCaseResult.Status, List<TestCaseResult>> group() {
        return results.stream()
                .collect(groupingBy(TestCaseResult::getStatus, toList()));
    }

    protected List<TestCaseResult> getTestCases(TestCaseResult.Status status) {
        return results.stream()
                .filter(e -> e.getStatus() == status)
                .collect(toList());
    }

    public List<TestCaseResult> getFailed() {
        return getTestCases(TestCaseResult.Status.FAILED);
    }
}
