package ru.yandex.metrika.dbclients.yt;

import java.util.List;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.Answers;
import org.mockito.Mock;
import org.mockito.runners.MockitoJUnitRunner;

import ru.yandex.inside.yt.kosher.Yt;
import ru.yandex.inside.yt.kosher.common.GUID;
import ru.yandex.inside.yt.kosher.cypress.Cypress;
import ru.yandex.inside.yt.kosher.impl.YtConfiguration;
import ru.yandex.inside.yt.kosher.impl.common.http.HttpCommandExecutor;
import ru.yandex.inside.yt.kosher.impl.tables.http.YtTablesHttpImpl;
import ru.yandex.inside.yt.kosher.operations.Yield;
import ru.yandex.inside.yt.kosher.tables.YTableEntryType;
import ru.yandex.inside.yt.kosher.transactions.Transaction;
import ru.yandex.inside.yt.kosher.transactions.YtTransactions;

import static com.google.common.collect.ImmutableList.of;
import static java.util.Arrays.asList;
import static org.mockito.Matchers.any;
import static org.mockito.Matchers.anyBoolean;
import static org.mockito.Matchers.anyObject;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@RunWith(MockitoJUnitRunner.class)
public class YtDatabaseTest {

    private final List<Object> dataToUpload = of(new Object());

    @Mock
    private Yield<Object> yield;
    @Mock
    private YTableEntryType<Object> entryType;
    @Mock
    private Yt yt;
    @Mock(answer = Answers.RETURNS_DEEP_STUBS)
    private Cypress cypress;
    @Mock(answer = Answers.RETURNS_DEEP_STUBS)
    private HttpCommandExecutor httpCommandExecutor;
    @Mock
    private Transaction transaction;
    @Mock
    private YtTransactions ytTransactions;

    @Before
    public void setUp() throws Exception {
        setupMockedTransaction();
        setupMockedYtTransactions();
        setupMockedYt();
    }

    @Test
    public void exportToSingleYt() {
        checkExportToYt("yt-cluster-single");
    }

    @Test
    public void exportToMultipleYt() {
        checkExportToYt("yt-cluster-1", "yt-cluster-2");
    }

    private void checkExportToYt(String... proxies) {
        invokeExportToYt(asList(proxies), dataToUpload, yield);
        verify(yield, times(dataToUpload.size() * proxies.length)).yield(anyObject());
    }

    private void invokeExportToYt(List<String> proxies, List<Object> dataToUpload, Yield<Object> yield) {
        when(entryType.yield(any())).thenReturn(yield);
        YtDatabase ytDatabase = new MockedYtDatabase(proxies);
        ytDatabase.exportToYt(dataToUpload, entryType, null, null, false);
    }

    private void setupMockedYt() {
        when(yt.cypress()).thenReturn(cypress);
        when(yt.tables()).thenReturn(createYtTablesHttp());
        when(yt.transactions()).thenReturn(ytTransactions);
    }

    private YtTablesHttpImpl createYtTablesHttp() {
        YtTablesHttpImpl ytTables = new YtTablesHttpImpl();
        ytTables.setConfiguration(YtConfiguration.builder().withToken("").withApiHost("").build());
        ytTables.setYt(yt);
        ytTables.setExecutor(httpCommandExecutor);
        return ytTables;
    }

    private void setupMockedTransaction() {
        when(transaction.getId()).thenReturn(GUID.create());
    }

    private void setupMockedYtTransactions() {
        when(ytTransactions.startAndGet(anyObject())).thenReturn(transaction);
        when(ytTransactions.startAndGet(anyObject(), anyBoolean(), anyObject())).thenReturn(transaction);
    }

    public class MockedYtDatabase extends YtDatabase {

        public MockedYtDatabase(List<String> proxies) {
            setProxies(proxies);
            setTableYTPath("//r");
            setTableName("t");
            afterPropertiesSet();
        }

        @Override
        protected Yt createYtHttp(String p) {
            return yt;
        }
    }

}
