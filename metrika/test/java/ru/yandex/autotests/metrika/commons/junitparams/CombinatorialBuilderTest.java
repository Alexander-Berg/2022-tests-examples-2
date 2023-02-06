package ru.yandex.autotests.metrika.commons.junitparams;

import org.junit.Test;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;

import java.util.Collection;
import java.util.Objects;
import java.util.stream.Stream;

import static com.google.common.collect.ImmutableList.of;
import static java.lang.String.format;
import static java.util.stream.Collectors.joining;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanDiffer;

/**
 * Created by konkov on 25.04.2016.
 */
public class CombinatorialBuilderTest {

    private static void dumpParams(Collection<Object[]> params) {
        System.out.println(format("Всего наборов параметров: %s", params.size()));
        for (Object[] param : params) {
            System.out.println(Stream.of(param).map(o -> Objects.toString(o)).collect(joining(", ", "[ ", " ]")));
        }
    }

    @Test(expected = IllegalStateException.class)
    public void emptyShouldThrowException() {
        Collection<Object[]> params = CombinatorialBuilder.builder()
                .build();
    }

    @Test
    public void oneParamOneValue() {
        Collection<Object[]> params = CombinatorialBuilder.builder()
                .value(1)
                .build();

        dumpParams(params);

        assertThat(params, beanDiffer(of(toArray((Object) 1))));
    }

    @Test
    public void twoParamsTwoValues() {
        Collection<Object[]> params = CombinatorialBuilder.builder()
                .values("A", "B")
                .values("Z", "X")
                .build();

        dumpParams(params);

        assertThat(params, beanDiffer(of(
                toArray("A", "Z"),
                toArray("B", "Z"),
                toArray("A", "X"),
                toArray("B", "X"))));
    }

    @Test
    public void withNulls() {
        Collection<Object[]> params = CombinatorialBuilder.builder()
                .values("A", "B")
                .values("Z", null)
                .build();

        dumpParams(params);

        assertThat(params, beanDiffer(of(
                toArray("A", "Z"),
                toArray("B", "Z"),
                toArray("A", null),
                toArray("B", null))));
    }

    @Test
    public void valueFlat() {
        Collection<Object[]> params = CombinatorialBuilder.builder()
                .values("A", "B")
                .vectorValue(toArray("C1", "D1"))
                .build();

        dumpParams(params);

        assertThat(params, beanDiffer(of(
                toArray("A", "C1", "D1"),
                toArray("B", "C1", "D1"))));
    }

    @Test
    public void valueFlatEquivalentInValue() {
        Collection<Object[]> params = CombinatorialBuilder.builder()
                .values("A", "B")
                .value("C1")
                .value("D1")
                .build();

        dumpParams(params);

        assertThat(params, beanDiffer(of(
                toArray("A", "C1", "D1"),
                toArray("B", "C1", "D1"))));
    }

    @Test
    public void valuesFlat() {
        Collection<Object[]> params = CombinatorialBuilder.builder()
                .values("A", "B")
                .vectorValues(of("C1", "D1"), of("C2", "D2"))
                .build();

        dumpParams(params);

        assertThat(params, beanDiffer(of(
                toArray("A", "C1", "D1"),
                toArray("B", "C1", "D1"),
                toArray("A", "C2", "D2"),
                toArray("B", "C2", "D2"))));
    }

    @Test
    public void valuesFlat2() {
        Collection<Object[]> params = CombinatorialBuilder.builder()
                .vectorValues(of("C1", "D1"), of("C2", "D2"))
                .values("A", "B")
                .build();

        dumpParams(params);

        assertThat(params, beanDiffer(of(
                toArray("C1", "D1", "A"),
                toArray("C2", "D2", "A"),
                toArray("C1", "D1", "B"),
                toArray("C2", "D2", "B")
                )));
    }
}
