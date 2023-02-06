package ru.yandex.quasar.app.configs;

import androidx.test.ext.junit.runners.AndroidJUnit4;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.robolectric.annotation.Config;

import java.util.ArrayList;
import java.util.List;

import ru.yandex.quasar.core.Configuration;
import ru.yandex.quasar.fakes.FakeConfiguration;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;

@RunWith(AndroidJUnit4.class)
@Config(manifest = Config.NONE)
public class ConfigUtilsTest {

    @Test
    public void testMergeExperiments() throws JSONException {
        JSONArray experimentsArray = new JSONArray();
        experimentsArray.put("experiment1");
        experimentsArray.put("experiment2");

        JSONObject experimentsDict = new JSONObject();
        experimentsDict.put("experiment1", "value1");
        experimentsDict.put("experiment3", "value2");

        JSONObject mergedExperiments = ConfigUtils.mergeExperiments(experimentsArray, experimentsDict);
        assertNotNull(mergedExperiments);
        assertEquals(3, mergedExperiments.length());
        assertEquals("value1", mergedExperiments.getString("experiment1"));
        assertEquals("1", mergedExperiments.getString("experiment2"));
        assertEquals("value2", mergedExperiments.getString("experiment3"));
    }

    @Test
    public void testExperimentsDictIsNull() throws JSONException {
        JSONArray experimentsArray = new JSONArray();
        experimentsArray.put("experiment1");
        experimentsArray.put("experiment2");

        JSONObject mergedExperiments = ConfigUtils.mergeExperiments(experimentsArray, null);
        assertNotNull(mergedExperiments);
        assertEquals(2, mergedExperiments.length());
        assertEquals("1", mergedExperiments.getString("experiment1"));
        assertEquals("1", mergedExperiments.getString("experiment2"));
    }

    @Test
    public void testExperimentsArrayIsNull() throws JSONException {
        JSONObject experimentsDict = new JSONObject();
        experimentsDict.put("experiment1", "value1");
        experimentsDict.put("experiment2", "value2");

        JSONObject mergedExperiments = ConfigUtils.mergeExperiments(null, experimentsDict);
        assertNotNull(mergedExperiments);
        assertEquals(2, mergedExperiments.length());
        assertEquals("value1", mergedExperiments.getString("experiment1"));
        assertEquals("value2", mergedExperiments.getString("experiment2"));
    }

    @Test
    public void testBothExperimentsAreNull() {
        JSONObject mergedExperiments = ConfigUtils.mergeExperiments(null, null);
        assertNotNull(mergedExperiments);
        assertEquals(0, mergedExperiments.length());
    }

    @Test
    public void testNotStringExperiments() throws JSONException {
        JSONArray experimentsArray = new JSONArray();
        experimentsArray.put("experiment1");
        experimentsArray.put("experiment2");

        JSONObject experimentsDict = new JSONObject();
        experimentsDict.put("experiment1", 1);
        experimentsDict.put("experiment3", true);
        experimentsDict.put("experiment4", new JSONObject());

        JSONObject mergedExperiments = ConfigUtils.mergeExperiments(experimentsArray, experimentsDict);
        assertNotNull(mergedExperiments);
        assertEquals(2, mergedExperiments.length());
        assertEquals("1", mergedExperiments.getString("experiment1"));
        assertEquals("1", mergedExperiments.getString("experiment2"));
    }

    @Test
    public void testTemplates() {
        FakeConfiguration configuration = new FakeConfiguration();
        configuration.initialize("{'patterns': {'YANDEX':'yandex', 'STATION': 'station', 'SERVICE': 'service'}, " +
                "'common': {'deviceType' : '${YANDEX}${STATION}', 'backendUrl': 'https://quasar.${YANDEX}.net', " +
                "'activeServices': ['service1', '${SERVICE}2', '${SERVICE}3${SERVICE}', 'service4service']}}");
        assertEquals(configuration.getDeviceType(), Configuration.DeviceType.YandexStation);
        assertEquals(configuration.getBackendUrl(), "https://quasar.yandex.net");
        List<String> res = new ArrayList<>();
        res.add("service1");
        res.add("service2");
        res.add("service3service");
        res.add("service4service");
        assertEquals(configuration.getActiveServices(), res);

    }
}
