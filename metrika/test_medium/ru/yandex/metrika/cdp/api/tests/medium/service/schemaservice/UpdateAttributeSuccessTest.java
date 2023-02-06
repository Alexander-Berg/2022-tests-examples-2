package ru.yandex.metrika.cdp.api.tests.medium.service.schemaservice;

import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;

import org.junit.Before;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.springframework.test.context.ContextConfiguration;

import ru.yandex.metrika.cdp.dto.schema.Attribute;
import ru.yandex.metrika.cdp.dto.schema.EntityNamespace;

import static java.util.stream.Collectors.toMap;
import static org.junit.Assert.assertTrue;

@RunWith(Parameterized.class)
@ContextConfiguration(classes = {AbstractSchemaServiceTest.SchemaConfig.class})
public class UpdateAttributeSuccessTest extends AbstractSchemaServiceParameterizedTest {

    Attribute attr2WithAcceptableChanges;
    Map<String, Attribute> mapOfAttr;

    @Before
    public void testBody() {
        schemaService.saveAttributes(getCounterId(), EntityNamespace.ORDER, List.of(attr2));
        attr2WithAcceptableChanges = new Attribute(getCounterId(),
                attr2.getName(),
                attr2.getType(),
                attr2.getMultivalued(),
                attr2.getHumanized().toUpperCase() + "something");
        schemaService.saveAttributes(getCounterId(), EntityNamespace.ORDER, List.of(attr2WithAcceptableChanges));
        mapOfAttr = schemaService
                .getCustomAttributes(getCounterId(), EntityNamespace.ORDER)
                .stream().collect(toMap(Attribute::getName, x -> x));
    }

    @Parameterized.Parameters(name = "{1}")
    public static List<Object[]> getParameters() {
        return Arrays.asList(
                new Object[][]{
                        {c(test -> assertTrue(test.mapOfAttr.size() >= 1)),
                                "Тест количества загруженных атрибутов"},
                        {c(test -> assertTrue(isAttributeEqual(test.attr2WithAcceptableChanges,
                                                    test.mapOfAttr.get(test.attr2WithAcceptableChanges.getName())))),
                                "Тест корректности обновления атрибута"}
                }
        );
    }

    private static Consumer<UpdateAttributeSuccessTest> c(Consumer<UpdateAttributeSuccessTest> x) {
        return x;
    }
}
