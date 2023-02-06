package ru.yandex.metrika.spring.response;

import java.util.HashMap;
import java.util.Map;

import com.fasterxml.jackson.annotation.JsonUnwrapped;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.Test;

import ru.yandex.metrika.spring.profile.Profiler;
import ru.yandex.metrika.util.json.ObjectMappersFactory;

import static junit.framework.Assert.assertTrue;

/**
 * @author jkee
 */
public class JsCallbackSerializerTest {
    @Test
    public void testSerialize() throws Exception {

        ObjectMapper mapper = ObjectMappersFactory.getDefaultMapper();
        mapper.registerModule(JsCallbackSerializer.JACKSON_MODULE);

        Profiler.init(null);
        Profiler.setLayer("42");
        {
            CommonApiResponse<Data> response = CommonApiResponse.build(new Data("value"));
            String s = mapper.writerWithView(Views.ManagerInterface.class).writeValueAsString(response);
            System.out.println("build(Data):"+s);
            assertTrue(s.contains("\"key\":\"value\""));
            assertTrue(s.contains("\"layer\":\"42\""));
            assertTrue(s.contains("\"_profile\""));
        }
        {
            Map<String,Data> dd = new HashMap<>();
            dd.put("abc", new Data("value"));
            CommonApiResponse<Map<String,Data>> response = CommonApiResponse.build(dd);
            String s = mapper.writerWithView(Views.ManagerInterface.class).writeValueAsString(response);
            System.out.println("build(Map):"+ s);

        }

        {
            Map<String,Data> dd = new HashMap<>();
            dd.put("abc", new Data("value"));
            CommonApiResponse<Map<String,Data>> response = CommonApiResponse.build(dd);
            String s = mapper.writerWithView(Views.ManagerInterface.class).writeValueAsString(response);
            System.out.println("build(Map) as obj:"+s);

        }

        {
            Data value = new Data("value");
            value.getMap().put("aa","bb");
            CommonApiResponse<Data> response = CommonApiResponse.build(value);
            String s = mapper.writerWithView(Views.ManagerInterface.class).writeValueAsString(response);
            System.out.println("build(key,Obj):"+s);

        }

        /*{
            ObjectMapper mapper = new ObjectMapper(new CustomJsonFactory());
            mapper.setDateFormat(new SimpleDateFormat("yyyy-MM-dd HH:mm:ss"));
            mapper.setSerializationInclusion(JsonInclude.Include.NON_NULL);
            mapper.registerModule(TreeSerializer.JACKSON_MODULE);
            mapper.registerModule(JsCallbackSerializer.JACKSON_MODULE);

            GAApiResponse<String> response = GAApiResponse.build("key", "value");
            String s = mapper.writerWithView(Views.ManagerInterface.class).writeValueAsString(response);
            System.out.println(s);
            assertTrue(s.contains("\"key\":\"value\""));
            assertTrue(s.contains("\"layer\":\"42\""));
            assertTrue(s.contains("\"_profile\""));
        }*/

    }

    static class Data{
        String key;
        @JsonUnwrapped
        Map<String,String> map = new HashMap<>();

        public Data(String key) {
            this.key = key;
        }

        public String getKey() {
            return key;
        }

        public void setKey(String key) {
            this.key = key;
        }

        public Map<String, String> getMap() {
            return map;
        }

        public void setMap(Map<String, String> map) {
            this.map = map;
        }
    }
}
