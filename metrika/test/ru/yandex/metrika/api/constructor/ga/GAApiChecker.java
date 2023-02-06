package ru.yandex.metrika.api.constructor.ga;

import java.io.IOException;
import java.nio.charset.Charset;
import java.util.Arrays;
import java.util.Collection;
import java.util.HashMap;
import java.util.Optional;
import java.util.Set;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import gnu.trove.set.hash.TLongHashSet;
import org.apache.http.HttpResponse;
import org.apache.http.NameValuePair;
import org.apache.http.client.HttpClient;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.message.BasicNameValuePair;
import org.mockito.Mockito;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import ru.yandex.metrika.managers.Currency;
import ru.yandex.metrika.managers.CurrencyInfoProvider;
import ru.yandex.metrika.managers.CurrencyService;
import ru.yandex.metrika.managers.GeoPointDao;
import ru.yandex.metrika.managers.GoalIdsDao;
import ru.yandex.metrika.managers.GoalIdsDaoImpl;
import ru.yandex.metrika.segments.core.ApiUtils;
import ru.yandex.metrika.segments.core.ApiUtilsConfig;
import ru.yandex.metrika.segments.core.bundles.SimpleProvidersBundle;
import ru.yandex.metrika.segments.core.doc.DocumentationSourceImpl;
import ru.yandex.metrika.segments.core.query.metric.MetricInternalMeta;
import ru.yandex.metrika.segments.core.query.paramertization.AttributeParamsImpl;
import ru.yandex.metrika.segments.core.query.parts.AbstractAttribute;
import ru.yandex.metrika.segments.site.bundles.CommonBundleFactory;
import ru.yandex.metrika.segments.site.bundles.ga.GAAttributeBundle;
import ru.yandex.metrika.segments.site.bundles.providers.GAProvidersBundle;
import ru.yandex.metrika.segments.site.bundles.providers.VisitProvidersBundle;
import ru.yandex.metrika.segments.site.decode.DecoderBundle;
import ru.yandex.metrika.segments.site.decode.DecodersStub;
import ru.yandex.metrika.segments.site.doc.DocumentationSourceSite;
import ru.yandex.metrika.segments.site.parametrization.AttributeParamsSite;
import ru.yandex.metrika.segments.site.schema.TableSchemaSite;
import ru.yandex.metrika.util.collections.StringMap;
import ru.yandex.metrika.util.io.UncheckedIOException;
import ru.yandex.metrika.util.locale.LocaleDictionaries;
import ru.yandex.metrika.util.log.Log4jSetup;

import static org.mockito.Matchers.anyString;

/**
 * 1. Тестируем дименшны и метрики ga на предмет работы вообще
 * 2. Тестируем на совпадение данных
 *
 * https://accounts.google.com/o/oauth2/auth?redirect_uri=http://jkee.org/auth&scope=https://www.googleapis.com/auth/analytics&response_type=token&client_id=634578038100-2tuad991s5ubtc7r2n3k8vm2aap755cm.apps.googleusercontent.com
 *
 * @author jkee
 */

public class GAApiChecker {

    private static final Logger log = LoggerFactory.getLogger(GAApiChecker.class);

    private static final String URL = "http://metrika-test.yandex.ru:8082/analytics/v3/data/ga";
    private static final String GA_URL = "https://www.googleapis.com/analytics/v3/data/ga";
    private static final String GA_OAUTH_URL = "https://accounts.google.com/o/oauth2/token";

    private static final String TOKEN = "204319735fa44070870f591fd2ae0f3d";
    private String gaToken;

    // ну это типа мой секретный токен. никому не говорите
    private static final String GA_REFRESH_TOKEN = "1/dRl7TNoU9oLqLvP_9MJYCJqv1GvaBdSdmMQy7sRWODk";

    private ApiUtils apiUtils;

    public DecoderBundle decoderBundle;
    public SimpleProvidersBundle providersBundle;

    private GAAttrsGrabber attrsGrabber;

