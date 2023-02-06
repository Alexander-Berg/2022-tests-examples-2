package ru.yandex.metrika.mobmet.dao.cluster;

import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.locale.LangCodes;
import ru.yandex.metrika.segments.apps.bundles.AppAttributeParams;
import ru.yandex.metrika.segments.apps.bundles.MobileProvidersBundle;
import ru.yandex.metrika.segments.apps.bundles.MobmetBundleFactory;
import ru.yandex.metrika.segments.apps.bundles.funnels.param.FunnelPatternParamMetaFactory;
import ru.yandex.metrika.segments.apps.bundles.funnels.param.FunnelRestrictionParamMetaFactory;
import ru.yandex.metrika.segments.apps.doc.DocumentationSourceApps;
import ru.yandex.metrika.segments.apps.misc.PartnerTypes;
import ru.yandex.metrika.segments.apps.schema.MobmetTableSchema;
import ru.yandex.metrika.segments.core.ApiUtils;
import ru.yandex.metrika.segments.core.ApiUtilsConfig;
import ru.yandex.metrika.segments.core.doc.DocumentationSource;
import ru.yandex.metrika.segments.core.query.paramertization.AttributeParams;
import ru.yandex.metrika.util.locale.LocaleDictionaries;

import static org.mockito.Mockito.mock;

public class ApiUtilsTestUtils {

    /**
     * Метод может быть полезен во многих тестах, но пока он здесь.
     * Такой же код есть в DocTreeGenerator2, как вынести в единое место пока не понял.
     */
    public static ApiUtils buildMobApiUtils() {
        try {
            ApiUtils nApiUtils = new ApiUtils();
            nApiUtils.setConfig(new ApiUtilsConfig());
            DocumentationSource documentationSource = new DocumentationSourceApps();
            FunnelPatternParamMetaFactory funnelsParamMetaFactory = new FunnelPatternParamMetaFactory(nApiUtils);
            FunnelRestrictionParamMetaFactory funnelRestrictionParamMetaFactory = new FunnelRestrictionParamMetaFactory(nApiUtils);
            AttributeParams attributeParams = new AppAttributeParams(funnelsParamMetaFactory, funnelRestrictionParamMetaFactory);
            LocaleDictionaries localeDictionaries = new LocaleDictionaries();
            localeDictionaries.afterPropertiesSet();
            MobileProvidersBundle mobProvBundle = new MobileProvidersBundle();
            mobProvBundle.setPartnerTypes(new PartnerTypes());
            LangCodes langCodes = new LangCodes();
            langCodes.setLocaleDictionaries(localeDictionaries);
            mobProvBundle.setLangCodes(langCodes);
            mobProvBundle.setAttributeParams(attributeParams);
            PartnerTypes partnerTypes = new PartnerTypes();
            partnerTypes.setMobile(mock(MySqlJdbcTemplate.class));
            mobProvBundle.setPartnerTypes(partnerTypes);
            mobProvBundle.afterPropertiesSet();
            MobmetTableSchema tableSchema = new MobmetTableSchema();
            nApiUtils.setTableSchema(tableSchema);
            nApiUtils.setAttributeParams(attributeParams);
            nApiUtils.setDocumentationSource(documentationSource);
            nApiUtils.setBundleFactory(new MobmetBundleFactory(tableSchema, mobProvBundle, documentationSource));
            nApiUtils.afterPropertiesSet();
            return nApiUtils;
        } catch (Exception ex) {
            throw new RuntimeException(ex);
        }
    }
}
