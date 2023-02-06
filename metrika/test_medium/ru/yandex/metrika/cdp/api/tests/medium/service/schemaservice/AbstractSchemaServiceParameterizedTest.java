package ru.yandex.metrika.cdp.api.tests.medium.service.schemaservice;

import java.util.function.Consumer;

import org.junit.ClassRule;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runners.Parameterized;
import org.springframework.test.context.junit4.rules.SpringClassRule;
import org.springframework.test.context.junit4.rules.SpringMethodRule;

public abstract class AbstractSchemaServiceParameterizedTest extends AbstractSchemaServiceTest{

    @ClassRule
    public static final SpringClassRule scr = new SpringClassRule();

    @Rule
    public final SpringMethodRule smr = new SpringMethodRule();

    @Parameterized.Parameter
    public Consumer<AbstractSchemaServiceParameterizedTest> check;

    @Parameterized.Parameter(1)
    public String testName;

    @Test
    public void test() {
        check.accept(this);
    }
}
