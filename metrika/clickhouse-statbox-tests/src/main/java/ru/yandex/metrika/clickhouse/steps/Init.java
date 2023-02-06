package ru.yandex.metrika.clickhouse.steps;

import java.net.URL;

import static org.junit.jupiter.api.Assertions.assertFalse;

public class Init extends TestCaseBase {
    public Init(URL test, URL ref, String query) {
        super(test, ref, query);
    }

    @Override
    protected void assertOnDifferenceDescriptor(DifferenceDescriptor differenceDescriptor) {
        assertFalse(differenceDescriptor.isFailedButNotNegative(), "Инициализация теста провалена");
    }
}
