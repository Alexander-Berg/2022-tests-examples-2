package ru.yandex.metrika.cdp.segments;

import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.CompletableFuture;
import java.util.stream.Collectors;

import com.codahale.metrics.MetricRegistry;
import com.google.common.collect.Maps;
import org.apache.logging.log4j.Level;
import org.jetbrains.annotations.NotNull;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.metrika.api.Feature;
import ru.yandex.metrika.api.constructor.contr.ConstructorService;
import ru.yandex.metrika.api.constructor.contr.FeatureService;
import ru.yandex.metrika.api.constructor.params.ConstructorParams;
import ru.yandex.metrika.auth.AuthUtils;
import ru.yandex.metrika.cdp.ch.cluster.MtCdpCluster;
import ru.yandex.metrika.cdp.dao.AttributesDao;
import ru.yandex.metrika.cdp.dto.schema.Attribute;
import ru.yandex.metrika.cdp.dto.schema.EntityNamespace;
import ru.yandex.metrika.dbclients.clickhouse.HttpTemplate;
import ru.yandex.metrika.dbclients.mysql.DbUtils;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.dbclients.ydb.async.QueryExecutionContext;
import ru.yandex.metrika.managers.TimeZones;
import ru.yandex.metrika.rbac.ObjectsRbac;
import ru.yandex.metrika.rbac.metrika.CountersRbac;
import ru.yandex.metrika.segments.core.dao.ClickHouseDaoImpl;
import ru.yandex.metrika.segments.core.parser.AbstractTest;
import ru.yandex.metrika.segments.core.parser.SimpleTestSetup;
import ru.yandex.metrika.segments.core.query.QueryContext;
import ru.yandex.metrika.segments.core.query.RequiredFilterBuilder;
import ru.yandex.metrika.segments.site.RequiredFilterBuilderSite;
import ru.yandex.metrika.tool.AllDatabases;
import ru.yandex.metrika.util.FrontendSettings;
import ru.yandex.metrika.util.app.XmlPropertyConfigurer;
import ru.yandex.metrika.util.log.Log4jSetup;
import ru.yandex.metrika.util.route.Router;

public class CdpSegmentsTest extends AbstractTest {

    private ConstructorService target;

    @Override
    public void setUp() throws Exception {
        Log4jSetup.basicSetup(Level.DEBUG);
        SimpleTestSetup simpleTestSetup = new SimpleTestSetup();
        apiUtils = simpleTestSetup.getApiUtils();

        HttpTemplate template = AllDatabases.getCHTemplate("localhost", 31123, "cdp");
        ClickHouseDaoImpl clickHouseDao = new ClickHouseDaoImpl();
        clickHouseDao.setApiUtils(apiUtils);
        clickHouseDao.setMetricRegistry(new MetricRegistry());
        Router<HttpTemplate> templateSource = new Router<>() {
            @NotNull
            @Override
            public HttpTemplate getRouteForLayer(int layerId) {
                return template;
            }

            @NotNull
            @Override
            public HttpTemplate getRouteForCounter(int counterId) {
                return template;
            }

            @Override
            public int getLayerForCounter(int counterId) {
                return 0;
            }

            @Override
            public Map<Integer, Integer> getLayersForCounters(Collection<Integer> counterIds) {
                return Maps.newHashMap();
            }

            @Override
            public Collection<HttpTemplate> getAllRoutes() {
                return Collections.singletonList(template);
            }

            @Override
            public Map<String, String> getLayerStatus() {
                return Collections.emptyMap();
            }

            @Override
            public Set<Integer> getAllLayers() {
                return Collections.emptySet();
            }

            @Override
            public void cleanConnections() {
                template.cleanConnections();
            }
        };
        final MtCdpCluster cluster = new MtCdpCluster(templateSource);
        clickHouseDao.setCluster(cluster);

        ObjectsRbac rbac = new CountersRbac();

        TimeZones tz = new TimeZones();
        MySqlJdbcTemplate convMain = DbUtils.makeJdbcTemplateForTests(3309, "metrika", XmlPropertyConfigurer.getTextFromFile("~/.mysql/pass_old"), "conv_main");
        tz.setTemplate(convMain);
        tz.setTimeZoneProvider(new TimeZones.TimeZoneProvider() {
            @Override
            public String getTimezoneIdFor(int id) {
                return "Europe/Moscow";
            }

            @Override
            public Map<Integer, String> getTimezoneIdsFor(Collection<Integer> ids) {
                return ids.stream().collect(Collectors.toMap(id -> id, id -> "Europe/Moscow"));
            }
        });

        target = new ConstructorService();
        target.setSettings(new FrontendSettings());
        target.setApiUtils(apiUtils);
        target.setRbac(rbac);
        target.setTimeZones(tz);
        target.setFeatureService(new FeatureService() {

            @Override
            public Set<Feature> getFeatures(int id) {
                return Set.of();
            }

            @Override
            public Map<Integer, Set<Feature>> getFeatures(Iterable<? extends Integer> ids) {
                return Collections.emptyMap();
            }

            @Override
            public int addFeatures(int id, Set<Feature> features) {
                return 0;
            }

            @Override
            public int addFeatures(List<Integer> ids, Feature feature) {
                return 0;
            }

            @Override
            public void addDefaultFeatures(int id) {

            }
        });
        target.setIdProvider(ids -> ids);
        target.setClickHouseDao(clickHouseDao);
        target.setGlobalClickHouseDao(clickHouseDao);
        target.afterPropertiesSet();
    }

