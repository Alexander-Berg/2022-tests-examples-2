package ru.yandex.taxi.ququmber.clients.saas;

import java.util.concurrent.TimeUnit;

import org.apache.commons.lang3.builder.EqualsBuilder;
import org.apache.commons.lang3.builder.HashCodeBuilder;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

class QueueNoDuplicatesTest {

    @Test
    public void testSimple() throws InterruptedException {
        QueueNoDuplicates<Integer, T> queue = new QueueNoDuplicates<>(t -> t.key, 2);
        long start = System.nanoTime();
        queue.add(new T(1, "a"));
        QueueNoDuplicates.PollResult<T> res = queue.poll();
        long spent = System.nanoTime() - start;
        Assertions.assertTrue(TimeUnit.NANOSECONDS.toMillis(spent) >= 2000);
        Assertions.assertEquals(new T(1, "a"), res.value);
        Assertions.assertTrue(res.duplicates.isEmpty());
        Assertions.assertTrue(queue.isEmpty());
    }

    @Test
    public void testDroppedDuplicate() throws InterruptedException {
        QueueNoDuplicates<Integer, T> queue = new QueueNoDuplicates<>(t -> t.key, 2);
        long start = System.nanoTime();
        queue.add(new T(1, "a"));
        queue.add(new T(2, "b"));
        queue.add(new T(1, "c"));
        QueueNoDuplicates.PollResult<T> item1 = queue.poll();
        QueueNoDuplicates.PollResult<T> item2 = queue.poll();
        long spent = System.nanoTime() - start;
        Assertions.assertTrue(TimeUnit.NANOSECONDS.toMillis(spent) >= 2000);

        Assertions.assertEquals(new T(2, "b"), item1.value);
        Assertions.assertTrue(item1.duplicates.isEmpty());
        Assertions.assertEquals(new T(1, "c"), item2.value);
        Assertions.assertEquals(new T(1, "a"), item2.duplicates.get(0));
        Assertions.assertTrue(queue.isEmpty());
    }

    static class T {
        int key;
        String value;

        public T(int key, String value) {
            this.key = key;
            this.value = value;
        }

        @Override
        public boolean equals(Object o) {
            if (this == o) {
                return true;
            }

            if (o == null || getClass() != o.getClass()) {
                return false;
            }

            T t = (T) o;

            return new EqualsBuilder().append(key, t.key).append(value, t.value).isEquals();
        }

        @Override
        public int hashCode() {
            return new HashCodeBuilder(17, 37).append(key).append(value).toHashCode();
        }
    }

}