    // список хороших, которые проверены руками
    private Set<String> goodAttrs = Sets.newHashSet(
            "ga:sessionCount",  // для мелких ключей отличается, но это история - норм
            "ga:daysSinceLastSession", // в целом норм, но там странное - ga считает что видел всех сегодня. подозрительно
            "ga:sessionDurationBucket", // длительность визита мы считаем по-разному
            "ga:referralPath", // почти сходится
            "ga:fullReferrer", // более-менее сходится

            // источники у нас по-разному считаются https://developers.google.com/analytics/devguides/platform/campaign-flow
            "ga:source",
            "ga:medium",
            "ga:sourceMedium",

            "ga:keyword", // у гугла там странное, почти сходится

            "ga:hasSocialSourceReferral", // почти сходится
            "ga:browser", // названия браузеров разные, сходимость отличная
            "ga:browserVersion", // у нас версии короче и это лучше
            "ga:operatingSystem", // немного разные названия
            "ga:operatingSystemVersion", // названия с префиксом, не критично
            "ga:mobileDeviceBranding", // у нас больше 'не определено', остальное ок
            "ga:mobileDeviceModel", // немного другие имена
            "ga:mobileDeviceInfo", // немного другие имена
            "ga:mobileDeviceMarketingName", // немного другие имена
            "ga:deviceCategory", // нет таблеток
            "ga:continent", // у нас Евразия, Европа и Азия. у них просто Европа и Азия
            "ga:country", // все отлично сходится
            "ga:region", // все отлично сходится
            "ga:city", // все отлично сходится
            "ga:latitude", // почти хорошо
            "ga:longitude", // почти хорошо
            "ga:flashVersion", // у нас до первого знака, и это лучше
            "ga:language", // у нас только первая часть (ru вместо ru-ru), другого нет, не страшно
            "ga:screenResolution", // прекрасно сходится

            "ga:pagePath", // сходится хорошо
            "ga:pagePathLevel1", // слеши немного по-другому, не критично
            "ga:pagePathLevel2", // слеши немного по-другому, не критично
            "ga:pagePathLevel3", // слеши немного по-другому, не критично
            "ga:pagePathLevel4", // слеши немного по-другому, не критично
            "ga:pageTitle", // все отлично
            "ga:landingPagePath", // все отлично
            "ga:exitPagePath", // все отлично
            "ga:previousPagePath", // у нас это реф. немного не то, но лучше чем ничего
            "ga:pageDepth", // все отлично

            "ga:yearWeek", // у нас недели с понедельника
            "ga:week", // у нас недели с понедельника
            "ga:hour", // отлично сходится
            "ga:nthMonth", // отлично сходится
            "ga:nthWeek", // у нас недели с понедельника
            "ga:nthDay", // отлично сходится
            "ga:nthHour", // отлично сходится
            "ga:nthMinute", // отлично сходится

            "ga:dateHour", // отлично сходится

            "ga:userAgeBracket", // у нас немного другие бакеты, в целом ок
            "ga:userGender", // у нас есть not set, не страшно
            "ga:interestAffinityCategory", // ключи разные совсем, что логично





            // метрики
            "ga:users", // ОНИ СКЛАДЫВАЮТ TOTALS

            "ga:goalStartsAll", // ну цели-то разные
            "ga:goalAbandonsAll", // ну цели-то разные

            // эти все для ga считаются по хитам и поэтому не очень совпадают (читай - показывают у нас херню)
            "ga:pageLoadTime",
            "ga:pageLoadSample",
            "ga:avgPageLoadTime",
            "ga:domainLookupTime",
            "ga:avgDomainLookupTime",
            "ga:pageDownloadTime",
            "ga:avgPageDownloadTime",
            "ga:redirectionTime",
            "ga:avgRedirectionTime",
            "ga:serverConnectionTime",
            "ga:avgServerConnectionTime",
            "ga:serverResponseTime",
            "ga:avgServerResponseTime",
            "ga:speedMetricsSample",
            "ga:domInteractiveTime",
            "ga:avgDomInteractiveTime",
            "ga:domLatencyMetricsSample"

    );
    private GAProvidersBundle gaProvidersBundle;
    private TableSchemaSite tableSchema;

    public static void main(String[] args) throws Exception {
        final GAApiChecker checker = new GAApiChecker();
        checker.init();

        GAApiComparator comparator = new GAApiComparator();
        comparator.setLeftUrl(GA_URL);
        comparator.setRightUrl(URL);
        comparator.setLeftToken(checker.gaToken);
        comparator.setRightToken(TOKEN);
        comparator.setDims(checker.attrsGrabber.getDims());
        comparator.setMetrics(checker.attrsGrabber.getMetrics());
        comparator.setFixedDim("ga:date");
        comparator.setGoodAttrs(checker.goodAttrs);
        comparator.setFixedMetric("ga:pageviews");
        comparator.setIsDimStub(checker::isDimStub);
        comparator.setIsMetrStub(checker::isMetrStub);
        comparator.init();
        comparator.compare();
        comparator.log();

        if (comparator.fail()) {
            System.exit(1);
        }
    }

