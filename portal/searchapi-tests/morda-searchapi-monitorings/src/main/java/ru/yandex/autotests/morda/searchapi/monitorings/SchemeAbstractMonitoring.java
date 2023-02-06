package ru.yandex.autotests.morda.searchapi.monitorings;

import com.fasterxml.jackson.core.JsonProcessingException;
import org.junit.After;
import org.junit.Rule;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.morda.rules.monitorings.BottleMessageAttachmentRule;
import ru.yandex.autotests.morda.searchapi.tests.scheme.SchemeAbstractTest;

import static ru.yandex.autotests.morda.searchapi.tests.scheme.ValidateSchemeUtils.OBJECT_MAPPER;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 04/06/15
 */
@RunWith(Parameterized.class)
public class SchemeAbstractMonitoring extends SchemeAbstractTest {

    @Rule
    public BottleMessageAttachmentRule bottleMessageRule = new BottleMessageAttachmentRule();

    public SchemeAbstractMonitoring(ValidationCase validationCase){
        super(validationCase);
    }

    @After
    public void attachMetas() throws JsonProcessingException {
        bottleMessageRule.addMeta("response.json",
                OBJECT_MAPPER.writerWithDefaultPrettyPrinter().writeValueAsString(response));
        if (!report.isSuccess()) {
            bottleMessageRule.addMeta("error.json",
                    OBJECT_MAPPER.writerWithDefaultPrettyPrinter().writeValueAsString(report.asJson()));
        }
    }
}
