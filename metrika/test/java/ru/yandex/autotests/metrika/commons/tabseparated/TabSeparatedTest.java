package ru.yandex.autotests.metrika.commons.tabseparated;

import com.google.common.collect.ImmutableList;
import org.junit.Test;

import java.util.List;

import static java.nio.charset.StandardCharsets.UTF_8;
import static org.apache.commons.lang3.ArrayUtils.EMPTY_BYTE_ARRAY;
import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;

public class TabSeparatedTest {
    @Test
    public void split() {
        byte[] input = "A\\tB\tC\\nD\n1\t2\n".getBytes(UTF_8);

        assertThat(TabSeparated.split(input),
                beanEquivalent(
                        ImmutableList.of(
                                ImmutableList.of("A\\tB".getBytes(UTF_8), "C\\nD".getBytes(UTF_8)),
                                ImmutableList.of("1".getBytes(UTF_8), "2".getBytes())
                        )));
    }

    @Test
    public void splitEmpty() {
        byte[] input = EMPTY_BYTE_ARRAY;

        assertThat(TabSeparated.split(input),
                beanEquivalent(ImmutableList.of()));
    }

    @Test
    public void splitSingleLine() {
        byte[] input = "\n".getBytes(UTF_8);

        assertThat(TabSeparated.split(input),
                beanEquivalent(
                        ImmutableList.of(
                                ImmutableList.of(EMPTY_BYTE_ARRAY)
                        )));
    }

    @Test
    public void splitSingleLineExtra() {
        byte[] input = "\t".getBytes(UTF_8);

        assertThat(TabSeparated.split(input),
                beanEquivalent(
                        ImmutableList.of(
                                ImmutableList.of(EMPTY_BYTE_ARRAY, EMPTY_BYTE_ARRAY)
                        )));
    }

    @Test
    public void splitMultiLineExtra() {
        byte[] input = "x\ty\nq\t".getBytes(UTF_8);

        assertThat(TabSeparated.split(input),
                beanEquivalent(
                        ImmutableList.of(
                                ImmutableList.of("x".getBytes(UTF_8), "y".getBytes(UTF_8)),
                                ImmutableList.of("q".getBytes(UTF_8), EMPTY_BYTE_ARRAY)
                        )));
    }

    @Test
    public void splitSingleLineSingleValueSingleLine() {
        byte[] input = "xxx\n".getBytes(UTF_8);

        assertThat(TabSeparated.split(input),
                beanEquivalent(
                        ImmutableList.of(
                                ImmutableList.of("xxx".getBytes(UTF_8))
                        )));
    }

    @Test
    public void splitMultiLineSingleValueSingleLine() {
        byte[] input = "xxx\nyyy".getBytes(UTF_8);

        assertThat(TabSeparated.split(input),
                beanEquivalent(
                        ImmutableList.of(
                                ImmutableList.of("xxx".getBytes(UTF_8)),
                                ImmutableList.of("yyy".getBytes(UTF_8))
                        )));
    }

    @Test
    public void splitSingleLineSingleValueSingleLineExtra() {
        byte[] input = "xxx\t\n".getBytes(UTF_8);

        assertThat(TabSeparated.split(input),
                beanEquivalent(
                        ImmutableList.of(
                                ImmutableList.of("xxx".getBytes(UTF_8), EMPTY_BYTE_ARRAY)
                        )));
    }

    @Test
    public void splitSingleLineSingleValue() {
        byte[] input = "xxx".getBytes(UTF_8);

        assertThat(TabSeparated.split(input),
                beanEquivalent(
                        ImmutableList.of(
                                ImmutableList.of("xxx".getBytes(UTF_8))
                        )));
    }

    @Test
    public void splitSingleLineMultiValue() {
        byte[] input = "xxx\tzzz".getBytes(UTF_8);

        assertThat(TabSeparated.split(input),
                beanEquivalent(
                        ImmutableList.of(
                                ImmutableList.of("xxx".getBytes(UTF_8), "zzz".getBytes(UTF_8))
                        )));
    }

    @Test
    public void splitSingleLineMultiValueExtra() {
        byte[] input = "xxx\tzzz\t".getBytes(UTF_8);

        assertThat(TabSeparated.split(input),
                beanEquivalent(
                        ImmutableList.of(
                                ImmutableList.of("xxx".getBytes(UTF_8), "zzz".getBytes(UTF_8), EMPTY_BYTE_ARRAY)
                        )));
    }

    @Test
    public void join() {
        List<List<byte[]>> input = ImmutableList.of(
                ImmutableList.of("A\\tB".getBytes(UTF_8), "C\\nD".getBytes(UTF_8)),
                ImmutableList.of("1".getBytes(UTF_8), "2".getBytes())
        );

        assertThat(TabSeparated.join(input),
                beanEquivalent("A\\tB\tC\\nD\n1\t2\n".getBytes(UTF_8)));
    }
}
