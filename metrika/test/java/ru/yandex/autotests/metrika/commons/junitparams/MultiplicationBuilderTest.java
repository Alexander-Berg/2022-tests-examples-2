package ru.yandex.autotests.metrika.commons.junitparams;

import com.google.common.collect.ImmutableList;
import org.apache.commons.lang3.tuple.Pair;
import org.junit.Test;

import java.util.Collection;
import java.util.Objects;
import java.util.stream.Stream;

import static com.google.common.collect.ImmutableList.of;
import static java.lang.String.format;
import static java.util.function.Function.identity;
import static java.util.stream.Collectors.joining;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanDiffer;

/**
 * Created by konkov on 05.09.2016.
 */
public class MultiplicationBuilderTest {

    private static void dumpParams(Collection<Object[]> params) {
        System.out.println(format("Всего наборов параметров: %s", params.size()));
        for (Object[] param : params) {
            System.out.println(Stream.of(param).map(o -> Objects.toString(o)).collect(joining(", ", "[ ", " ]")));
        }
    }

    public static class Holder {
        private String B;
        private String C;

        public String getB() {
            return this.B;
        }

        public String getC() {
            return this.C;
        }

        public Holder withB(final String B) {
            this.B = B;
            return this;
        }

        public Holder withC(final String C) {
            this.C = C;
            return this;
        }

        public Holder clone() {
            return new Holder()
                    .withB(getB())
                    .withC(getC());
        }

        @Override
        public String toString() {
            final StringBuilder sb = new StringBuilder("Holder{");
            sb.append("B='").append(B).append('\'');
            sb.append(", C='").append(C).append('\'');
            sb.append('}');
            return sb.toString();
        }

        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (o == null || getClass() != o.getClass()) return false;
            Holder holder = (Holder) o;
            return Objects.equals(B, holder.B) &&
                    Objects.equals(C, holder.C);
        }

        @Override
        public int hashCode() {
            return Objects.hash(B, C);
        }
    }

    @Test
    public void simpleUseCaseWithHolder() {
        Collection<Object[]> params = MultiplicationBuilder.<String, String, Holder>builder(
                ImmutableList.of("a1", "a2<B>", "a3<C>"), () -> new Holder())
                .apply(s -> s.contains("<B>"),
                        (s, h) -> Stream.of("b1", "b2").map(p -> Pair.of(s, h.clone().withB(p))))
                .apply(s -> s.contains("<C>"),
                        (s, h) -> Stream.of("c1", "c2").map(p -> Pair.of(s, h.clone().withC(p))))
                .build(identity());

        dumpParams(params);

        assertThat(params, beanDiffer(of(
                toArray("a1", new Holder()),
                toArray("a2<B>", new Holder().withB("b1")),
                toArray("a2<B>", new Holder().withB("b2")),
                toArray("a3<C>", new Holder().withC("c1")),
                toArray("a3<C>", new Holder().withC("c2")))));
    }

    @Test
    public void simpleUseCaseWithOutHolder() {
        Collection<Object[]> params = MultiplicationBuilder.<String, String, Holder>builder(
                ImmutableList.of("a1", "a2<B>", "a3<C>"), () -> null)
                .apply(s -> s.contains("<B>"),
                        (s, h) -> Stream.of("b1", "b2").map(p -> Pair.of(s.replace("<B>", p), h)))
                .apply(s -> s.contains("<C>"),
                        (s, h) -> Stream.of("c1", "c2").map(p -> Pair.of(s.replace("<C>", p), h)))
                .build(identity());

        dumpParams(params);

        assertThat(params, beanDiffer(of(
                toArray("a1", null),
                toArray("a2b1", null),
                toArray("a2b2", null),
                toArray("a3c1", null),
                toArray("a3c2", null))));
    }
}
