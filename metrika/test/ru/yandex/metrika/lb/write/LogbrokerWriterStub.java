package ru.yandex.metrika.lb.write;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import java.util.concurrent.CompletableFuture;
import java.util.function.BiPredicate;

import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.core.IsCollectionContaining.hasItem;
import static org.hamcrest.core.IsCollectionContaining.hasItems;
import static org.junit.Assert.assertThat;
import static org.junit.Assert.assertTrue;

public class LogbrokerWriterStub<T> implements LogbrokerWriter<T> {

    private final List<T> messages = new ArrayList<>();

    @Override
    public CompletableFuture<Void> writeBatchAsync(List<T> list) {
        messages.addAll(list);
        return CompletableFuture.completedFuture(null);
    }

    @Override
    public void close() {

    }

    @SafeVarargs
    public final void assertHaveOnlyMessages(T... ts) {
        assertThat(messages, hasItems(ts));
        assertThat(messages, hasSize(ts.length));
    }

    public final void assertHaveOnlyMessages(List<T> ts) {
        assertThat(messages, hasSize(ts.size()));
        for (T t : ts) {
            assertThat(messages, hasItem(t));
        }
    }

    @SafeVarargs
    public final void assertHaveOnlyMessagesInOrder(T... ts) {
        assertHaveOnlyMessagesInOrder(Arrays.asList(ts));
    }

    public final void assertHaveOnlyMessagesInOrder(List<T> ts) {
        assertHaveOnlyMessagesInOrder(Objects::equals, ts);
    }

    @SafeVarargs
    public final void assertHaveOnlyMessagesInOrder(BiPredicate<T, T> equality, T... ts) {
        assertHaveOnlyMessagesInOrder(equality, Arrays.asList(ts));
    }

    public final void assertHaveOnlyMessagesInOrder(BiPredicate<T, T> equality, List<T> ts) {
        boolean ok = messages.size() == ts.size();
        for (int i = 0; i < messages.size() && ok; i++) {
            ok = equality.test(messages.get(i), ts.get(i));
        }
        assertTrue("Expected " + ts + ", but got " + messages, ok);
    }

    public final void assertHaveExactlyOneMessage(T t) {
        assertThat(messages, equalTo(List.of(t)));
    }

    public final void assertHaveNoMessages() {
        assertThat(messages, empty());
    }

    public final List<T> getMessages() {
        return List.copyOf(messages);
    }

    public void clear() {
        messages.clear();
    }
}
