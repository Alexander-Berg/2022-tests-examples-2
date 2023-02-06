package ru.yandex.metrika.api.management.client.segments.streamabillity;

import java.util.Collection;
import java.util.Set;
import java.util.stream.Collectors;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.clickhouse.func.CHFunction;

import static org.junit.Assert.assertTrue;


@RunWith(Parameterized.class)
public class HardFunctionSetsImplementedTest {

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> params() {
        return FunctionSet.HARD_FUNCTIONS.stream()
                .map(FunctionSet::getFunctions)
                .flatMap(Set::stream)
                .map(f -> new Object[]{f})
                .collect(Collectors.toList());
    }


    @Parameterized.Parameter
    public CHFunction chFunction;

    @Test
    public void testHasApply() {
        assertTrue("Function " + chFunction.getName() + " has no implementation", chFunction.hasApply());
    }
}
