package ru.yandex.metrika.cdp.scheduler.bitrix.validation;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.regex.Pattern;

import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.cdp.scheduler.bitrix.BitrixTestUtils;
import ru.yandex.metrika.cdp.scheduler.bitrix.dto.BitrixStatusYt;

@RunWith(Parameterized.class)
public class BitrixStatusValidatorTest {
    private BitrixStatusValidator validator;

    @Parameterized.Parameter
    public String testName;

    @Parameterized.Parameter(value = 1)
    public BitrixStatusYt status;

    @Parameterized.Parameter(value = 2)
    public Integer errorsCount;

    @Before
    public void setUp() {
        validator = new BitrixStatusValidator(
                BitrixTestUtils.connectorsCache, true,
                BitrixTestUtils.activeCountersCache, true,
                List.of(Pattern.compile(BitrixTestUtils.DEALS_STATUSES_ENTITY_NAME + "[\\w-]*")),
                List.of(Pattern.compile(BitrixTestUtils.LEADS_STATUSES_ENTITY_NAME))
        );
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> parameters() {
        List<Object[]> parameters = new ArrayList<>();

        BitrixStatusYt validStatus = new BitrixStatusYt();
        validStatus.setCounterId(343);
        validStatus.setId("43");
        validStatus.setEntityId(BitrixTestUtils.DEALS_STATUSES_ENTITY_NAME);
        validStatus.setStatusId("valid-status:id");
        validStatus.setHumanized("Валидный статус");
        parameters.add(new Object[]{"Valid status", validStatus, 0});

        BitrixStatusYt validNotDefaultStatus = new BitrixStatusYt();
        validNotDefaultStatus.setCounterId(878);
        validNotDefaultStatus.setId("40");
        validNotDefaultStatus.setEntityId(BitrixTestUtils.DEALS_STATUSES_ENTITY_NAME + "_5");
        validNotDefaultStatus.setStatusId("valid-not-default-status:id");
        validNotDefaultStatus.setHumanized("Валидный статус в направлениях не по-умолчанию");
        parameters.add(new Object[]{"Valid not default status", validNotDefaultStatus, 0});

        BitrixStatusYt invalidStatus = new BitrixStatusYt();
        invalidStatus.setCounterId(BitrixTestUtils.NOT_ACTIVE_COUNTER_ID);
        invalidStatus.setId("2");
        invalidStatus.setEntityId(BitrixTestUtils.DEALS_STATUSES_ENTITY_NAME);
        invalidStatus.setStatusId("1nc0rr*ct@status");
        invalidStatus.setHumanized("");
        parameters.add(new Object[]{"Invalid status", invalidStatus, 3});

        BitrixStatusYt redundantStatus = new BitrixStatusYt();
        redundantStatus.setCounterId(65);
        redundantStatus.setId("65");
        redundantStatus.setEntityId("INCORRECT_ENTITY_ID");
        redundantStatus.setStatusId("doesnt_matter");
        redundantStatus.setHumanized("Не имеет значения");
        parameters.add(new Object[]{"Redundant status", redundantStatus, -1});

        BitrixStatusYt leadStatusWithDisabledLeads = new BitrixStatusYt();
        leadStatusWithDisabledLeads.setCounterId(BitrixTestUtils.COUNTER_ID_WITH_DISABLED_LEADS);
        leadStatusWithDisabledLeads.setId("124");
        leadStatusWithDisabledLeads.setEntityId(BitrixTestUtils.LEADS_STATUSES_ENTITY_NAME);
        leadStatusWithDisabledLeads.setStatusId("lead_status-id");
        leadStatusWithDisabledLeads.setHumanized("Статус лида");
        parameters.add(new Object[]{"Lead status with disabled lead", leadStatusWithDisabledLeads, 1});

        return parameters;
    }

    @Test
    public void isValidTest() {
        if (errorsCount == 0) {
            Assert.assertTrue(validator.isValid(status));
        } else {
            Assert.assertFalse(validator.isValid(status));
        }
        // Для лишних статусов, которые мы не хотим загружать и записывать о них кучу мусора в статлог
        if (errorsCount < 0) {
            errorsCount = 0;
        }
        BitrixTestUtils.assertValidatorErrorsSize(validator, errorsCount);
    }
}
