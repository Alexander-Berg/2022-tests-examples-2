package ru.yandex.metrika.dbclients.ytrpc;

import java.util.Collection;
import java.util.Iterator;
import java.util.function.BiConsumer;
import java.util.function.Function;

import com.google.common.collect.Iterators;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.mockito.Mockito;

import ru.yandex.yt.ytclient.proxy.YtClient;
import ru.yandex.yt.ytclient.proxy.YtClientMock;
import ru.yandex.yt.ytclient.wire.UnversionedRow;

import static com.google.common.collect.ImmutableList.of;
import static org.mockito.Mockito.anyString;
import static org.mockito.Mockito.verify;
import static org.mockito.internal.verification.VerificationModeFactory.times;

@RunWith(Parameterized.class)
public class YtDaoTest {
    private YtClient ytClient;
    private YtDao dao;

    @Parameterized.Parameter
    public int queryLimit;

    @Parameterized.Parameter(1)
    public int tableSize;

    @Parameterized.Parameter(2)
    public int expectedLookups;

    @Parameterized.Parameters(name = "query limit: {0}, table size: {1}, expected lookups: {2}")
    public static Collection<Object[]> createParameters() {
        return of(
                param(2, 6, 4),
                param(2, 2, 2),
                param(10, 10, 2),
                param(11, 10, 2)
        );
    }

    @Before
    public void setUp() throws Exception {
        ytClient = Mockito.spy(YtClientMock.getInstance(queryLimit, tableSize));
        dao = new YtDao(new YtTransactionalClientMock(ytClient));
        performQueryByChunks();
    }

    @Test
    public void doesExpectedDatabaseLookupsWhenQueryByChunks() {
        verify(ytClient, times(expectedLookups)).selectRows(anyString());
    }

    private void performQueryByChunks() {
        String query = "value where value > %s";
        Object[] initialQueryParams = new Object[]{"0"};
        Function<UnversionedRow, Long> mapper = row -> row.getValues().get(0).longValue();
        BiConsumer<Long, Object[]> setter = (param, queryParams) -> queryParams[0] = Long.toUnsignedString(param);
        Iterator<Long> it = dao.queryByChunks(query, initialQueryParams, mapper, setter).iterator();
        Iterators.advance(it, tableSize + 1);
    }

    private static Object[] param(int queryLimit, int tableSize, int expectedLookups) {
        return new Object[]{queryLimit, tableSize, expectedLookups};
    }
}
