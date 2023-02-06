package ru.yandex.metrika.replica;

import java.util.Collection;
import java.util.HashMap;
import java.util.Map;

import javax.annotation.Nonnull;
import javax.annotation.Nullable;

public class ReplicaStub<Key, Value extends Replica.Entity<Key>> implements Replica<Key, Value> {

    private final Map<Key, Value> map = new HashMap<>();

    @Nullable
    @Override
    public Value get(Key key) {
        return map.get(key);
    }

    @Nonnull
    @Override
    public Collection<Value> values() {
        return map.values();
    }

    public void add(Value value) {
        map.put(value.getKey(), value);
    }

    public void clear() {
        map.clear();
    }
}
