package ru.yandex.audience.uploading.crm;

import java.util.Arrays;
import java.util.Collection;

import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import static org.assertj.core.api.Assertions.assertThat;
import static ru.yandex.audience.uploading.crm.CsvField.EMAIL;
import static ru.yandex.audience.uploading.crm.CsvField.PHONE;

@RunWith(Parameterized.class)
public class CrmFieldPreprocessorTest {

    private static CrmFieldPreprocessor preprocessor;
    @Parameterized.Parameter
    public String name;
    @Parameterized.Parameter(1)
    public CsvField csvField;
    @Parameterized.Parameter(2)
    public String input;
    @Parameterized.Parameter(3)
    public String expected;

    @Parameterized.Parameters(name = "{1}: {0}")
    public static Collection<Object[]> createParameters() {
        return Arrays.asList(
                new Object[][]{
                        {"remove spaces in the beginning and end", EMAIL, " aaa@yandex.ru  ", "aaa@yandex.ru"},
                        {"remove spaces in the beginning and end", PHONE, " 79112223344  ", "79112223344"},
                        {"convert uppercase to lowercase", EMAIL, "AAA@YANDEX.RU", "aaa@yandex.ru"},
                        {"remove leading '+'", PHONE, "+79112223344", "79112223344"},
                        {"replace leading '8' to '7'", PHONE, "89112223344", "79112223344"},
                        {"replace leading '8' to '7' in '8'", PHONE, "8", "7"},
                        {"removes braces", PHONE, "7(911)2223344", "79112223344"},
                        {"removes dashes", PHONE, "7-911-222-33-44", "79112223344"},
                        {"empty string interpreted as null", EMAIL, "", null},
                        {"empty string interpreted as null", PHONE, "", null},
                }
        );
    }

    @BeforeClass
    public static void beforeClass() {
        preprocessor = new CrmFieldPreprocessor();
    }

    @Test
    public void preprocessLogic() {
        assertThat(preprocessor.preprocess(input, csvField)).isEqualTo(expected);
    }
}
