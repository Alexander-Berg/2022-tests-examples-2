package ru.yandex.metrika.api.constructor.contr;

import java.util.Collection;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.Set;

import com.codahale.metrics.MetricRegistry;
import com.google.common.collect.Maps;
import gnu.trove.map.hash.TObjectLongHashMap;
import org.apache.logging.log4j.Level;
import org.jetbrains.annotations.NotNull;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;
import org.mockito.Mockito;

import ru.yandex.metrika.api.constructor.params.DrillDownParams;
import ru.yandex.metrika.auth.AuthUtils;
import ru.yandex.metrika.clusters.clickhouse.MtLogCluster;
import ru.yandex.metrika.dbclients.clickhouse.HttpTemplate;
import ru.yandex.metrika.managers.Currency;
import ru.yandex.metrika.managers.CurrencyInfoProvider;
import ru.yandex.metrika.managers.CurrencyService;
import ru.yandex.metrika.managers.GeoPointDao;
import ru.yandex.metrika.managers.GoalDao2Cached;
import ru.yandex.metrika.managers.GoalIdsDaoImpl;
import ru.yandex.metrika.rbac.OwnerProviderCached;
import ru.yandex.metrika.rbac.Role;
import ru.yandex.metrika.rbac.metrika.CountersRbac;
import ru.yandex.metrika.rbac.metrika.MetrikaRole;
import ru.yandex.metrika.segments.core.ApiUtils;
import ru.yandex.metrika.segments.core.ApiUtilsConfig;
import ru.yandex.metrika.segments.core.dao.ClickHouseDaoImpl;
import ru.yandex.metrika.segments.core.query.paramertization.AttributeParamsImpl;
import ru.yandex.metrika.segments.core.query.paramertization.GroupType;
import ru.yandex.metrika.segments.site.RowsUniquesProvider;
import ru.yandex.metrika.segments.site.SamplerSite;
import ru.yandex.metrika.segments.site.bundles.CommonBundleFactory;
import ru.yandex.metrika.segments.site.bundles.providers.GAProvidersBundle;
import ru.yandex.metrika.segments.site.bundles.providers.VisitProvidersBundle;
import ru.yandex.metrika.segments.site.doc.DocumentationSourceSite;
import ru.yandex.metrika.segments.site.parametrization.AttributeParamsSite;
import ru.yandex.metrika.segments.site.schema.TableSchemaSite;
import ru.yandex.metrika.tool.AllDatabases;
import ru.yandex.metrika.util.FrontendSettings;
import ru.yandex.metrika.util.collections.MapBuilder;
import ru.yandex.metrika.util.geobase.GeoBase;
import ru.yandex.metrika.util.locale.LocaleDictionaries;
import ru.yandex.metrika.util.log.Log4jSetup;
import ru.yandex.metrika.util.route.Router;

import static org.mockito.Matchers.anyString;

/**
 * Created by orantius on 6/2/15.
 */
@Ignore
public class ConstructorServiceTest {

    private ConstructorService target;

