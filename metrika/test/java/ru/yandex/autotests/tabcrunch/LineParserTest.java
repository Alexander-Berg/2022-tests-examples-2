package ru.yandex.autotests.tabcrunch;

import com.google.common.collect.ImmutableList;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.tabcrunch.util.LineParser;

import java.nio.charset.StandardCharsets;
import java.util.Collection;
import java.util.List;

import static com.google.common.collect.ImmutableList.of;
import static java.util.Collections.emptyList;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;

/**
 * Created by konkov on 07.09.2016.
 */
@RunWith(Parameterized.class)
public class LineParserTest {

    @Parameterized.Parameter()
    public byte[] source;

    @Parameterized.Parameter(1)
    public List<String> expected;

    @Parameterized.Parameters(name = "{0} : {1}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(param("", ""))
                .add(param("a", "a"))
                .add(param("a\tb", "a", "b"))
                .add(param("a\tb\t", "a", "b", ""))
                .add(param("\t", "", ""))
                .add(param("\t\t", "", "", ""))
                .build();
    }

    private static Object[] param(String source, String... expected) {
        return new Object[]
                {
                        source.getBytes(StandardCharsets.UTF_8),
                        expected == null ?
                                emptyList() :
                                ImmutableList.<String>builder()
                                        .add(expected)
                                        .build()
                };
    }


    @Test
    public void test() {
        LineParser lineParser = new LineParser();

        List<String> actual = lineParser.parseLine(source);

        assertThat(actual, equalTo(expected));
    }
}
