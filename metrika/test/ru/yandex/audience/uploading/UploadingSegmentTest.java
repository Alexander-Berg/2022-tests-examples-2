package ru.yandex.audience.uploading;

import org.junit.Test;

import ru.yandex.audience.ContentPattern;
import ru.yandex.audience.SegmentContentType;

import static org.assertj.core.api.Assertions.assertThat;
import static ru.yandex.audience.SegmentContentType.crm;
import static ru.yandex.audience.SegmentContentType.crypta_id;
import static ru.yandex.audience.SegmentContentType.email;
import static ru.yandex.audience.SegmentContentType.puid;

public class UploadingSegmentTest {

    @Test
    public void crmNonhashedSegmentPatternIsNull() {
        UploadingSegment uploadingSegment = getUploadingSegment(crm, false);
        assertThat(uploadingSegment.getPattern()).isNull();
    }

    @Test
    public void crmHashedSegmentPatternIsNull() {
        UploadingSegment uploadingSegment = getUploadingSegment(crm, true);
        assertThat(uploadingSegment.getPattern()).isNull();
    }

    @Test
    public void emailHashedSegmentPatternIsMd5() {
        UploadingSegment uploadingSegment = getUploadingSegment(email, true);
        assertThat(uploadingSegment.getPattern()).isEqualTo(ContentPattern.MD5);
    }

    @Test
    public void emailNonHashedSegmentPatternIsEmail() {
        UploadingSegment uploadingSegment = getUploadingSegment(email, false);
        assertThat(uploadingSegment.getPattern()).isEqualTo(ContentPattern.EMAIL);
    }

    @Test
    public void cryptaIdNonHashedSegmentPatternIsCryptaId() {
        UploadingSegment uploadingSegment = getUploadingSegment(crypta_id, false);
        assertThat(uploadingSegment.getPattern()).isEqualTo(ContentPattern.CRYPTA_ID);
    }

    @Test
    public void puidNonHashedSegmentPatternIsPuid() {
        UploadingSegment uploadingSegment = getUploadingSegment(puid, false);
        assertThat(uploadingSegment.getPattern()).isEqualTo(ContentPattern.PUID);
    }

    private UploadingSegment getUploadingSegment(SegmentContentType segmentContentType, boolean hashed) {
        UploadingSegment uploadingSegment = new UploadingSegment();
        uploadingSegment.setContentType(segmentContentType);
        uploadingSegment.setHashed(hashed);
        return uploadingSegment;
    }
}
