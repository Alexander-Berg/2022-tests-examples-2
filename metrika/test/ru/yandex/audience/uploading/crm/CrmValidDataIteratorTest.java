package ru.yandex.audience.uploading.crm;

import java.util.Iterator;
import java.util.List;

import com.google.common.collect.ImmutableList;
import org.junit.Test;

import ru.yandex.audience.SegmentStorageRow;
import ru.yandex.metrika.util.collections.CloseableIterators;
import ru.yandex.metrika.util.collections.F;

import static org.assertj.core.api.Assertions.assertThat;
import static ru.yandex.audience.uploading.crm.SampleCrmData.INVALID_DATA;
import static ru.yandex.audience.uploading.crm.SampleCrmData.VALID_DATA;
import static ru.yandex.audience.uploading.crm.SampleCrmData.VALID_HASHED_DATA;
import static ru.yandex.audience.uploading.crm.SampleCrmData.VALID_HASHED_DATA_BOM;

public class CrmValidDataIteratorTest {

    private static final List<String> MIXED_DATA = ImmutableList.of(
            "phone",
            "bad-phone",
            "+7(495)739-70-00",
            "fff"
    );

    @Test
    public void returnsCrmDataWhenValidationSuccessful() {
        CrmValidDataIterator it = buildNonhashedCrmValidDataIterator(VALID_DATA);
        assertThat(it.count()).isEqualTo(2);
    }

    @Test
    public void returnsCrmHashedDataWhenValidationSuccessful() {
        CrmValidDataIterator it = buildHashedCrmValidDataIterator(VALID_HASHED_DATA);
        assertThat(it.count()).isEqualTo(2);
    }

    @Test
    public void returnsEmptyWhenInvalidData() {
        CrmValidDataIterator it = buildNonhashedCrmValidDataIterator(INVALID_DATA);
        assertThat(it.count()).isZero();
    }

    @Test
    public void returnsCorrectedCrmData() {
        CrmValidDataIterator it = buildNonhashedCrmValidDataIterator(MIXED_DATA);
        CrmRecord record = it.next();
        assertThat(record.validPhone()).isEqualTo("74957397000");
        assertThat(it.hasNext()).isFalse();
    }

    @Test
    public void returnsCrmHashedDataWhenValidationSuccessfulWithBom() {
        CrmValidDataIterator it = buildHashedCrmValidDataIterator(VALID_HASHED_DATA_BOM);
        int count = 0;
        while(it.hasNext()) {
            CrmRecord record = it.next();
            assertThat(record.validPhone()).isNotNull();
            assertThat(record.validEmail()).isNotNull();
            count++;
        }
        assertThat(count).isEqualTo(2);
    }

    private CrmValidDataIterator buildNonhashedCrmValidDataIterator(List<String> data) {
        return crmValidDataIterator(data, false);
    }

    private CrmValidDataIterator buildHashedCrmValidDataIterator(List<String> data) {
        return crmValidDataIterator(data, true);
    }

    private CrmValidDataIterator crmValidDataIterator(List<String> data, boolean hashed) {
        Iterator<SegmentStorageRow> mappedFromString = F.map(data.iterator(), SegmentStorageRow::new);
        return new CrmValidDataIterator(
                CloseableIterators.fromNonCloseableIterator(mappedFromString),
                hashed);
    }
}
