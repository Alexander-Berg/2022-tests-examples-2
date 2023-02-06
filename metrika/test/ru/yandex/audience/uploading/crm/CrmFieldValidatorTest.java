package ru.yandex.audience.uploading.crm;

import java.util.Arrays;
import java.util.Collection;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.util.StringUtil;

import static java.lang.Boolean.FALSE;
import static java.lang.Boolean.TRUE;
import static org.junit.Assert.assertTrue;
import static ru.yandex.audience.uploading.crm.CsvField.EMAIL;
import static ru.yandex.audience.uploading.crm.CsvField.PHONE;

@RunWith(Parameterized.class)
public class CrmFieldValidatorTest {

    private static final Boolean VALID = TRUE;
    private static final Boolean INVALID = FALSE;
    private static final Boolean HASHED = TRUE;
    private static final Boolean NON_HASHED = FALSE;

    @Parameterized.Parameter
    public String comment;
    @Parameterized.Parameter(1)
    public CsvField csvField;
    @Parameterized.Parameter(2)
    public String input;
    @Parameterized.Parameter(3)
    public Boolean hashed;
    @Parameterized.Parameter(4)
    public Boolean validity;

    @Parameterized.Parameters(name = "{1}, hashed={3}, valid={4}, {0}")
    public static Collection<Object[]> createParameters() {
        return Arrays.asList(
                new Object[][]{
                        {"", PHONE, "74957397000", NON_HASHED, VALID},
                        {"", PHONE, "bdjahsdg", NON_HASHED, INVALID},
                        {"empty", PHONE, "", NON_HASHED, INVALID},
                        {"empty", PHONE, "", HASHED, INVALID},
                        {"", EMAIL, "volozh@yandex-team.ru", NON_HASHED, VALID},
                        {"", EMAIL, "bad-email", NON_HASHED, INVALID},
                        {"empty", EMAIL, "", NON_HASHED, INVALID},
                        {"empty", EMAIL, "", HASHED, INVALID},
                        {"", PHONE, StringUtil.stringMd5("somestring"), HASHED, VALID},
                        {"", PHONE, "somestring", HASHED, INVALID},
                        {"", EMAIL, StringUtil.stringMd5("somestring"), HASHED, VALID},
                        {"", EMAIL, "somestring", HASHED, INVALID},
                }
        );
    }

    private CrmFieldValidator validator;

    @Before
    public void setUp() throws Exception {
        validator = new CrmFieldValidator(hashed);
    }

    @Test
    public void validationLogic() {
        assertTrue(validator.isValid(input, csvField) == validity);
    }
}
