package ru.yandex.autotests.metrika.appmetrica.wrappers;

import ru.yandex.metrika.mobmet.model.TestDevice;

/**
 * Created by graev on 18/01/2017.
 */
public final class TestDeviceWrapper {
    public TestDevice device;

    public TestDeviceWrapper(TestDevice device) {
        this.device = device;
    }

    public TestDevice get() {
        return device;
    }

    @Override
    public String toString() {
        return device == null ? "null" : device.getName();
    }
}
