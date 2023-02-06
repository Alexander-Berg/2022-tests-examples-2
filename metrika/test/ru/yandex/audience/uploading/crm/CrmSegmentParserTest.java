package ru.yandex.audience.uploading.crm;

import java.util.Map;

import org.junit.Test;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static ru.yandex.audience.uploading.crm.SampleCrmData.HEADER;
import static ru.yandex.audience.uploading.crm.SampleCrmData.VALID_DATA;

public class CrmSegmentParserTest {

    public static final String ROW1 = VALID_DATA.get(1);

    @Test
    public void lineContainsRequiredFields() throws Exception {
        CrmSegmentParser parser = new CrmSegmentParser(HEADER);
        Map<String, String> data = parser.parse(ROW1, 1);
        assertThat(data.get(CsvField.EMAIL.toString())).isEqualTo("email@example.com");
        assertThat(data.get(CsvField.PHONE.toString())).isEqualTo("666");
    }

    @Test
    public void lineContainsFieldsInPreservedOrder() throws Exception {
        CrmSegmentParser parser = new CrmSegmentParser(HEADER);
        Map<String, String> data = parser.parse(ROW1, 1);
        assertThat(data.keySet()).containsExactly(parser.getHeader());
    }

    @Test
    public void parserPreservesHeaderItemsOrder() throws Exception {
        String[] expectedHeader = HEADER.split(",");
        CrmSegmentParser parser = new CrmSegmentParser(HEADER);
        assertThat(parser.getHeader()).containsExactly(expectedHeader);
    }

    @Test
    public void constructionSuccessesWhenPhoneHeaderIsNotPresent() throws Exception {
        new CrmSegmentParser("email,data");
    }

    @Test
    public void constructionSuccessesWhenEmailHeaderIsNotPresent() throws Exception {
        new CrmSegmentParser("phone");
    }

    @Test
    public void constructionFailsWhenBothEmailAndPhoneHeadersAreNotPresent() throws Exception {
        assertThatThrownBy(() -> new CrmSegmentParser("ext_id,data"))
                .isInstanceOf(HeaderValidationException.class);
    }

    @Test
    public void correctlyMapFieldPositionsTest() {
        var parser = new CrmSegmentParser("email,data");

        var mapping = parser.getMergeRowMapper("data,email").getMapping();

        assertThat(mapping).hasSize(2);
        assertThat(mapping).isEqualTo(Map.of(0, 1, 1, 0));
    }

    @Test
    public void leaveOnlyPresentFieldsTest() {
        var parser = new CrmSegmentParser("email,data");

        var mapping = parser.getMergeRowMapper("email,ext_id,data,some_field").getMapping();

        assertThat(mapping).hasSize(2);
        assertThat(mapping).isEqualTo(Map.of(0, 0, 1, 2));
    }

    @Test
    public void failsWhenBothEmailAndPhoneHeadersAreNotPresentAfterMergeTest() {
        var parser = new CrmSegmentParser("email,data");

        assertThatThrownBy(() -> parser.getMergeRowMapper("phone,data,ext_id"))
                .isInstanceOf(HeaderValidationException.class);
    }
}
