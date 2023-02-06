package ru.yandex.metrika.cdp.api.tests.medium.service.schemaservice;

import java.util.Set;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringRunner;

import ru.yandex.metrika.cdp.dto.schema.CustomEvent;

@RunWith(SpringRunner.class)
@ContextConfiguration(classes = {AbstractSchemaServiceTest.SchemaConfig.class})
public class SaveCustomEventTest extends AbstractSchemaServiceTest{

    /**
     * Этот тест ничего не проверяет, так как customEvent'ы ещё толком нигде не используются
     * и нет нормального механизма их чтения из базы.
     */
    @Test
    public void testBody() {
        var customEvent = new CustomEvent();
        customEvent.setHumanized("Какой-то тип события");
        customEvent.setName("some_event");
        customEvent.setAttributes(Set.of(attr, attr2));

        schemaService.saveCustomEvent(getCounterId(), customEvent);
    }
}
