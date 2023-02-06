package ru.yandex.metrika.util.cache;

import java.time.Duration;
import java.util.Collection;
import java.util.concurrent.CompletableFuture;

import io.lettuce.core.ClientOptions;
import io.lettuce.core.api.StatefulRedisConnection;
import io.lettuce.core.api.async.RedisAsyncCommands;
import io.lettuce.core.api.push.PushListener;
import io.lettuce.core.api.reactive.RedisReactiveCommands;
import io.lettuce.core.api.sync.RedisCommands;
import io.lettuce.core.protocol.RedisCommand;
import io.lettuce.core.resource.ClientResources;

public class RedisConnectionMock<K,V> implements StatefulRedisConnection {


    private Duration timeout;
    private RedisCommands commands;

    public RedisConnectionMock(RedisCommands commands) {
        this.commands = commands;
    }

    @Override
    public boolean isMulti() {
        return false;
    }

    @Override
    public RedisCommands sync() {
        return commands;
    }

    @Override
    public RedisAsyncCommands async() {
        return null;
    }

    @Override
    public RedisReactiveCommands reactive() {
        return null;
    }

    @Override
    public void addListener(PushListener listener) {

    }

    @Override
    public void removeListener(PushListener listener) {

    }

    @Override
    public void setTimeout(Duration timeout) {
        this.timeout = timeout;
    }

    @Override
    public Duration getTimeout() {
        return timeout;
    }

    @Override
    public void close() {

    }

    @Override
    public CompletableFuture<Void> closeAsync() {
        return null;
    }

    @Override
    public boolean isOpen() {
        return true;
    }

    @Override
    public ClientOptions getOptions() {
        return null;
    }

    @Override
    public ClientResources getResources() {
        return null;
    }

    @Override
    public void reset() {}

    @Override
    public void setAutoFlushCommands(boolean autoFlush) { }

    @Override
    public void flushCommands() { }

    @Override
    public Collection<RedisCommand> dispatch(Collection collection) {
        return null;
    }

    @Override
    public RedisCommand dispatch(RedisCommand command) {
        return null;
    }
}
