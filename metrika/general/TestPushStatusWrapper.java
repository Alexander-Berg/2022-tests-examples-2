package ru.yandex.metrika.mobmet.push.response;

import ru.yandex.metrika.mobmet.push.common.campaigns.adapters.TestPushStatusAdapter;

/**
 * Враппер для тестов
 * <p>
 * Created by graev on 23/09/16.
 */
public final class TestPushStatusWrapper {
    private TestPushStatusAdapter status;

    public TestPushStatusWrapper() {
    }

    public TestPushStatusWrapper(TestPushStatusAdapter status) {
        this.status = status;
    }

    public TestPushStatusAdapter getStatus() {
        return status;
    }

    public void setStatus(TestPushStatusAdapter status) {
        this.status = status;
    }
}
