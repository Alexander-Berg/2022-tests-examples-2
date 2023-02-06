package ru.yandex.metrika.audience.pubapi.converter;

import org.junit.Test;

import ru.yandex.audience.SegmentContentType;
import ru.yandex.audience.SegmentType;
import ru.yandex.audience.uploading.UploadingSegment;
import ru.yandex.metrika.audience.pubapi.ClientIdSegmentRequestUploading;

import static org.assertj.core.api.Assertions.assertThat;

public class ClientIdSegmentRequestUploadingConverterTest {

    public static final String NAME = "somename";
    public static final int COUNTER_ID = 12376534;

    @Test
    public void correctlyConvertsClientIdSegmentRequestUploadingToUploadingSegment() {
        ClientIdSegmentRequestUploadingConverter converter = new ClientIdSegmentRequestUploadingConverter();
        assertThat(converter.convert(clientIdSegmentRequestUploading()))
                .isEqualToComparingFieldByField(uploadingSegment());
    }

    private UploadingSegment uploadingSegment() {
        UploadingSegment segment = new UploadingSegment();
        segment.setName(NAME);
        segment.setCounterId(COUNTER_ID);
        segment.setContentType(SegmentContentType.client_id);
        segment.setType(SegmentType.uploading);
        return segment;
    }

    private ClientIdSegmentRequestUploading clientIdSegmentRequestUploading() {
        ClientIdSegmentRequestUploading clientIdSegmentRequestUploading = new ClientIdSegmentRequestUploading();
        clientIdSegmentRequestUploading.setName(NAME);
        clientIdSegmentRequestUploading.setCounterId(COUNTER_ID);
        return clientIdSegmentRequestUploading;
    }

}
