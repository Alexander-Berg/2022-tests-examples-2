package ru.yandex.audience;

import java.util.Arrays;
import java.util.Collection;
import java.util.Map;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.audience.uploading.UploadingSegment;

import static com.google.common.collect.ImmutableMap.of;
import static org.assertj.core.api.Assertions.assertThat;

@RunWith(Parameterized.class)
public class UploadingSegmentCryptaAttributeTest {

    @Parameterized.Parameter
    public String contentType;

    @Parameterized.Parameter(1)
    public UploadingSegment segment;

    @Parameterized.Parameter(2)
    public Map<CryptaAttribute, String> cryptaAttributes;

    @Parameterized.Parameters(name = "type: {0}")
    public static Collection<Object[]> createParameters() {
        return Arrays.asList(
                new Object[][]{
                        {"email",
                                segment(SegmentMatchingType.exact,
                                        SegmentContentType.email),
                                of(CryptaAttribute.crypta_matching_type, SegmentMatchingType.exact.toString(),
                                        CryptaAttribute.crypta_id_type, SegmentContentType.email.toString())},
                        {"idfa_gaid",
                                segment(SegmentMatchingType.exact,
                                        SegmentContentType.idfa_gaid,
                                        SegmentDeviceMatchingType.crossdevice),
                                of(CryptaAttribute.crypta_matching_type, SegmentMatchingType.exact.toString(),
                                        CryptaAttribute.crypta_id_type, SegmentContentType.idfa_gaid.toString(),
                                        CryptaAttribute.crypta_dev_matching_type,
                                        SegmentDeviceMatchingType.crossdevice.toString())},
                        {"client_id",
                                segment(SegmentMatchingType.exact,
                                        SegmentContentType.client_id),
                                of(CryptaAttribute.crypta_matching_type, SegmentMatchingType.exact.toString(),
                                        CryptaAttribute.crypta_id_type, SegmentContentType.yuid.toString())},
                        {"crypta_id",
                                segment(SegmentMatchingType.exact,
                                        SegmentContentType.crypta_id),
                                of(CryptaAttribute.crypta_matching_type, SegmentMatchingType.exact.toString(),
                                        CryptaAttribute.crypta_id_type, SegmentContentType.crypta_id.toString())
                        },
                        {"puid",
                                segment(SegmentMatchingType.exact,
                                        SegmentContentType.puid),
                                of(CryptaAttribute.crypta_matching_type, SegmentMatchingType.exact.toString(),
                                        CryptaAttribute.crypta_id_type, SegmentContentType.puid.toString())
                        }
                }
        );
    }

    @Test
    public void cryptaAttributesForUploadingSegment() throws Exception {
        assertThat(segment.getCryptaAttributes()).containsAllEntriesOf(cryptaAttributes);
    }

    private static UploadingSegment segment(SegmentMatchingType matchingType, SegmentContentType contentType,
                                            SegmentDeviceMatchingType deviceMatchingType) {
        UploadingSegment segment = segment(matchingType, contentType);
        segment.setDeviceMatchingType(deviceMatchingType);
        return segment;
    }

    private static UploadingSegment segment(SegmentMatchingType matchingType, SegmentContentType contentType) {
        UploadingSegment seg = new UploadingSegment();
        seg.setMatchingType(matchingType);
        seg.setContentType(contentType);
        return seg;
    }
}
