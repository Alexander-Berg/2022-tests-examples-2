package ru.yandex.metrika.mobmet.crash.decoder.steps;

import java.util.List;

public class CrashTestData {

    private final CrashInputFields input;

    private final List<CrashProcessingFields> expected;

    public CrashTestData(CrashInputFields input, List<CrashProcessingFields> expected) {
        this.input = input;
        this.expected = expected;
    }

    public CrashInputFields getInput() {
        return input;
    }

    public List<CrashProcessingFields> getExpected() {
        return expected;
    }

}
