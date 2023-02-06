package ru.yandex.metrika.util.cache;

import io.lettuce.core.api.StatefulRedisConnection;

import ru.yandex.metrika.dbclients.redis.RedisConnector;
import ru.yandex.metrika.dbclients.redis.RedisSourceList;

public class RedisConnectorMock extends RedisConnector {
    private StatefulRedisConnection<String, String> connection;
    private boolean connected;

    public RedisConnectorMock(RedisSourceList sources) {
        super(sources);
    }


    public RedisConnectorMock(StatefulRedisConnection<String, String> connection, boolean connected) {
        super(new RedisSourceList());
        this.connection = connection;
        this.connected = connected;
    }

    @Override
    public void init() {
    }

    @Override
    protected StatefulRedisConnection<String, String> getConnection() {
        return connection;
    }

    public boolean isConnected() {
        return connected;
    }

    public void setConnected(boolean connected) {
        this.connected = connected;
    }
}
