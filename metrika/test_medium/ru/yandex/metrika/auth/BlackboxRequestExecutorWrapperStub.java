package ru.yandex.metrika.auth;

import ru.yandex.inside.passport.blackbox2.BlackboxRequestExecutor;

public class BlackboxRequestExecutorWrapperStub extends BlackboxRequestExecutorWrapper {
    public BlackboxRequestExecutorWrapperStub() {
        super(null, null);
    }

    @Override
    protected BlackboxRequestExecutor buildRequestExecutor(String blackboxUrl, int blackboxTimeout) {
        return new BlackboxRequestExecutorStub();
    }

    @Override
    protected BlackboxRequestExecutor buildBatchRequestExecutor(String blackboxUrl, int blackboxTimeout) {
        return new BlackboxRequestExecutorStub();
    }
}
