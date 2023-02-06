package ru.yandex.metrika.api.management.global;

import java.util.List;
import java.util.Map;

import com.google.common.collect.Lists;
import org.junit.Test;
import org.mockito.Mockito;

import ru.yandex.metrika.api.constructor.params.ConstructorParams;
import ru.yandex.metrika.api.segmentation.GlobalProvider;
import ru.yandex.metrika.segments.core.dao.ApiResponse;
import ru.yandex.metrika.segments.core.dao.ClickHouseDaoImpl;
import ru.yandex.metrika.segments.core.parser.QueryParams;
import ru.yandex.metrika.segments.core.query.parts.AttributeKeys;
import ru.yandex.metrika.segments.core.type.StringSetTypeConverter;
import ru.yandex.metrika.segments.core.type.TypeConverter;
import ru.yandex.metrika.segments.core.type.TypeConverters;
import ru.yandex.metrika.util.collections.MapBuilder;
import ru.yandex.metrika.util.locale.LocaleLangs;
import ru.yandex.metrika.util.log.Log4jSetup;

import static junit.framework.Assert.assertEquals;

/**
 * @author jkee
 */

public class GlobalProviderTest {

    @Test
    public void testName() throws Exception {
        Log4jSetup.basicSetup();
        GlobalProvider globalProvider = new GlobalProvider();
        StringSetTypeConverter typeConverter = new StringSetTypeConverter(
                new MapBuilder<String, String>()
                        .put("v1", "k1")
                        .put("v2", "k2")
                        .put("v3", "k3")
                        .build()
        );
        globalProvider.setNameTypeConverter(typeConverter);
        globalProvider.setIdTypeConverter(TypeConverters.getStringTypeConverter(TypeConverter.STRING_NULL_VALUE));
        globalProvider.setAttributeName("test:ololo");
        globalProvider.setCountAttributeName("test:sumФейхоа");
        ClickHouseDaoImpl clickHouseDao = Mockito.mock(ClickHouseDaoImpl.class);
        ApiResponse apiResponse = new ApiResponse();
        apiResponse.setNames(Lists.newArrayList("test:ololo"), Lists.newArrayList("test:sumФейхоа"), Lists.newArrayList("-test:sumФейхоа"));
        apiResponse.setRows(Lists.newArrayList(Lists.newArrayList("k2", "3000"), Lists.newArrayList("k3", "100")));
        apiResponse.setSrcRows(Lists.newArrayList(Lists.newArrayList("k2", "3000"), Lists.newArrayList("k3", "100")));
        apiResponse.setAsMap(Lists.newArrayList((List<Map<String, String>>) Lists.newArrayList(getMap("k2", "3000")), Lists.newArrayList(getMap("k3", "100"))));
        Mockito.when(clickHouseDao.request(Mockito.<QueryParams>any()))
                .thenReturn(apiResponse);
        globalProvider.setClickHouseDao(clickHouseDao);
        globalProvider.afterPropertiesSet();
        ConstructorParams params = new ConstructorParams();
        params.setLang(LocaleLangs.getDefaultLang());
        List<Map<String, String>> maps = globalProvider.getMaps(params);
        assertEquals(maps, Lists.newArrayList(getMap("k2", "v2"), getMap("k3", "v3"), getMap("k1", "v1")));

    }

    private static Map<String, String> getMap(String k, String v) {
        return MapBuilder.<String, String>builder()
                .put(AttributeKeys.ID, k)
                .put(AttributeKeys.NAME, v)
                .build();
    }
}
