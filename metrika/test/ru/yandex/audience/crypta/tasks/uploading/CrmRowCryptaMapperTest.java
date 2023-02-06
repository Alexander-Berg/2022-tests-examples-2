package ru.yandex.audience.crypta.tasks.uploading;

import java.util.List;

import org.junit.Test;

import ru.yandex.audience.uploading.crm.CrmRecord;
import ru.yandex.inside.yt.TabSeparatedKeyValue;

import static org.assertj.core.api.Assertions.assertThat;
import static ru.yandex.metrika.util.StringUtil.stringMd5;

public class CrmRowCryptaMapperTest {

    public static final String PHONE = "79851112233";
    public static final String EMAIL = "a@yandex.ru";

    @Test
    public void mapsNonHashedRecordsToTabSeparatedKeyValues() throws Exception {
        CrmRowCryptaMapper mapper = new CrmRowCryptaMapper(false);
        List<TabSeparatedKeyValue> mappedData = mapper.mappingFunction(
                new CrmRecord(null, EMAIL, PHONE));
        assertThat(mappedData).containsExactlyInAnyOrder(toKeyValueWithHashing(EMAIL),
                toKeyValueWithHashing(PHONE));
    }

    @Test
    public void mapsHashedRecordsToTabSeparatedKeyValues() throws Exception {
        CrmRowCryptaMapper mapper = new CrmRowCryptaMapper(true);
        List<TabSeparatedKeyValue> mappedData = mapper.mappingFunction(
                new CrmRecord(null, stringMd5(EMAIL), stringMd5(PHONE)));
        assertThat(mappedData).containsExactlyInAnyOrder(toKeyValueWithHashing(EMAIL),
                toKeyValueWithHashing(PHONE));
    }

    @Test
    public void mapsHNonHashedRecordsWithNullValuesToTabSeparatedKeyValues() throws Exception {
        CrmRowCryptaMapper mapper = new CrmRowCryptaMapper(false);
        List<TabSeparatedKeyValue> mappedData = mapper.mappingFunction(
                new CrmRecord(null, null, PHONE));
        assertThat(mappedData).containsExactlyInAnyOrder(toKeyValueWithHashing(PHONE));
    }

    private TabSeparatedKeyValue toKeyValueWithHashing(String s) {
        return TabSeparatedKeyValue.valueOf("id_value=" + stringMd5(s));
    }
}
