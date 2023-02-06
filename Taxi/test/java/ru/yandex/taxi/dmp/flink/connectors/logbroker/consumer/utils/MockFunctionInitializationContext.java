package ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.utils;

import java.util.OptionalLong;

import org.apache.flink.api.common.state.KeyedStateStore;
import org.apache.flink.api.common.state.OperatorStateStore;
import org.apache.flink.runtime.state.FunctionInitializationContext;

public class MockFunctionInitializationContext implements FunctionInitializationContext {

    private final boolean isRestored;
    private final OperatorStateStore operatorStateStore;

    public MockFunctionInitializationContext(boolean isRestored, OperatorStateStore operatorStateStore) {
        this.isRestored = isRestored;
        this.operatorStateStore = operatorStateStore;
    }

    @Override
    public boolean isRestored() {
        return isRestored;
    }

    @Override
    public OptionalLong getRestoredCheckpointId() {
        throw new UnsupportedOperationException();
    }

    @Override
    public OperatorStateStore getOperatorStateStore() {
        return operatorStateStore;
    }

    @Override
    public KeyedStateStore getKeyedStateStore() {
        throw new UnsupportedOperationException();
    }
}
