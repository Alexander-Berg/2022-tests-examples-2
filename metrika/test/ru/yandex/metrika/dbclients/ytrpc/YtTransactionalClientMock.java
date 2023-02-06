package ru.yandex.metrika.dbclients.ytrpc;

import ru.yandex.yt.ytclient.proxy.YtClient;

import static ru.yandex.metrika.dbclients.ytrpc.YtTransactionUtils.defaultTransactionOptions;

public class YtTransactionalClientMock extends YtTransactionalClient {

    public YtTransactionalClientMock(YtClient ytClient) {
        this.ytClient = ytClient;
        this.ytTransactionalExecutor = new YtTransactionalExecutor(ytClient, defaultTransactionOptions());
    }

    public YtTransactionalClientMock(YtClient ytClient, YtTransactionalExecutor ytTransactionalExecutor) {
        this.ytClient = ytClient;
        this.ytTransactionalExecutor = ytTransactionalExecutor;
    }

    @Override
    public void afterPropertiesSet() {
    }
}
