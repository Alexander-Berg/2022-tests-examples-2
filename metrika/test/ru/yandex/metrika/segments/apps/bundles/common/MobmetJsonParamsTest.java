package ru.yandex.metrika.segments.apps.bundles.common;

import java.util.Collection;
import java.util.List;

import com.google.common.collect.ImmutableList;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import static org.assertj.core.api.Assertions.assertThat;

@RunWith(Parameterized.class)
public class MobmetJsonParamsTest {

    @Parameterized.Parameter
    public String input;

    @Parameterized.Parameter(1)
    public List<String> expected;

    @Parameterized.Parameters(name = "input {0}, expected {1}")
    public static Collection<Object[]> initParams() {
        return new ImmutableList.Builder<Object[]>()
                .add(new Object[]{"a1\\.", List.of("a1.")})
                .add(new Object[]{"a1.b1.c2", List.of("a1", "b1", "c2")})
                .add(new Object[]{"a1\\.b1.c2", List.of("a1.b1", "c2")})
                .add(new Object[]{"a1\\.b1.c\n2", List.of("a1.b1", "c\n2")})
                .add(new Object[]{"a1\\\\.b1.c\n2", List.of("a1\\", "b1", "c\n2")})
                .build();
    }

    @Test
    public void test() {
        List<String> actual = MobmetJsonParams.parseParamPath(input);
        assertThat(actual).isEqualTo(expected);
    }
}
