package ru.yandex.metrika.clickhouse.steps;

import java.net.URL;

import static org.junit.jupiter.api.Assertions.assertFalse;

public class TestCase extends TestCaseBase {

    public TestCase(URL test, URL ref, String query) {
        super(test, ref, query);
    }

    @Override
    protected void assertOnDifferenceDescriptor(DifferenceDescriptor differenceDescriptor) {
        if (differenceDescriptor.isBroken()) {
            throw new RuntimeException("Тест сломан");
        }
        assertFalse(differenceDescriptor.isFail(), "Тест провален");
    }
}
