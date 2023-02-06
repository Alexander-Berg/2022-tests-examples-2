package ru.yandex.metrika.schedulerd.cron.task.direct.dicts;

import java.util.List;

import com.fasterxml.jackson.databind.JavaType;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.Test;

import ru.yandex.metrika.util.json.ObjectMappersFactory;

/**
 * Created by orantius on 26.10.16.
 */
public class BroadmatchTypeTaskMiscTest {
    @Test
    public void execute() throws Exception {
        String resp = "[{\"EndDate\":\"2038-01-01 00:00:00\",\"SimDistance\":\"0\",\"StartDate\":\"2016-08-03 00:00:00\",\"BMType\":\"none\"},{\"EndDate\":\"2038-01-01 00:00:00\",\"SimDistance\":\"1\",\"StartDate\":\"2016-08-03 00:00:00\",\"BMType\":\"adf\"},{\"EndDate\":\"2038-01-01 00:00:00\",\"SimDistance\":\"3\",\"StartDate\":\"2016-08-03 00:00:00\",\"BMType\":\"adf\"},{\"EndDate\":\"2038-01-01 00:00:00\",\"SimDistance\":\"2\",\"StartDate\":\"2016-08-03 00:00:00\",\"BMType\":\"drf\"},{\"EndDate\":\"2038-01-01 00:00:00\",\"SimDistance\":\"9\",\"StartDate\":\"2016-08-03 00:00:00\",\"BMType\":\"adf\"},{\"EndDate\":\"2038-01-01 00:00:00\",\"SimDistance\":\"16\",\"StartDate\":\"2016-08-03 00:00:00\",\"BMType\":\"drf\"},{\"EndDate\":\"2038-01-01 00:00:00\",\"SimDistance\":\"8\",\"StartDate\":\"2016-08-03 00:00:00\",\"BMType\":\"synonym\"},{\"EndDate\":\"2038-01-01 00:00:00\",\"SimDistance\":\"11\",\"StartDate\":\"2016-08-03 00:00:00\",\"BMType\":\"synonym\"},{\"EndDate\":\"2038-01-01 00:00:00\",\"SimDistance\":\"4\",\"StartDate\":\"2016-08-03 00:00:00\",\"BMType\":\"adf\"},{\"EndDate\":\"2038-01-01 00:00:00\",\"SimDistance\":\"5\",\"StartDate\":\"2016-08-03 00:00:00\",\"BMType\":\"experiment\"},{\"EndDate\":\"2038-01-01 00:00:00\",\"SimDistance\":\"6\",\"StartDate\":\"2016-08-03 00:00:00\",\"BMType\":\"experiment\"},{\"EndDate\":\"2038-01-01 00:00:00\",\"SimDistance\":\"7\",\"StartDate\":\"2016-08-03 00:00:00\",\"BMType\":\"experiment\"},{\"EndDate\":\"2038-01-01 00:00:00\",\"SimDistance\":\"10\",\"StartDate\":\"2016-08-03 00:00:00\",\"BMType\":\"experiment\"},{\"EndDate\":\"2038-01-01 00:00:00\",\"SimDistance\":\"12\",\"StartDate\":\"2016-08-03 00:00:00\",\"BMType\":\"experiment\"},{\"EndDate\":\"2038-01-01 00:00:00\",\"SimDistance\":\"13\",\"StartDate\":\"2016-08-03 00:00:00\",\"BMType\":\"experiment\"},{\"EndDate\":\"2038-01-01 00:00:00\",\"SimDistance\":\"14\",\"StartDate\":\"2016-08-03 00:00:00\",\"BMType\":\"experiment\"},{\"EndDate\":\"2038-01-01 00:00:00\",\"SimDistance\":\"15\",\"StartDate\":\"2016-08-03 00:00:00\",\"BMType\":\"experiment\"},{\"EndDate\":\"2038-01-01 00:00:00\",\"SimDistance\":\"17\",\"StartDate\":\"2016-08-03 00:00:00\",\"BMType\":\"experiment\"},{\"EndDate\":\"2038-01-01 00:00:00\",\"SimDistance\":\"18\",\"StartDate\":\"2016-08-03 00:00:00\",\"BMType\":\"experiment\"},{\"EndDate\":\"2038-01-01 00:00:00\",\"SimDistance\":\"19\",\"StartDate\":\"2016-08-03 00:00:00\",\"BMType\":\"experiment\"},{\"EndDate\":\"2038-01-01 00:00:00\",\"SimDistance\":\"20\",\"StartDate\":\"2016-08-03 00:00:00\",\"BMType\":\"experiment\"},{\"EndDate\":\"2038-01-01 00:00:00\",\"SimDistance\":\"21\",\"StartDate\":\"2016-08-03 00:00:00\",\"BMType\":\"experiment\"},{\"EndDate\":\"2038-01-01 00:00:00\",\"SimDistance\":\"22\",\"StartDate\":\"2016-08-03 00:00:00\",\"BMType\":\"experiment\"},{\"EndDate\":\"2038-01-01 00:00:00\",\"SimDistance\":\"23\",\"StartDate\":\"2016-08-03 00:00:00\",\"BMType\":\"experiment\"},{\"EndDate\":\"2038-01-01 00:00:00\",\"SimDistance\":\"24\",\"StartDate\":\"2016-08-03 00:00:00\",\"BMType\":\"experiment\"},{\"EndDate\":\"2038-01-01 00:00:00\",\"SimDistance\":\"25\",\"StartDate\":\"2016-08-03 00:00:00\",\"BMType\":\"experiment\"},{\"EndDate\":\"2038-01-01 00:00:00\",\"SimDistance\":\"26\",\"StartDate\":\"2016-08-03 00:00:00\",\"BMType\":\"experiment\"}]";
        ObjectMapper mapper = ObjectMappersFactory.getDefaultMapper();
        JavaType javaType = mapper.getTypeFactory().constructCollectionType(List.class, BroadmatchTypeTaskMisc.BroadmatchTypeMRow.class);
        Object o = mapper.readValue(resp, javaType);
        System.out.println("o = " + o);
        String resp2 = "{\"EndDate\":\"2038-01-01 00:00:00\",\"SimDistance\":\"0\",\"StartDate\":\"2016-08-03 00:00:00\",\"BMType\":\"none\"}";
        Object o2 = mapper.readValue(resp2, BroadmatchTypeTaskMisc.BroadmatchTypeMRow.class);
        System.out.println("o2 = " + o2);

    }

}
