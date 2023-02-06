package ru.yandex.taxi.dmp.flink.connectors.logbroker.consumer.utils;

import java.util.ArrayList;
import java.util.List;

import org.apache.flink.api.common.state.ListState;
import org.apache.flink.util.Preconditions;

public final class TestingListState<T> implements ListState<T> {

    private final List<T> list = new ArrayList<>();
    private boolean clearCalled = false;

    @Override
    public void clear() {
        list.clear();
        clearCalled = true;
    }

    @Override
    public Iterable<T> get() throws Exception {
        return list;
    }

    @Override
    public void add(T value) throws Exception {
        Preconditions.checkNotNull(value, "You cannot add null to a ListState.");
        list.add(value);
    }

    public List<T> getList() {
        return list;
    }

    public boolean isClearCalled() {
        return clearCalled;
    }

    @Override
    public void update(List<T> values) throws Exception {
        clear();

        addAll(values);
    }

    @Override
    public void addAll(List<T> values) throws Exception {
        if (values != null) {
            values.forEach(v -> Preconditions.checkNotNull(v, "You cannot add null to a ListState."));

            list.addAll(values);
        }
    }
}
