package ru.yandex.audience.uploading;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import org.junit.Test;
import org.mockito.ArgumentCaptor;

import ru.yandex.audience.SegmentChunksService;
import ru.yandex.audience.SegmentExternalService;
import ru.yandex.audience.SegmentLimit;
import ru.yandex.audience.SegmentLimitConf;
import ru.yandex.audience.SegmentLimitConfDao;
import ru.yandex.audience.SegmentPermissionService;
import ru.yandex.audience.SegmentType;
import ru.yandex.audience.dao.SegmentDao;
import ru.yandex.audience.geo.GeoPoint;
import ru.yandex.audience.geo.GeoPointsService;
import ru.yandex.audience.rbac.SegmentsRbac;
import ru.yandex.metrika.api.error.LocalizedApiExceptionFactory;
import ru.yandex.metrika.audience.quota.TargetedSegmentsQuotaService;
import ru.yandex.metrika.auth.MetrikaUserDetails;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.util.chunk.clickhouse.haze.ReliableChunkStorage;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.Assert.assertEquals;
import static org.mockito.Matchers.any;
import static org.mockito.Mockito.anyInt;
import static org.mockito.Mockito.anyObject;
import static org.mockito.Mockito.anyString;
import static org.mockito.Mockito.atLeastOnce;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static ru.yandex.audience.SegmentContentType.client_id;
import static ru.yandex.audience.SegmentContentType.crm;
import static ru.yandex.audience.SegmentStatus.confirmed;
import static ru.yandex.audience.SegmentStatus.uploaded;

public class SegmentServiceTest {

    private class SegmentLimitConfDaoMock extends SegmentLimitConfDao {
        public SegmentLimitConfDaoMock() {
            super(null);
        }

        @Override
        public Integer getMinSegmentSizeByUsername(long uid, SegmentType segmentType) {
            return 100;
        }
    }

    public static final String ORIGIN_REPOSITORY_CHUNK_ID = "123";

    private byte[] bytesForClickhouse = new byte[100];
    private ChunkUploader chunkUploader = new ChunkUploader(mock(ReliableChunkStorage.class), false);
    private ChunkUploader csvChunkUploader = new ChunkUploader(mock(ReliableChunkStorage.class), true);
    private GeoPointsService geoPointsService = new GeoPointsService(null, null);
    private SegmentLimitConfDao confDao = new SegmentLimitConfDaoMock();
    private SegmentLimit segmentLimit = new SegmentLimit(100, 100000000L, confDao, new SegmentLimitConf());

/*    @Test
    public void testParseSegmentFileForClickhouse3() {
        byte[] bytes = new byte[]{44,10};
        SegmentService.SegmentFileParseState context = new SegmentService().parseSegmentFileForClickhouse(bytes);
        assertEquals(0, context.itemQuantity);
        assertEquals(0, context.bytesForClickhouseQuantity);
        assertEquals(0, context.bytesForClickhouse.length);
    }
*/


    @Test
    public void testMakeUniqueGeoPoints() {
        List<GeoPoint> points = Arrays.asList(new GeoPoint(1.1, 1.2), new GeoPoint(1.1, 1.2), new GeoPoint(1, 2), new GeoPoint(1.1, 1.2));
        ArrayList<GeoPoint> points_ = new ArrayList<>();
        points_.addAll(geoPointsService.makeUniqueGeoPoints(points));
        assertEquals(2, points_.size());
        assertEquals(new GeoPoint(1.1, 1.2), points_.get(0));
        assertEquals(new GeoPoint(1, 2), points_.get(1));
    }

    @Test
    public void confirmPersistsCorrectUploadingSegmentWhenNonInterimUploading() {
        UploadingSegment actualUploadingSegment = getUploadingSegmentPersistedByConfirmMethod(
                createUploadingPhoneSegment());

        assertThat(actualUploadingSegment.getInternalStatus()).isEqualTo(confirmed);
        assertThat(actualUploadingSegment.getOriginRepositoryChunkId()).isEqualTo(ORIGIN_REPOSITORY_CHUNK_ID);
    }

    @Test
    public void confirmMethodPersistsCorrectUploadingSegmentWhenInterimUploading() {
        UploadingSegment actualUploadingSegment = getUploadingSegmentPersistedByConfirmMethod(
                createUploadingClientIdSegment());

        assertThat(actualUploadingSegment.getInternalStatus()).isEqualTo(confirmed);
        assertThat(actualUploadingSegment.getInterimRepositoryChunkId()).isEqualTo(ORIGIN_REPOSITORY_CHUNK_ID);
        assertThat(actualUploadingSegment.getOriginRepositoryChunkId()).isEmpty();
    }

    private UploadingSegment getUploadingSegmentPersistedByConfirmMethod(UploadingSegment inboundUploadingSegment) {
        SegmentDao segmentDao = mock(SegmentDao.class);
        SegmentUploadingService segmentService = createSegmentService(segmentDao);

        ArgumentCaptor<UploadingSegment> captor = ArgumentCaptor.forClass(UploadingSegment.class);
        segmentService.confirm(inboundUploadingSegment, mock(MetrikaUserDetails.class));

        verify(segmentDao, atLeastOnce()).update(captor.capture());

        return captor.getValue();
    }

    private SegmentUploadingService createSegmentService(SegmentDao segmentDao) {
        UploadingSegment segment = new UploadingSegment();
        segment.setInternalStatus(uploaded);
        segment.setOriginRepositoryChunkId(ORIGIN_REPOSITORY_CHUNK_ID);
        segment.setItemQuantity(1);

        SegmentExternalService segmentExternalService = mock(SegmentExternalService.class);
        SegmentChunksService segmentChunksService = getSegmentChunksService();
        SegmentUploadingService segmentService = new SegmentUploadingService(
                mock(MySqlJdbcTemplate.class),
                mock(LocalizedApiExceptionFactory.class),
                mock(SegmentsRbac.class),
                mock(ReliableChunkStorage.class),
                segmentDao,
                segmentExternalService,
                segmentChunksService,
                mock(SegmentPermissionService.class),
                mock(TargetedSegmentsQuotaService.class),
                segmentLimit
        );
        doReturn(segment).when(segmentExternalService).findById(anyInt(), any(MetrikaUserDetails.class));
        return segmentService;
    }

    private SegmentChunksService getSegmentChunksService() {
        SegmentChunksService mock = mock(SegmentChunksService.class);
        when(mock.getValidUniqueQuantity(anyObject(), anyString())).thenReturn(1000L);
        return mock;
    }

    private UploadingSegment createUploadingClientIdSegment() {
        UploadingSegment uploadingSegment = new UploadingSegment();
        uploadingSegment.setContentType(client_id);
        uploadingSegment.setName("somename");
        uploadingSegment.setCounterId(101024);
        return uploadingSegment;
    }

    private UploadingSegment createUploadingPhoneSegment() {
        UploadingSegment uploadingSegment = new UploadingSegment();
        uploadingSegment.setContentType(crm);
        uploadingSegment.setName("somename");
        return uploadingSegment;
    }

}