    @Ignore
    @Test
    public void testSimple() {
        AuthUtils.setUserDetails(AuthUtils.buildFakeDetails(1, "localhost"));

        ConstructorParams params = new ConstructorParams();
        params.setDimensions("cdp:cn:birthDate");
        params.setFilters("cdp:cn:name!n");
        params.setMetrics("cdp:cn:clients");
        params.setId(42);
        params.setDate1("2020-01-20");
        params.setDate2("2020-01-21");
        target.requestStatic(params);
    }

    @Ignore
    @Test
    public void testCustomAttr() {
        AuthUtils.setUserDetails(AuthUtils.buildFakeDetails(1, "localhost"));

        ConstructorParams params = new ConstructorParams();
        params.setDimensions("cdp:cn:birthDate");
        params.setFilters("cdp:cn:attrStr:custom_key_2=='custom_value_846297765498143651'");
        params.setMetrics("cdp:cn:clients");
        params.setId(9);
        params.setDate1("2020-01-20");
        params.setDate2("2020-01-21");
        target.requestStatic(params);
    }

    @Ignore
    @Test
    public void testCustomAttrNotNull() {
        AuthUtils.setUserDetails(AuthUtils.buildFakeDetails(1, "localhost"));

        ConstructorParams params = new ConstructorParams();
        params.setDimensions("cdp:cn:birthDate");
        params.setFilters("cdp:cn:attrStr:custom_key_2=='custom_value_846297765498143651'");
        params.setMetrics("cdp:cn:clients");
        params.setId(9);
        params.setDate1("2020-01-20");
        params.setDate2("2020-01-21");
        target.requestStatic(params);
    }

    @Ignore
    @Test
    public void testCustomAttrDim() {
        AuthUtils.setUserDetails(AuthUtils.buildFakeDetails(1, "localhost"));

        ConstructorParams params = new ConstructorParams();
        params.setDimensions("cdp:cn:attrStr:custom_key_1,cdp:cn:attrStr:custom_key_2");
        params.setFilters("(cdp:cn:birthDate>'1970-01-01')");
        params.setMetrics("cdp:cn:clients");
        params.setId(9);
        params.setDate1("2020-01-20");
        params.setDate2("2020-01-21");
        target.requestStatic(params);
    }

    @Ignore
    @Test
    public void testArrayFilter() {
        AuthUtils.setUserDetails(AuthUtils.buildFakeDetails(1, "localhost"));

        ConstructorParams params = new ConstructorParams();
        params.setDimensions("cdp:cn:birthDate");
        params.setFilters("EXISTS(cdp:cn:clientUserIDs=='some-client-user-id-3620910365023740139')");
        params.setMetrics("cdp:cn:clients");
        params.setId(9);
        params.setDate1("2020-01-20");
        params.setDate2("2020-01-21");
        target.requestStatic(params);
    }

