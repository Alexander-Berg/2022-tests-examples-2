package ru.yandex.autotests.metrika.commons.tabseparated;


import com.google.common.collect.ImmutableList;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.junit.Test;

import java.util.List;
import java.util.Map;

import static java.nio.charset.StandardCharsets.UTF_8;
import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;

public class TabSeparatedKeyValueTest {
    @Test
    public void split() {
        byte[] input = "tskv\tkey with \\= equal=value with = equal\ntskv\tk=v\n".getBytes(UTF_8);

        assertThat(TabSeparatedKeyValue.split(input),
                beanEquivalent(
                        ImmutableList.of(
                                ImmutableList.of(ImmutablePair.of("key with = equal", "value with = equal".getBytes(UTF_8))),
                                ImmutableList.of(ImmutablePair.of("k", "v".getBytes(UTF_8)))
                        )));
    }

    @Test
    public void join() {
        List<List<Map.Entry<String, byte[]>>> input = ImmutableList.of(
                ImmutableList.of(ImmutablePair.of("key with = equal", "value with = equal".getBytes(UTF_8))),
                ImmutableList.of(ImmutablePair.of("k", "v".getBytes(UTF_8))));

        assertThat(TabSeparatedKeyValue.join(input),
                beanEquivalent("tskv\tkey with \\= equal=value with = equal\ntskv\tk=v\n".getBytes(UTF_8)));
    }
}
