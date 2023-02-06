package ru.yandex.metrika.restream.ydb;

import java.time.Duration;
import java.time.Instant;
import java.util.List;
import java.util.stream.IntStream;

import org.hamcrest.Matchers;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringRunner;

import ru.yandex.metrika.config.EnvironmentHelper;
import ru.yandex.metrika.dbclients.YdbSetupUtil;
import ru.yandex.metrika.dbclients.config.YdbConfig;
import ru.yandex.metrika.dbclients.ydb.YdbTemplate;
import ru.yandex.metrika.restream.ProfilesTestUtil;
import ru.yandex.metrika.restream.dto.UserSegmentProfile;
import ru.yandex.metrika.util.collections.F;

import static java.util.stream.Collectors.toMap;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.hasEntry;
import static org.hamcrest.Matchers.hasSize;
import static org.junit.Assert.assertThat;
import static ru.yandex.metrika.dbclients.ydb.async.QueryExecutionContext.read;
import static ru.yandex.metrika.dbclients.ydb.async.QueryExecutionContext.write;
import static ru.yandex.metrika.restream.ProfilesTestUtil.profile;

@RunWith(SpringRunner.class)
@ContextConfiguration
public class UserSegmentsProfilesDaoYdbTest {

    @Autowired
    public UserSegmentsProfilesDaoYdb dao;

    @Before
    public void setUp() {
        YdbSetupUtil.truncateTablesIfExists(EnvironmentHelper.ydbDatabase + "/" + UserSegmentsProfilesDaoYdb.TABLE_NAME);
    }

    @Test
    public void simpleSaveAndGet() {
        var key = new UserSegmentProfile.Key(1, 2);
        var profile = profile(true, ProfilesTestUtil.visit(1, 1, 10, 1, 1));
        var usp = new UserSegmentProfile(key, profile);
        dao.saveProfiles(List.of(usp), write()).join();
        var uspMap = dao.getProfiles(List.of(key), read()).join();
        assertThat(uspMap.entrySet(), hasSize(1));
        assertThat(uspMap, hasEntry(key, usp));
    }

    @Test
    public void saveNewRevisionNoConflict() {
        var key = new UserSegmentProfile.Key(1, 2);
        var profile = profile(true, ProfilesTestUtil.visit(1, 1, 10, 1, 1));
        var usp = new UserSegmentProfile(key, profile);
        dao.saveProfiles(List.of(usp), write()).join();

        var updated = usp.updateProfile(profile(true, ProfilesTestUtil.visit(1, 2, 20, 1, 1)));
        assertThat(updated.getRevision(), greaterThan(usp.getRevision()));
        dao.saveNewRevisionsIfNoConflict(List.of(updated)).join();

        var uspMap = dao.getProfiles(List.of(key), read()).join();
        assertThat(uspMap.entrySet(), hasSize(1));
        assertThat(uspMap, hasEntry(key, updated));
    }

    @Test
    public void dontSaveNewRevisionDueToConflict() {
        var key = new UserSegmentProfile.Key(1, 2);
        var profile = profile(true, ProfilesTestUtil.visit(1, 1, 10, 1, 1));
        var usp = new UserSegmentProfile(key, profile);
        dao.saveProfiles(List.of(usp), write()).join();

        var updated = usp.updateProfile(profile(true, ProfilesTestUtil.visit(1, 2, 20, 1, 1)));
        assertThat(updated.getRevision(), greaterThan(usp.getRevision()));
        // conflicting update
        dao.saveProfiles(List.of(updated), write()).join();

        var otherUpdate = usp.updateProfile(profile(true, ProfilesTestUtil.visit(1, 3, 30, 1, 1)));
        assertThat(otherUpdate.getRevision(), greaterThan(usp.getRevision()));
        // should not save anything because new revision was saved before via direct saveProfiles
        dao.saveNewRevisionsIfNoConflict(List.of(otherUpdate)).join();

        // copy and saveNewRevisionsIfNoConflict should have no affect on state
        var uspMap = dao.getProfiles(List.of(key), read()).join();
        assertThat(uspMap.entrySet(), hasSize(1));
        assertThat(uspMap, hasEntry(key, updated));
    }

    @Test
    public void deleteOldRevisionNoConflict() {
        var key = new UserSegmentProfile.Key(1, 2);
        var deadline = Instant.now().minus(Duration.ofDays(5));
        var utcStartTime = deadline.minus(Duration.ofDays(10)).getEpochSecond();
        var profile = profile(true, ProfilesTestUtil.visit(1, 1, (int) utcStartTime, 1, 1));
        var usp = new UserSegmentProfile(key, profile);
        dao.saveProfiles(List.of(usp), write()).join();

        dao.deleteIfNoConflict(List.of(usp)).join();

        var uspMap = dao.getProfiles(List.of(key), read()).join();
        assertThat(uspMap.entrySet(), Matchers.empty());
    }

    @Test
    public void dontDeleteNewRevisionNoConflict() {
        var key = new UserSegmentProfile.Key(1, 2);
        var deadline = Instant.now().minus(Duration.ofDays(5));
        var utcStartTime = deadline.minus(Duration.ofDays(10)).getEpochSecond();
        var profile = profile(true, ProfilesTestUtil.visit(1, 1, (int) utcStartTime, 1, 1));
        var usp = new UserSegmentProfile(key, profile);
        dao.saveProfiles(List.of(usp), write()).join();

        var updated = usp.updateProfile(profile(false));
        dao.deleteIfNoConflict(List.of(updated)).join();

        var uspMap = dao.getProfiles(List.of(key), read()).join();
        assertThat(uspMap.entrySet(), hasSize(1));
        assertThat(uspMap, hasEntry(key, usp));
    }


    @Test
    public void dontDeleteOldRevisionOnConflict() {
        var key = new UserSegmentProfile.Key(1, 2);
        var deadline = Instant.now().minus(Duration.ofDays(5));
        var utcStartTime = deadline.plus(Duration.ofDays(2)).getEpochSecond();
        var profile = profile(true, ProfilesTestUtil.visit(1, 1, (int) utcStartTime, 1, 1));
        var usp = new UserSegmentProfile(key, profile);
        dao.saveProfiles(List.of(usp), write()).join();

        var updated = usp.updateProfile(profile(false));
        dao.saveProfiles(List.of(updated), write()).join();

        dao.deleteIfNoConflict(List.of(usp)).join();

        var uspMap = dao.getProfiles(List.of(key), read()).join();
        assertThat(uspMap.entrySet(), hasSize(1));
        assertThat(uspMap, hasEntry(key, updated));
    }

    @Test
    public void saveBatchAndGetMoreThenThousandProfiles() {
        var profile = profile(true, ProfilesTestUtil.visit(1, 1, 10, 1, 1));
        var batchMap = IntStream.rangeClosed(1, 2000)
                .mapToObj(userId -> new UserSegmentProfile.Key(userId, 2))
                .collect(toMap(F.id(), key -> new UserSegmentProfile(key, profile)));

        dao.saveProfiles(batchMap.values(), write()).join();
        var uspMap = dao.getProfiles(batchMap.keySet(), read()).join();
        Assert.assertEquals(batchMap, uspMap);
    }

    @Configuration
    @Import(YdbConfig.class)
    public static class Config {
        @Bean
        public UserSegmentsProfilesDaoYdb userSegmentsProfilesDaoYdb(YdbTemplate template) {
            return new UserSegmentsProfilesDaoYdb(template);
        }
    }
}
