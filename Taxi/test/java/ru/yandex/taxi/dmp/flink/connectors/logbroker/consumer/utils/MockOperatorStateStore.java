package ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.utils;

import java.util.Set;

import org.apache.flink.api.common.state.BroadcastState;
import org.apache.flink.api.common.state.ListState;
import org.apache.flink.api.common.state.ListStateDescriptor;
import org.apache.flink.api.common.state.MapStateDescriptor;
import org.apache.flink.api.common.state.OperatorStateStore;

public class MockOperatorStateStore implements OperatorStateStore {

    private final ListState<?> mockRestoredUnionListState;

    public MockOperatorStateStore(ListState<?> restoredUnionListState) {
        this.mockRestoredUnionListState = restoredUnionListState;
    }

    @Override
    @SuppressWarnings("unchecked")
    public <S> ListState<S> getUnionListState(ListStateDescriptor<S> stateDescriptor) throws Exception {
        return (ListState<S>) mockRestoredUnionListState;
    }

    @Override
    public <K, V> BroadcastState<K, V> getBroadcastState(MapStateDescriptor<K, V> stateDescriptor) throws Exception {
        throw new UnsupportedOperationException();
    }

    @Override
    public <S> ListState<S> getListState(ListStateDescriptor<S> stateDescriptor) throws Exception {
        throw new UnsupportedOperationException();
    }

    @Override
    public Set<String> getRegisteredStateNames() {
        throw new UnsupportedOperationException();
    }

    @Override
    public Set<String> getRegisteredBroadcastStateNames() {
        throw new UnsupportedOperationException();
    }
}
