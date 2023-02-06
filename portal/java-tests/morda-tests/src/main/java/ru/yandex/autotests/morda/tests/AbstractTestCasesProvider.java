package ru.yandex.autotests.morda.tests;

import ru.yandex.autotests.morda.tests.MordaTestsProperties.TestMode;

import java.util.List;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 22/08/16
 */
public abstract class AbstractTestCasesProvider<T> {
    protected String environment;

    public AbstractTestCasesProvider(String environment) {
        this.environment = environment;
    }

    public List<T> getTestCases(TestMode mode) {
        List<T> testCases;
        switch (mode) {
            case FULL:
                testCases = getFullTestCases();
                break;
            case SMOKE:
                testCases = getSmokeTestCases();
                break;
            case BASE:
                testCases = getBaseTestCases();
                break;
            case MONITORING:
                testCases = getMonitoringTestCases();
                break;
            default:
                testCases = getBaseTestCases();
                break;
        }
        return testCases;
    }

    public abstract List<T> getBaseTestCases();

    public List<T> getSmokeTestCases() {
        return getBaseTestCases();
    }

    public List<T> getFullTestCases() {
        return getBaseTestCases();
    }

    public List<T> getMonitoringTestCases() {
        return getBaseTestCases();
    }
}