    @Ignore
    @Test
    public void testOrders() {
        AuthUtils.setUserDetails(AuthUtils.buildFakeDetails(1, "localhost"));

        ConstructorParams params = new ConstructorParams();
        params.setDimensions("cdp:o:orderStatus");
        params.setFilters("cdp:o:revenue>0");
        params.setMetrics("cdp:o:orders");
        params.setId(9);
        params.setDate1("2020-01-20");
        params.setDate2("2020-01-21");
        target.requestStatic(params);
    }

    @Ignore
    @Test
    public void testCrossClientsAndOrders() {
        AuthUtils.setUserDetails(AuthUtils.buildFakeDetails(1, "localhost"));

        ConstructorParams params = new ConstructorParams();
        params.setDimensions("cdp:o:orderStatus");
        params.setFilters("cdp:cn:name!n");
        params.setMetrics("cdp:o:orders");
        params.setId(9);
        params.setDate1("2020-01-20");
        params.setDate2("2020-01-21");
        target.requestStatic(params);
    }

    @Ignore
    @Test
    public void testCrossContactsAndCompanies() {
        AuthUtils.setUserDetails(AuthUtils.buildFakeDetails(1, "localhost"));

        ConstructorParams params = new ConstructorParams();
        params.setDimensions("cdp:cn:birthDate");
        params.setFilters("cdp:cm:externalHardID=='some_company_001'");
        params.setMetrics("cdp:cn:clients");
        params.setId(9);
        params.setDate1("2020-01-20");
        params.setDate2("2020-01-21");
        target.requestStatic(params);
    }

    @NotNull
    private RequiredFilterBuilder getRequiredFilterBuilder() {
        RequiredFilterBuilderSite requiredFilterBuilderSite = new RequiredFilterBuilderSite();
        requiredFilterBuilderSite.setRankProvider(new CountersRbac());
        return requiredFilterBuilderSite;
    }

    public QueryContext.Builder contextBuilder() {
        return QueryContext.defaultFields()
                .apiUtils(apiUtils)
                .startDate("2020-01-11")
                .endDate("2020-01-12")
                .idsByName(Map.of("counter", new int[]{100}))
                .lang("ru");
    }

    private static final class StubAttributesDao implements AttributesDao {

        @Override
        public void save(int counterId, EntityNamespace ns, Iterable<Attribute> attributes) {

        }

        @Override
        public void save(int counterId, EntityNamespace ns, Iterable<Attribute> attributes, QueryExecutionContext executionContext) {

        }

        @Override
        public CompletableFuture<Void> saveAsync(int counterId, EntityNamespace ns, Iterable<Attribute> attributes, QueryExecutionContext executionContext) {
            return null;
        }

        @Override
        public List<Attribute> get(int counterId, EntityNamespace ns) {
            return null;
        }

        @Override
        public List<Attribute> get(int counterId, EntityNamespace ns, QueryExecutionContext executionContext) {
            return null;
        }

        @Override
        public boolean isCustomAttributeExists(int counterId, EntityNamespace entityNamespace, String name) {
            return true;
        }

        @Override
        public Optional<Attribute> getByName(int counterId, EntityNamespace ns, String name) {
            return Optional.empty();
        }

        @Override
        public Optional<Attribute> getByNameCached(int counterId, EntityNamespace ns, String name) {
            return Optional.empty();
        }

        @Override
        public CompletableFuture<Optional<Attribute>> getByNameAsync(int counterId, EntityNamespace ns, String name, QueryExecutionContext executionContext) {
            return null;
        }

        @Override
        public List<Attribute> getByNames(int counterId, EntityNamespace ns, Collection<String> names, QueryExecutionContext executionContext) {
            return null;
        }

        @Override
        public CompletableFuture<List<Attribute>> getByNamesAsync(int counterId, EntityNamespace ns, Collection<String> names, QueryExecutionContext executionContext) {
            return null;
        }

        @Override
        public CompletableFuture<List<Attribute>> getAsync(int counterId, EntityNamespace ns, QueryExecutionContext executionContext) {
            return null;
        }
    }
}
