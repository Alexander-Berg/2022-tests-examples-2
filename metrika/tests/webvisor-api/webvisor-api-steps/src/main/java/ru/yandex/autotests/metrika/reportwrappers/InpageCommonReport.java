package ru.yandex.autotests.metrika.reportwrappers;

/**
 * Created by sonick on 20.12.16.
 */
public abstract class InpageCommonReport<T> implements InpageReport {

    protected final T rawReport;

    public InpageCommonReport(T rawReport) {
        this.rawReport = rawReport;
    }
}
