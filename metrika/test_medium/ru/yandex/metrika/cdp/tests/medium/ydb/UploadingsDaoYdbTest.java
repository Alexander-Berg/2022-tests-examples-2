package ru.yandex.metrika.cdp.tests.medium.ydb;

import java.time.Instant;
import java.util.UUID;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringRunner;

import ru.yandex.metrika.cdp.dto.core.UpdateType;
import ru.yandex.metrika.cdp.dto.schema.EntityNamespace;
import ru.yandex.metrika.cdp.dto.uploading.ApiValidationStatus;
import ru.yandex.metrika.cdp.dto.uploading.UploadingFormat;
import ru.yandex.metrika.cdp.dto.uploading.UploadingMeta;
import ru.yandex.metrika.cdp.dto.uploading.UploadingSource;
import ru.yandex.metrika.cdp.dto.uploading.UploadingStatus;
import ru.yandex.metrika.cdp.ydb.UploadingsDaoYdb;
import ru.yandex.metrika.config.EnvironmentHelper;
import ru.yandex.metrika.dbclients.YdbSetupUtil;
import ru.yandex.metrika.dbclients.config.YdbConfig;
import ru.yandex.metrika.dbclients.ydb.YdbTemplate;

import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.hasItems;
import static org.hamcrest.Matchers.not;
import static org.junit.Assert.assertThat;
import static ru.yandex.metrika.cdp.ydb.UploadingsDaoYdb.UPLOADINGS_TABLE;

@RunWith(SpringRunner.class)
@ContextConfiguration
public class UploadingsDaoYdbTest {

    private static final String SYSTEM_DATA_FOLDER = "system_data";
    private static final String UPLOADINGS_TABLE_PREFIX = EnvironmentHelper.ydbDatabase + "/" + SYSTEM_DATA_FOLDER;
    private static final String UPLOADINGS_TABLE_PATH = UPLOADINGS_TABLE_PREFIX + "/" + UPLOADINGS_TABLE;
    private static final int COUNTER_ID = 10;

    @BeforeClass
    public static void beforeClass() {
        YdbSetupUtil.setupYdbFolders(SYSTEM_DATA_FOLDER);
    }

    @Autowired
    private UploadingsDaoYdb uploadingsDaoYdb;

    @Before
    public void setUp() {
        YdbSetupUtil.truncateTablesIfExists(UPLOADINGS_TABLE_PATH);
    }

    @Test
    public void saveUploading() {
        var meta = createMeta(Instant.now());
        uploadingsDaoYdb.saveUploading(meta);

        var lastUploadings = uploadingsDaoYdb.getLastUploadings(COUNTER_ID, 100, null);
        assertThat(lastUploadings, not(empty()));
        assertThat(lastUploadings, hasItem(meta));
    }

    @Test
    public void getLastUploadings() {
        var meta1 = createMeta(Instant.now());
        var meta2 = createMeta(Instant.now());
        var meta3 = createMeta(Instant.now());
        uploadingsDaoYdb.saveUploading(meta1);
        uploadingsDaoYdb.saveUploading(meta2);
        uploadingsDaoYdb.saveUploading(meta3);

        var lastUploadings = uploadingsDaoYdb.getLastUploadings(COUNTER_ID, 100, null);
        assertThat(lastUploadings, not(empty()));
        assertThat(lastUploadings, hasItems(meta1, meta2, meta3));
    }

    @Test
    public void getLastUploadingsWithLimit() {
        var meta1 = createMeta(Instant.now());
        var meta2 = createMeta(Instant.now().minusSeconds(1000));
        var meta3 = createMeta(Instant.now().minusSeconds(2000));
        uploadingsDaoYdb.saveUploading(meta1);
        uploadingsDaoYdb.saveUploading(meta2);
        uploadingsDaoYdb.saveUploading(meta3);

        var lastUploadings = uploadingsDaoYdb.getLastUploadings(COUNTER_ID, 2, null);
        assertThat(lastUploadings, not(empty()));
        assertThat(lastUploadings, hasItems(meta1, meta2));
        assertThat(lastUploadings, not(hasItem(meta3)));
    }

    @Test
    public void getLastUploadingsWithBefore() {
        var meta1 = createMeta(Instant.now());
        var meta2 = createMeta(Instant.now().minusSeconds(1000));
        var meta3 = createMeta(Instant.now().minusSeconds(2000));
        uploadingsDaoYdb.saveUploading(meta1);
        uploadingsDaoYdb.saveUploading(meta2);
        uploadingsDaoYdb.saveUploading(meta3);

        var lastUploadings = uploadingsDaoYdb.getLastUploadings(COUNTER_ID, 2, meta1.getUploadingDatetime());
        assertThat(lastUploadings, not(empty()));
        assertThat(lastUploadings, hasItems(meta2, meta3));
        assertThat(lastUploadings, not(hasItem(meta1)));
    }

    @Test
    public void getLastUploadingsWithDifferentParams() {
        var meta1 = createMeta(Instant.now());
        meta1.setUploadingFormat(UploadingFormat.CSV);
        var meta2 = createMeta(Instant.now().minusSeconds(1000));
        meta2.setApiValidationStatus(ApiValidationStatus.FAILED);
        meta2.setElementsCount(null);
        var meta3 = createMeta(Instant.now().minusSeconds(2000));
        meta3.setUploadingSource(UploadingSource.CRM);

        uploadingsDaoYdb.saveUploading(meta1);
        uploadingsDaoYdb.saveUploading(meta2);
        uploadingsDaoYdb.saveUploading(meta3);

        var lastUploadings = uploadingsDaoYdb.getLastUploadings(COUNTER_ID, 100, null);
        assertThat(lastUploadings, not(empty()));
        assertThat(lastUploadings, hasItems(meta1, meta2, meta3));
    }

    @Test(expected = IllegalArgumentException.class)
    public void testNegativeLimit() {
        uploadingsDaoYdb.getLastUploadings(COUNTER_ID, -1, null);
    }

    @Test(expected = IllegalArgumentException.class)
    public void testTooBigLimit() {
        uploadingsDaoYdb.getLastUploadings(COUNTER_ID, 1001, null);
    }

    private static UploadingMeta createMeta(Instant instant) {
        return new UploadingMeta(
                COUNTER_ID, UUID.randomUUID(), instant, EntityNamespace.CONTACT, 1,
                ApiValidationStatus.PASSED, UploadingFormat.JSON, UploadingSource.API, UploadingStatus.COMPLETED, UpdateType.SAVE
        );
    }

    @Configuration
    @Import(YdbConfig.class)
    static class Config {

        @Bean
        public UploadingsDaoYdb uploadingsDaoYdb(YdbTemplate ydbTemplate) {
            return new UploadingsDaoYdb(ydbTemplate, UPLOADINGS_TABLE_PREFIX);
        }

    }
}
