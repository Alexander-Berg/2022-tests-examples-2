package ru.yandex.metrika.expenses.connectors.google;

import java.util.Arrays;
import java.util.Collection;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.google.ads.googleads.v9.enums.ConversionActionCategoryEnum;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.util.json.ObjectMappersFactory;

import static org.junit.Assert.assertEquals;

@RunWith(Parameterized.class)
public class GoogleExpenseConversionsTest {

    @Parameterized.Parameter
    public String name;
    @Parameterized.Parameter(1)
    public GoogleExpenseConversions conversions;
    @Parameterized.Parameter(2)
    public Long conversionActionId;

    @Parameterized.Parameters(name = "{0}[{2}]")
    public static Collection<Object[]> getParameters() {
        return Arrays.asList(
                new Object[][]{
                        {
                                "Data Empty",
                                new GoogleExpenseConversions(
                                        0.,
                                        0.,
                                        "customers/0/conversionActions/0",
                                        "TEST",
                                        ConversionActionCategoryEnum.ConversionActionCategory.DEFAULT
                                ),
                                0L
                        },
                        {
                                "Data Sample",
                                new GoogleExpenseConversions(
                                        14.,
                                        46655.,
                                        "customers/9482315431/conversionActions/522780200",
                                        "Беру - товары для жизни (iOS) purchase_without_credit_multiorder (Firebase)",
                                        ConversionActionCategoryEnum.ConversionActionCategory.PURCHASE
                                ),
                                522780200L
                        },
                        {
                                "Data Sample #2",
                                new GoogleExpenseConversions(
                                        472.,
                                        472.,
                                        "customers/9482315431/conversionActions/265471890",
                                        "ru.yandex.blue.market (iOS) First open (Firebase)",
                                        ConversionActionCategoryEnum.ConversionActionCategory.DOWNLOAD
                                ),
                                265471890L
                        },
                        {
                                "Data WrongAction ID #1",
                                new GoogleExpenseConversions(
                                        472.,
                                        472.,
                                        "customers/9482315431/conversionActions",
                                        "ru.yandex.blue.market (iOS) First open (Firebase)",
                                        ConversionActionCategoryEnum.ConversionActionCategory.DOWNLOAD
                                ),
                                0L
                        },
                        {
                                "Data WrongAction ID #2",
                                new GoogleExpenseConversions(
                                        472.,
                                        472.,
                                        "",
                                        "ru.yandex.blue.market (iOS) First open (Firebase)",
                                        ConversionActionCategoryEnum.ConversionActionCategory.DOWNLOAD
                                ),
                                0L
                        }
                }
        );
    }

    @Test
    public void serializationTest() {
        // Serialize
        String result = "";
        try {
            result = ObjectMappersFactory
                    .getDefaultMapper()
                    .writeValueAsString(
                            conversions
                    );
        } catch (JsonProcessingException e) {
            throw new RuntimeException(e);
        }
        // DeSerialize
        GoogleExpenseConversions reverse = null;
        try {
            reverse = ObjectMappersFactory
                    .getDefaultMapper()
                    .readValue(
                            result,
                            new TypeReference<>() {}
                    );
        } catch (JsonProcessingException e) {
            throw new RuntimeException(e);
        }
        assertEquals(conversions, reverse);
    }

    @Test
    public void testFetchConversionActionId() {
        assertEquals(conversions.getConversionActionId(), conversionActionId);
    }
}
