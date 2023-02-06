package ru.yandex.metrika.expenses.connectors.google;

import java.time.LocalDate;
import java.util.Map;

import org.junit.Test;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNull;

public class GoogleParamSubstitutorTest {

    String optionalString = "{ifmobile:{ifsearch:{keyword:cp={_customParameter1}}}}";
    String simpleParametersString = "{device}|{network}|{campaignid}|{adgroupid}|{creative}|{matchtype}";

    @Test
    public void withOptionalParamsTest() {
        GoogleExpensesYdbRow ydbRow = getMobileAndSearchAndEmptyKeywordRow();
        GoogleParamsSubstitutor substitutor = new GoogleParamsSubstitutor(ydbRow);
        assertEquals("cp=1", substitutor.replace(optionalString));
    }

    @Test
    public void withOptionalParamsAndDefinedKeywordTest() {
        GoogleExpensesYdbRow ydbRow = getMobileAndSearchAndKeywordRow();
        GoogleParamsSubstitutor substitutor = new GoogleParamsSubstitutor(ydbRow);
        assertEquals("searchkeyword", substitutor.replace(optionalString));
    }

    @Test
    public void withKeywordTest() {
        GoogleExpensesYdbRow ydbRow = getMobileAndSearchAndKeywordRow();
        GoogleParamsSubstitutor substitutor = new GoogleParamsSubstitutor(ydbRow);
        assertEquals("searchkeyword", substitutor.replace("{keyword}"));
    }

    @Test
    public void withOptionalParamsAndUndefinedNetworkTest() {
        GoogleExpensesYdbRow ydbRow = getMobileEmptyKeywordRow();
        GoogleParamsSubstitutor substitutor = new GoogleParamsSubstitutor(ydbRow);
        assertEquals("{ifsearch:cp=1}", substitutor.replace(optionalString));
    }

    @Test
    public void withSimpleParams() {
        GoogleExpensesYdbRow ydbRow = getMobileAndSearchAndEmptyKeywordRow();
        GoogleParamsSubstitutor substitutor = new GoogleParamsSubstitutor(ydbRow);
        assertEquals("m|g|2|3|4|e", substitutor.replace(simpleParametersString));
    }

    @Test
    public void withNullString() {
        GoogleExpensesYdbRow ydbRow = getMobileAndSearchAndEmptyKeywordRow();
        GoogleParamsSubstitutor substitutor = new GoogleParamsSubstitutor(ydbRow);
        assertNull(substitutor.replace(null));
    }

    @Test
    public void withCustomParameterLevels() {
        GoogleExpensesYdbRow ydbRow = getMobileAndSearchAndEmptyKeywordRow();
        GoogleParamsSubstitutor substitutor = new GoogleParamsSubstitutor(ydbRow);
        assertEquals("1", substitutor.replace("{_customParameter1}"));
    }

    @Test
    public void withNotExistedParameter() {
        GoogleExpensesYdbRow ydbRow = getMobileAndSearchAndEmptyKeywordRow();
        GoogleParamsSubstitutor substitutor = new GoogleParamsSubstitutor(ydbRow);
        String str = "{_notexisted:blablabla}{_notexisted2}";
        assertEquals(str, substitutor.replace(str));
    }

    private GoogleExpensesYdbRow getMobileAndSearchAndEmptyKeywordRow() {
        return new GoogleExpensesYdbRow(
                1L,
                LocalDate.now(),
                2L,
                3L,
                4L,
                "",
                "SEARCH",
                "",
                "",
                "MOBILE",
                "",
                "",
                "EXACT",
                "",
                "",
                "",
                "",
                "",
                "",
                Map.of("customParameter1", "3"),
                "",
                "",
                Map.of("customParameter1", "1"),
                "",
                "",
                "",
                Map.of("customParameter1", "2"),
                "",
                "",
                "",
                0L,
                0L,
                0L,
                null,
                false
        );
    }

    private GoogleExpensesYdbRow getMobileAndSearchAndKeywordRow() {
        return new GoogleExpensesYdbRow(
                1L,
                LocalDate.now(),
                2L,
                3L,
                4L,
                "",
                "SEARCH",
                "",
                "",
                "MOBILE",
                "",
                "",
                "",
                "searchkeyword",
                "",
                "",
                "",
                "",
                "",
                Map.of(),
                "",
                "",
                Map.of("customParameter1", "1"),
                "",
                "",
                "",
                Map.of(),
                "",
                "",
                "",
                0L,
                0L,
                0L,
                null,
                false
        );
    }

    private GoogleExpensesYdbRow getMobileEmptyKeywordRow() {
        return new GoogleExpensesYdbRow(
                1L,
                LocalDate.now(),
                2L,
                3L,
                4L,
                "",
                "MIXED",
                "",
                "",
                "MOBILE",
                "String slot",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                Map.of(),
                "",
                "",
                Map.of("customParameter1", "1"),
                "",
                "",
                "",
                Map.of(),
                "",
                "",
                "",
                0L,
                0L,
                0L,
                null,
                false
        );
    }
}