    private static String acquireGAToken() {
        try {
            HttpClient httpClient = new DefaultHttpClient();
            HttpPost post = new HttpPost(GA_OAUTH_URL);
            UrlEncodedFormEntity form = new UrlEncodedFormEntity(Lists.<NameValuePair>newArrayList(
                    new BasicNameValuePair("client_id", "634578038100-2tuad991s5ubtc7r2n3k8vm2aap755cm@developer.gserviceaccount.com"),
                    new BasicNameValuePair("client_secret", "yiGzuHrUOdIwQg9nJEpSBrud"),
                    new BasicNameValuePair("refresh_token", GA_REFRESH_TOKEN),
                    new BasicNameValuePair("grant_type", "refresh_token")
            ), Charset.defaultCharset());
            post.setEntity(form);
            HttpResponse execute = httpClient.execute(post);
            return new ObjectMapper().readValue(execute.getEntity().getContent(), StringMap.class).get("access_token");
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    private void init() throws Exception {
        Log4jSetup.basicSetup();
        gaToken = acquireGAToken();
        attrsGrabber = new GAAttrsGrabber();
        attrsGrabber.grab();

        LocaleDictionaries localeDictionaries = new LocaleDictionaries();
        localeDictionaries.afterPropertiesSet();

        decoderBundle = Mockito.mock(DecoderBundle.class);
        Mockito.when(decoderBundle.getDecodersForLang(anyString()))
                .thenReturn(new DecodersStub());

        GoalIdsDao goalIdsDao = Mockito.mock(GoalIdsDaoImpl.class);
        Mockito.when(goalIdsDao.getGoals(Mockito.anyInt()))
                .thenReturn(new TLongHashSet(Arrays.asList(12345L, 23456L, 34567L, 45678L)));

        apiUtils = new ApiUtils();
        apiUtils.setConfig(new ApiUtilsConfig());
        tableSchema = new TableSchemaSite();
        apiUtils.setTableSchema(tableSchema);
        CurrencyService currencyService = Mockito.mock(CurrencyService.class);
        Mockito.when(currencyService.getCurrency(anyString())).thenReturn(Optional.of(new Currency(42, "ABC", "name")));
        Mockito.when(currencyService.getCurrenciesMap()).thenReturn(new HashMap<String, String>());
        CurrencyInfoProvider cip = Mockito.mock(CurrencyInfoProvider.class);
        GeoPointDao geoPointDao = new GeoPointDao();
        //currencyService.afterPropertiesSet();
        AttributeParamsImpl attributeParams = new AttributeParamsSite(goalIdsDao, geoPointDao, currencyService, cip);
        apiUtils.setAttributeParams(attributeParams);

        VisitProvidersBundle visitProvidersBundle = new VisitProvidersBundle();
        visitProvidersBundle.setCurrencyService(currencyService);
        visitProvidersBundle.setDecoderBundle(decoderBundle);
        visitProvidersBundle.setLocaleDictionaries(localeDictionaries);
        visitProvidersBundle.afterPropertiesSet();

        apiUtils.setProvidersBundle(visitProvidersBundle);

        providersBundle = new SimpleProvidersBundle();
        providersBundle.setLocaleDictionaries(localeDictionaries);

        gaProvidersBundle = new GAProvidersBundle();
        gaProvidersBundle.setDecoderBundle(decoderBundle);
        gaProvidersBundle.setLocaleDictionaries(localeDictionaries);
        gaProvidersBundle.setAttributeParams(attributeParams);
        gaProvidersBundle.setGoalIdsDao(goalIdsDao);
        gaProvidersBundle.afterPropertiesSet();

        DocumentationSourceImpl documentationSource = new DocumentationSourceSite();
        apiUtils.setDocumentationSource(documentationSource);
        apiUtils.setBundleFactory(new CommonBundleFactory(tableSchema, documentationSource, visitProvidersBundle, gaProvidersBundle));
        apiUtils.afterPropertiesSet();
    }

    private Collection<AbstractAttribute> getDimensions() {
        return new GAAttributeBundle(gaProvidersBundle, apiUtils.getUnionBundle()).getAttributes();
    }

    private boolean isDimStub(String dimension) {
        Set<AbstractAttribute> attributes = new GAAttributeBundle(gaProvidersBundle, apiUtils.getUnionBundle()).getAttributes();
        for (AbstractAttribute attribute : attributes) {
            if (attribute.toApiName().equals(dimension)) {
                return attribute.getDocumentation() != null
                        && "true".equals(attribute.getDocumentation().getAdditionalParams().get("isStub"));
            }
        }
        return false;
    }

    private boolean isMetrStub(String metr) {
        Set<MetricInternalMeta> metrics = new GAAttributeBundle(gaProvidersBundle, apiUtils.getUnionBundle()).getMetrics();
        for (MetricInternalMeta metric : metrics) {
            if (metric.getDim().equals(metr)) {
                return metric.getMeta() != null
                    && "true".equals(metric.getMeta().getAdditionalParams().get("isStub"));
            }
        }
        return false;
    }

    // wtf
    private Collection<AbstractAttribute> getMetrics() {
        return new GAAttributeBundle(gaProvidersBundle, apiUtils.getUnionBundle()).getAttributes();
    }

}
