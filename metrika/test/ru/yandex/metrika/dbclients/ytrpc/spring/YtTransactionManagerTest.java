package ru.yandex.metrika.dbclients.ytrpc.spring;

import org.assertj.core.api.Assertions;
import org.junit.After;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InOrder;
import org.mockito.Mockito;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.Ordered;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;
import org.springframework.test.context.support.AnnotationConfigContextLoader;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.annotation.EnableTransactionManagement;
import org.springframework.transaction.support.SimpleTransactionStatus;

import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Matchers.any;
import static org.mockito.Mockito.inOrder;
import static org.mockito.Mockito.reset;
import static org.mockito.Mockito.times;
import static ru.yandex.metrika.dbclients.ytrpc.YtClientMockFactory.apiClientWithTransaction;

@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration(loader = AnnotationConfigContextLoader.class)
public class YtTransactionManagerTest {

    @Autowired
    private TransactionalDao failingTransactionalDao;

    @Autowired
    private TransactionalService failingTransactionalService;

    @Autowired
    private TransactionalDao successfulTransactionalDao;

    @Autowired
    private TransactionalService successfulTransactionalService;

    @Autowired
    private YtTransactionManager txManager;

    @After
    public void tearDown() throws Exception {
        reset(txManager);
    }

    @Test
    public void transactionCreatedAndCommittedWithCleanUpInOrder() throws Exception {
        InOrder inOrder = inOrder(txManager);
        successfulTransactionalDao.daoMethod();
        inOrder.verify(txManager).getTransaction(any());
        inOrder.verify(txManager).doStart();
        inOrder.verify(txManager).commit(any());
        inOrder.verify(txManager).doCommit();
        inOrder.verify(txManager).doCleanupAfterCompletion();
        inOrder.verifyNoMoreInteractions();
    }

    @Test
    public void transactionCreatedAndCommittedByOuterMethodWhenNestedTransactionInOrder() throws Exception {
        successfulTransactionalService.serviceMethod();
        ArgumentCaptor<SimpleTransactionStatus> transactionStatusCaptor =
                verifyManagerInvocationOrderAndGetTransactionStatusesWhenSuccessful();
        Assertions.assertThat(transactionStatusCaptor.getAllValues())
                .usingElementComparatorOnFields("newTransaction")
                .containsExactly(
                        new SimpleTransactionStatus(false),
                        new SimpleTransactionStatus(true)
                );
    }

    @Test
    public void transactionCreatedAndRolledBackWithCleanUpInOrder() throws Exception {
        InOrder inOrder = inOrder(txManager);
        assertThatThrownBy(() -> failingTransactionalDao.daoMethod()).isInstanceOf(RuntimeException.class);
        inOrder.verify(txManager).getTransaction(any());
        inOrder.verify(txManager).doStart();
        inOrder.verify(txManager).rollback(any());
        inOrder.verify(txManager).doRollback();
        inOrder.verify(txManager).doCleanupAfterCompletion();
        inOrder.verifyNoMoreInteractions();
    }

    @Test
    public void transactionCreatedAndRolledBackByOuterMethodWhenNestedTransactionInOrder() throws Exception {
        assertThatThrownBy(() -> failingTransactionalService.serviceMethod()).isInstanceOf(RuntimeException.class);
        ArgumentCaptor<SimpleTransactionStatus> transactionStatusCaptor =
                verifyManagerInvocationOrderAndGetTransactionStatusesWhenFailing();
        Assertions.assertThat(transactionStatusCaptor.getAllValues())
                .usingElementComparatorOnFields("newTransaction")
                .containsExactly(
                        new SimpleTransactionStatus(false),
                        new SimpleTransactionStatus(true)
                );
    }

    private ArgumentCaptor<SimpleTransactionStatus> verifyManagerInvocationOrderAndGetTransactionStatusesWhenSuccessful() {
        InOrder inOrder = inOrder(txManager);
        ArgumentCaptor<SimpleTransactionStatus> transactionStatusCaptor = ArgumentCaptor.forClass(SimpleTransactionStatus.class);
        inOrder.verify(txManager).getTransaction(any());
        inOrder.verify(txManager).doStart();
        inOrder.verify(txManager).getTransaction(any());
        inOrder.verify(txManager, times(2)).commit(transactionStatusCaptor.capture());
        inOrder.verify(txManager).doCommit();
        inOrder.verify(txManager).doCleanupAfterCompletion();
        inOrder.verifyNoMoreInteractions();
        return transactionStatusCaptor;
    }

    private ArgumentCaptor<SimpleTransactionStatus> verifyManagerInvocationOrderAndGetTransactionStatusesWhenFailing() {
        InOrder inOrder = inOrder(txManager);
        ArgumentCaptor<SimpleTransactionStatus> transactionStatusCaptor = ArgumentCaptor.forClass(SimpleTransactionStatus.class);
        inOrder.verify(txManager).getTransaction(any());
        inOrder.verify(txManager).doStart();
        inOrder.verify(txManager).getTransaction(any());
        inOrder.verify(txManager, times(2)).rollback(transactionStatusCaptor.capture());
        inOrder.verify(txManager).doRollback();
        inOrder.verify(txManager).doCleanupAfterCompletion();
        inOrder.verifyNoMoreInteractions();
        return transactionStatusCaptor;
    }

    @Configuration
    @EnableTransactionManagement(order = Ordered.HIGHEST_PRECEDENCE)
    static class ContextConfiguration {

        @Bean
        TransactionalDao failingTransactionalDao() {
            return new TransactionalDaoImpl(true);
        }

        @Bean
        TransactionalService failingTransactionalService() {
            return new TransactionalServiceImpl(failingTransactionalDao());
        }

        @Bean
        TransactionalDao successfulTransactionalDao() {
            return new TransactionalDaoImpl(false);
        }

        @Bean
        TransactionalService successfulTransactionalService() {
            return new TransactionalServiceImpl(successfulTransactionalDao());
        }

        @Bean
        PlatformTransactionManager txManager() {
            return Mockito.spy(new YtTransactionManager(apiClientWithTransaction()));
        }
    }
}
