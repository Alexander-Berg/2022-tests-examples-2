package ru.yandex.metrika.api.management.tests.medium.client;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;

import com.yandex.ydb.core.Status;
import org.junit.After;
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

import ru.yandex.metrika.api.management.client.recommendations.FrontRecommendation;
import ru.yandex.metrika.api.management.client.recommendations.Recommendation;
import ru.yandex.metrika.api.management.client.recommendations.RecommendationInterfaceSection;
import ru.yandex.metrika.api.management.client.recommendations.RecommendationMetaDao;
import ru.yandex.metrika.api.management.client.recommendations.RecommendationService;
import ru.yandex.metrika.api.management.client.recommendations.RecommendationYdbDao;
import ru.yandex.metrika.api.management.config.CountersRbacConfig;
import ru.yandex.metrika.api.management.config.LocaleDictionariesConfig;
import ru.yandex.metrika.api.management.config.RecommendationDaoConfig;
import ru.yandex.metrika.api.management.config.RecommendationYdbDaoConfig;
import ru.yandex.metrika.api.management.tests.util.YdbTestUtils;
import ru.yandex.metrika.auth.MetrikaUserDetails;
import ru.yandex.metrika.dbclients.ydb.YdbTemplate;
import ru.yandex.metrika.rbac.metrika.CountersRbac;
import ru.yandex.metrika.util.collections.F;
import ru.yandex.metrika.util.locale.LocaleDictionaries;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;
import static ru.yandex.metrika.api.management.client.recommendations.UserRecommendationStatus.CLOSED;
import static ru.yandex.metrika.api.management.client.recommendations.UserRecommendationStatus.NEW;
import static ru.yandex.metrika.api.management.client.recommendations.UserRecommendationStatus.READ;

@RunWith(SpringRunner.class)
@ContextConfiguration
public class RecommendationServiceTest {

    @Autowired
    public RecommendationService recommendationService;

    @Autowired
    public YdbTemplate ydbTemplate;

    @Autowired
    public RecommendationYdbDao recommendationYdbDao;

    @Autowired
    public CountersRbac countersRbacMock;

    public MetrikaUserDetails owner;
    public MetrikaUserDetails editor;
    public MetrikaUserDetails reader;

    @Before
    public void setUp() {
        YdbTestUtils.createSubscriptionTables();

        owner = MetrikaUserDetails.createMud(1);
        editor = MetrikaUserDetails.createMud(2);
        reader = MetrikaUserDetails.createMud(3);

        when(countersRbacMock.view(owner, 1)).thenReturn(true);
        when(countersRbacMock.view(editor, 1)).thenReturn(true);
        when(countersRbacMock.view(reader, 1)).thenReturn(true);
        when(countersRbacMock.save(owner, 1)).thenReturn(true);
        when(countersRbacMock.save(editor, 1)).thenReturn(true);
        when(countersRbacMock.save(reader, 1)).thenReturn(false);
        when(countersRbacMock.isOwner(owner.getUid(), 1)).thenReturn(true);
        when(countersRbacMock.isOwner(editor.getUid(), 1)).thenReturn(false);
        when(countersRbacMock.isOwner(reader.getUid(), 1)).thenReturn(false);

        recommendationYdbDao.insertRecommendations(List.of(new Recommendation(1, 1, 1, Instant.now(), "{\"goal_name\":\"1 1 1 CLOSED\"}")));
        recommendationYdbDao.insertRecommendations(List.of(new Recommendation(1, 2, 2, Instant.now(), "{\"goal_name\":\"1 1 2 READ\"}")));
        recommendationYdbDao.insertRecommendations(List.of(new Recommendation(1, 3, 3, Instant.now(), "{\"goal_name\":\"1 1 3 NEW\"}")));
        recommendationYdbDao.changeStatus(1, 1, 1, 1, CLOSED);
        recommendationYdbDao.changeStatus(1, 1, 2, 2, READ);
        recommendationYdbDao.changeStatus(1, 1, 3, 3, NEW);
    }

