package ru.yandex.metrika.dbclients.ytrpc;

import org.junit.Before;
import org.junit.Test;
import org.springframework.transaction.TransactionStatus;

import ru.yandex.metrika.dbclients.ytrpc.spring.YtTransactionManager;
import ru.yandex.yt.ytclient.proxy.YtClient;

import static org.assertj.core.api.Assertions.assertThat;

public class YtTransactionalExecutorTest {

    private YtTransactionManager txManager;
    private CountingYtTransactionalExecutor ytTransactionalExecutor;
    private YtTransactionalClientMock client;

    @Before
    public void setUp() throws Exception {
        YtClient ytClient = YtClientMockFactory.apiClientWithTransaction();
        ytTransactionalExecutor = new CountingYtTransactionalExecutor(ytClient);
        client = new YtTransactionalClientMock(ytClient, ytTransactionalExecutor);
        client.afterPropertiesSet();
        txManager = new YtTransactionManager(ytClient);
    }

    @Test
    public void usesStartedTransactionWhenStartedOne() {
        startTransaction();
        client.modifyRows(null).join();
        client.modifyRows(null).join();
        assertThat(ytTransactionalExecutor.getNewTransactionCounter()).isEqualTo(0);
        assertThat(ytTransactionalExecutor.getCurrentTransactionCounter()).isEqualTo(2);
    }

    @Test
    public void createsNewTransactionWhenNoStartedOne() {
        client.modifyRows(null).join();
        client.modifyRows(null).join();
        assertThat(ytTransactionalExecutor.getNewTransactionCounter()).isEqualTo(2);
        assertThat(ytTransactionalExecutor.getCurrentTransactionCounter()).isEqualTo(0);
    }

    protected TransactionStatus startTransaction() {
        return txManager.getTransaction(null);
    }
}
