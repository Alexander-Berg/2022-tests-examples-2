package ru.yandex.metrika.ui.webvisor.dao2;

import java.util.List;
import java.util.Set;
import java.util.concurrent.CompletableFuture;
import java.util.stream.IntStream;

import org.junit.Test;

import ru.yandex.inside.yt.kosher.impl.ytree.object.serializers.YTreeObjectSerializer;
import ru.yandex.yt.ytclient.proxy.SelectRowsRequest;
import ru.yandex.yt.ytclient.proxy.YtClient;

import static org.hamcrest.Matchers.containsInAnyOrder;
import static org.junit.Assert.assertThat;
import static org.junit.Assert.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

public class YtEventDaoTest {

    private final YTreeObjectSerializer<Wv2YtData> serializer = new YTreeObjectSerializer<>(Wv2YtData.class);

    @Test
    public void findEmpty() {
        YtEventDao dao = new YtEventDao(List.of());
        assertTrue(dao.find("", 1, 1, Set.of(1), serializer).isEmpty());
    }

    @Test
    public void findFromOneSource() {
        int sz = 100;
        List<Wv2YtData> data = genData(sz);
        YtClient client = createYtClientWithData(data);
        YtEventDao dao = new YtEventDao(List.of(client));
        var result = dao.find("", 1, 1, Set.of(42), serializer);
        assertThat(result, containsInAnyOrder(data.toArray()));
    }


    @Test
    public void findFromTwoSourceAndDeduplicate() {
        int sz = 100;
        List<Wv2YtData> fullData = genData(sz);
        YtClient client1 = createYtClientWithData(fullData.subList(0, 75));
        YtClient client2 = createYtClientWithData(fullData.subList(25, 100));
        YtEventDao dao = new YtEventDao(List.of(client1, client2));
        var result = dao.find("", 1, 1, Set.of(42), serializer);
        assertThat(result, containsInAnyOrder(fullData.toArray()));
    }

    @Test
    public void findFromTwoSourceWhenOneThrows() {
        int sz = 100;
        List<Wv2YtData> data = genData(sz);
        YtClient client1 = createYtClientWithData(data);
        YtClient client2 = createYtClientWithException();
        YtEventDao dao = new YtEventDao(List.of(client1, client2));
        var result = dao.find("", 1, 1, Set.of(42), serializer);
        assertThat(result, containsInAnyOrder(data.toArray()));
    }

    @Test(expected = RuntimeException.class)
    public void findFromTwoSourceWhenTwoThrows() {
        YtClient client1 = createYtClientWithException();
        YtClient client2 = createYtClientWithException();
        YtEventDao dao = new YtEventDao(List.of(client1, client2));
        dao.find("", 1, 1, Set.of(42), serializer);
    }

    private YtClient createYtClientWithData(List<Wv2YtData> data) {
        YtClient client = mock(YtClient.class);

        when(client.selectRows(any(SelectRowsRequest.class), any(YTreeObjectSerializer.class)))
                .thenReturn(CompletableFuture.completedFuture(data));
        return client;
    }

    private YtClient createYtClientWithException() {
        YtClient client = mock(YtClient.class);

        when(client.selectRows(any(SelectRowsRequest.class), any(YTreeObjectSerializer.class)))
                .thenReturn(CompletableFuture.failedFuture(new RuntimeException("connection failed")));
        return client;
    }

    private YtClient createYtClientWithExceptionThanReturnData(List<Wv2YtData> data) {
        YtClient client = mock(YtClient.class);

        when(client.selectRows(any(SelectRowsRequest.class), any(YTreeObjectSerializer.class)))
                .thenReturn(CompletableFuture.failedFuture(new RuntimeException("connection failed")))
                .thenReturn(CompletableFuture.completedFuture(data));
        return client;
    }

    private List<Wv2YtData> genData(int size) {
        return IntStream.range(0, size).mapToObj(i -> {
            var newPart = new Wv2YtData();
            newPart.setHit(42);
            newPart.setPart(i);
            return newPart;
        }).toList();
    }
}