    @Test
    public void showForTest() {
        // доступность определяется настройками в посгре, а в тестах в 00_postgres_misc_schema_subscriptions.sql
        Assert.assertEquals("Owner is allowed to get recommendations", 3, recommendationService.getUserRecommendations(owner, 1).size());
        Assert.assertEquals("Editor is allowed to get recommendations", 3, recommendationService.getUserRecommendations(editor, 1).size());
        Assert.assertEquals("Reader is not allowed to get recommendations", 0, recommendationService.getUserRecommendations(reader, 1).size());
    }

    @Test
    public void recommendationStatusTest() {
        List<FrontRecommendation> recommendations = recommendationService.getUserRecommendations(owner, 1);
        Assert.assertEquals("There are 3 recommendations", 3, recommendations.size());
        Assert.assertTrue(
                "Recommendations are sorted",
                recommendations.get(0).getStatus() == NEW
                        && recommendations.get(1).getStatus() == READ
                        && recommendations.get(2).getStatus() == CLOSED
        );
    }

    @Test
    public void templateSubstitutionTest() {
        List<FrontRecommendation> recommendations = recommendationService.getUserRecommendations(owner, 1);
        Assert.assertEquals("There are 3 recommendations", 3, recommendations.size());
        Assert.assertTrue(
                "Templates are processed correctly",
                recommendations.get(0).getDescription().contains("1 1 3 NEW")
                        && recommendations.get(1).getDescription().contains("1 1 2 READ")
                        && recommendations.get(2).getDescription().contains("1 1 1 CLOSED")
        );
    }

    @Test
    public void changeStatusTest() {
        recommendationYdbDao.changeStatus(1, 1, 3, 3, READ);
        List<FrontRecommendation> recommendations = recommendationService.getUserRecommendations(owner, 1);
        Assert.assertEquals("There are 3 recommendations", 3, recommendations.size());
        Assert.assertTrue(
                "Status 'NEW' changed to 'READ'",
                recommendations.get(0).getStatus() == READ
                        && recommendations.get(2).getStatus() == CLOSED
                        && recommendations.stream().noneMatch(r -> r.getStatus() == NEW)
        );
    }

    @Test
    public void getForDashboardInterfaceSectionTest() {
        RecommendationInterfaceSection interfaceSection = RecommendationInterfaceSection.DASHBOARD;
        List<FrontRecommendation> recommendations = recommendationService.getUserRecommendations(owner, 1, interfaceSection);
        Assert.assertEquals("There are 2 recommendations", 2, recommendations.size());
    }

    @Test
    public void getForCounterListInterfaceSectionTest() {
        RecommendationInterfaceSection interfaceSection = RecommendationInterfaceSection.COUNTER_LIST_VISITS;
        List<FrontRecommendation> recommendations = recommendationService.getUserRecommendations(owner, 1, interfaceSection);
        Assert.assertEquals("There are 1 recommendations", 1, recommendations.size());
    }

    @After
    public void cleanUp() {
        List<CompletableFuture<Status>> futures = new ArrayList<>();
        futures.add(ydbTemplate.dropTable(ydbTemplate.getDatabase() + "/recommendations"));
        futures.add(ydbTemplate.dropTable(ydbTemplate.getDatabase() + "/recommendations_create_info"));
        futures.add(ydbTemplate.dropTable(ydbTemplate.getDatabase() + "/user_recommendations"));
        F.sequence(futures).join();
    }

    @Configuration
    @Import({
            RecommendationYdbDaoConfig.class,
            RecommendationDaoConfig.class,
            LocaleDictionariesConfig.class,
            CountersRbacConfig.class
    })
    public static class Config {

        @Bean
        public CountersRbac countersRbacMock() {
            return mock(CountersRbac.class);
        }

        @Bean
        public RecommendationService recommendationService(
                RecommendationYdbDao recommendationYdbDao,
                RecommendationMetaDao recommendationMetaDao,
                LocaleDictionaries localeDictionaries,
                CountersRbac countersRbacMock
        ) {
            return new RecommendationService(
                    recommendationYdbDao,
                    recommendationMetaDao,
                    localeDictionaries,
                    countersRbacMock
            );
        }
    }
}