    @Before
    public void setUp() throws Exception {
        Log4jSetup.basicSetup(Level.DEBUG);
        target = new ConstructorService();
        target.setSettings(new FrontendSettings());
        ApiUtils apiUtils = new ApiUtils();
        apiUtils.setConfig(new ApiUtilsConfig());
        DocumentationSourceSite documentationSource = new DocumentationSourceSite();
        apiUtils.setDocumentationSource(documentationSource);
        TableSchemaSite tableSchema = new TableSchemaSite();

        GoalIdsDaoImpl goalIdsDao = new GoalIdsDaoImpl();
        GoalDao2Cached goalDao2 = new GoalDao2Cached();
        CurrencyService currencyService = Mockito.mock(CurrencyService.class);
        Mockito.when(currencyService.getCurrency(anyString())).thenReturn(Optional.of(new Currency(42, "ABC", "name")));
        Mockito.when(currencyService.getCurrenciesMap()).thenReturn(new HashMap<>());
        CurrencyInfoProvider cip = Mockito.mock(CurrencyInfoProvider.class);
        GeoPointDao geoPointDao = new GeoPointDao();
        //currencyService.afterPropertiesSet();
        AttributeParamsImpl attributeParams = new AttributeParamsSite(goalIdsDao, geoPointDao, currencyService,cip);
        LocaleDictionaries localeDictionaries = new LocaleDictionaries();
        GeoBase geoBase = new GeoBase();

        Map<String, Role> scopes = new HashMap<>();
        scopes.put("metrika:read", MetrikaRole.api_read);
        scopes.put("metrika:write", MetrikaRole.api_write);
        CountersRbac rbac = new CountersRbac();

        OwnerProviderCached ownerProvider = new OwnerProviderCached();
        ownerProvider.setRbac(rbac);

        VisitProvidersBundle visitProvidersBundle = new VisitProvidersBundle();
        visitProvidersBundle.setCurrencyService(currencyService);
        visitProvidersBundle.setAttributeParams(attributeParams);
        visitProvidersBundle.setLocaleDictionaries(localeDictionaries);
        visitProvidersBundle.setGoalIdsDao(goalIdsDao);
        visitProvidersBundle.setGoalDao2(goalDao2);
        visitProvidersBundle.setOwnerProvider(ownerProvider);
        visitProvidersBundle.afterPropertiesSet();

        GAProvidersBundle gaProvidersBundle = new GAProvidersBundle();
        gaProvidersBundle.setAttributeParams(attributeParams);
        gaProvidersBundle.setLocaleDictionaries(localeDictionaries);
        gaProvidersBundle.setGoalIdsDao(goalIdsDao);
        gaProvidersBundle.setGeoBase(geoBase);
        gaProvidersBundle.afterPropertiesSet();

        HttpTemplate template = AllDatabases.getCHTemplate("localhost", 31123,"default");

        apiUtils.setBundleFactory(new CommonBundleFactory(tableSchema, documentationSource,
                visitProvidersBundle,
                gaProvidersBundle));
        apiUtils.setAttributeParams(attributeParams);
        apiUtils.setSampler(new SamplerSite(new TObjectLongHashMap<>(), new TObjectLongHashMap<>(), new TObjectLongHashMap<>(), new RowsUniquesProvider() { }));
        apiUtils.setTableSchema(tableSchema);
        ClickHouseDaoImpl clickHouseDao = new ClickHouseDaoImpl();
        clickHouseDao.setApiUtils(apiUtils);
        clickHouseDao.setMetricRegistry(new MetricRegistry());
        Router<HttpTemplate> templateSource = new Router<HttpTemplate>() {
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
        final MtLogCluster cluster = new MtLogCluster(templateSource);
        clickHouseDao.setCluster(cluster);
        apiUtils.setCluster(cluster);
        apiUtils.afterPropertiesSet();
        target.setApiUtils(apiUtils);
        target.setClickHouseDao(clickHouseDao);
        target.afterPropertiesSet();
    }

    @Test
    public void testRequestDrillDown() throws Exception {
        AuthUtils.setUserDetails(AuthUtils.buildFakeDetails(1, "localhost"));
        DrillDownParams params = new DrillDownParams();
        /*http://mtback01et.yandex.ru:8082/stat/v1/data/drilldown?
offset=1
&limit=20
&row_ids=
&request_id=2r9o2tv
&include_undefined=true
&date1=2015-04-20
&date2=2015-04-26
&dimensions=ym%3As%3AparamsLevel2%2Cym%3As%3AparamsLevel3%2Cym%3As%3A%3Cattribution%3ETrafficSource%2Cym%3As%3AparamsLevel4%2Cym%3As%3AparamsLevel5
&parent_id=%5B%22Xiva-%D1%83%D0%B2%D0%B5%D0%B4%D0%BE%D0%BC%D0%BB%D0%B5%D0%BD%D0%B8%D0%B5%20%D0%BE%20%D0%BD%D0%BE%D0%B2%D0%BE%D0%BC%20%D0%BF%D0%B8%D1%81%D1%8C%D0%BC%D0%B5%22%5D
&sort=-ym%3As%3AsumParams
&group=day
&ids=22836271
&filters=ym%3As%3AparamsLevel2!n
&attribution=Last
&quantile=50
&accuracy=full
&metrics=ym%3As%3Avisits%2Cym%3As%3AsumParams%2Cym%3As%3AavgParams%2Cym%3As%3AparamsNumber%2Cym%3As%3AbounceRate%2Cym%3As%3ApageDepth%2Cym%3As%3AavgVisitDurationSeconds
&interface=1
&lang=ru
&request_domain=ru
&uid_real=30127817
&uid=30127817*/
        params.setOffset(1);
        params.setLimit(20);
        params.setIncludeUndefined(true);
        params.setDate1("2015-04-20");
        params.setDate2("2015-04-26");
        //params.setDimensions("ym:s:paramsLevel2,ym:s:paramsLevel3,ym:s:<attribution>TrafficSource,ym:s:paramsLevel4,ym:s:paramsLevel5");
        params.setDimensions("ym:s:paramsLevel2,ym:s:paramsLevel3,ym:s:paramsLevel4,ym:s:paramsLevel5");
        params.setParentId(Collections.singletonList("Xiva-уведомление о новом письме"));
        params.setSort("-ym:s:sumParams");
        params.setGroup(GroupType.day);
        params.setIds(new int[]{22836271});
        params.setFilters("ym:s:paramsLevel2!n");
        params.setOtherParams(MapBuilder.stringBuilder().put("attribution", "Last").put("quantile", "50").put("interface", "1").build());
        params.setAccuracy("full");
        params.setMetrics("ym:s:visits,ym:s:sumParams,ym:s:avgParams,ym:s:paramsNumber,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds");
        params.setLang("ru");
        params.setRequestDomain("ru");
        target.requestDrillDown(params);
    }

    @Test
    public void test16650() throws Exception {
        AuthUtils.setUserDetails(AuthUtils.buildFakeDetails(1, "localhost"));
        DrillDownParams params = new DrillDownParams();
        /*http://mtback01e.yandex.ru:8082/stat/v1/data/drilldown?
        offset=1&
        limit=20&
        row_ids=&
        request_id=2ob84r2&
        include_undefined=true
        &date1=2015-05-03&date2=2015-06-03
        &dimensions=ym%3As%3AparamsLevel1%2Cym%3As%3AparamsLevel2
        &parent_id=%5B%22from%22%5D&sort=-ym%3As%3Avisits&group=day&ids=722889&
        filters=ym%3As%3AparamsLevel1!n&attribution=Last&quantile=50
        &accuracy=medium
        &metrics=ym%3As%3Avisits%2Cym%3As%3AsumParams%2Cym%3As%3AavgParams%2Cym%3As%3AparamsNumber%2Cym%3As%3AbounceRate%2Cym%3As%3ApageDepth%2Cym%3As%3AavgVisitDurationSeconds
        &interface=1&lang=ru&request_domain=ru&uid_real=30127817&uid=30127817*/
        params.setOffset(1);
        params.setLimit(20);
        params.setIncludeUndefined(true);
        params.setDate1("2015-05-03");
        params.setDate2("2015-06-03");
        params.setDimensions("ym:s:paramsLevel1,ym:s:paramsLevel2");
        params.setParentId(Collections.singletonList("from"));
        params.setSort("-ym:s:visits");
        params.setGroup(GroupType.day);
        params.setIds(new int[]{722889});
        params.setFilters("ym:s:paramsLevel1!n");
        params.setOtherParams(MapBuilder.stringBuilder().put("attribution", "Last").put("quantile", "50").put("interface", "1").build());
        params.setAccuracy("medium");
        params.setMetrics("ym:s:visits,ym:s:sumParams,ym:s:avgParams,ym:s:paramsNumber,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds");
        params.setLang("ru");
        params.setRequestDomain("ru");
        target.requestDrillDown(params);
    }

    /**/
}
