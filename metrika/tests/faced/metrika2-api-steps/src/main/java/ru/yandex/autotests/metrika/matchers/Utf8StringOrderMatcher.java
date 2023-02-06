package ru.yandex.autotests.metrika.matchers;

import java.nio.charset.StandardCharsets;
import java.util.Collection;
import java.util.stream.Collectors;

import org.hamcrest.Description;
import org.hamcrest.TypeSafeMatcher;

import ru.yandex.autotests.irt.testutils.matchers.OrderMatcher;

public class Utf8StringOrderMatcher extends TypeSafeMatcher<Collection<String>> {

    private OrderMatcher orderMatcher;

    Utf8StringOrderMatcher(OrderMatcher orderMatcher) {
        this.orderMatcher = orderMatcher;
    }

    @Override
    protected boolean matchesSafely(Collection<String> strings) {
        return orderMatcher.matches(strings.stream().map(Utf8ByteArray::new).collect(Collectors.toList()));
    }

    @Override
    public void describeTo(Description description) {
        orderMatcher.describeTo(description);
    }

    static class Utf8ByteArray implements Comparable<Utf8ByteArray> {
        private byte[] bytes;

        Utf8ByteArray(String str) {
            this.bytes = str.getBytes(StandardCharsets.UTF_8);
        }

        @Override
        public int compareTo(Utf8ByteArray o) {
            int minLen = Math.min(bytes.length, o.bytes.length);
            for (int i = 0; i < minLen; i++) {
                final int i1 = Byte.toUnsignedInt(bytes[i]);
                final int i2 = Byte.toUnsignedInt(o.bytes[i]);
                if (i1 != i2) {
                    return i1 - i2;
                }
            }
            return bytes.length - o.bytes.length;
        }
    }
}
