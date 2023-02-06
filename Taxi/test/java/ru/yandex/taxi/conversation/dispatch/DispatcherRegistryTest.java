package ru.yandex.taxi.conversation.dispatch;

import java.util.Arrays;
import java.util.Collections;
import java.util.LinkedList;
import java.util.List;
import java.util.Random;
import java.util.stream.Collectors;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

import ru.yandex.taxi.conversation.endpoint.Endpoint;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

public class DispatcherRegistryTest {

    private static final Random rnd = new Random();

    @Test
    void noOneDispatcher() {
        Assertions.assertThrows(IllegalStateException.class, () -> new DispatcherRegistry(Collections.emptyList()));
    }

    @Test
    void dispatchersDeficit() {
        var dispatchers = dispatchersForEveryChannel();
        var index = rnd.nextInt(dispatchers.size() - 1);
        dispatchers.remove(index);
        Assertions.assertThrows(IllegalStateException.class, () -> new DispatcherRegistry(dispatchers));
    }

    @Test
    void oneDispatcherForOneChannel() {
        Assertions.assertDoesNotThrow(() -> new DispatcherRegistry(dispatchersForEveryChannel()));
    }

    @Test
    void abundanceOfDispatchers() {
        var dispatchers = dispatchersForEveryChannel();
        var channels = Endpoint.Channel.values();
        var randomChannel = channels[rnd.nextInt(channels.length - 1)];
        var redundantDispatcher = mockDispatcher(randomChannel);
        dispatchers.add(redundantDispatcher);
        Assertions.assertThrows(IllegalStateException.class, () -> new DispatcherRegistry(dispatchers));
    }

    private List<Dispatcher<?, ?>> dispatchersForEveryChannel() {
        return Arrays.stream(Endpoint.Channel.values())
                .map(this::mockDispatcher)
                .collect(Collectors.toCollection(LinkedList::new));
    }

    private Dispatcher<?, ?> mockDispatcher(Endpoint.Channel channel) {
        var dispatcher = mock(Dispatcher.class, channel + "Dispatcher");
        when(dispatcher.getTargetChannel()).thenReturn(channel);
        return dispatcher;
    }
}
