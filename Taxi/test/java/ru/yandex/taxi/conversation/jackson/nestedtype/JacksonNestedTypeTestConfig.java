package ru.yandex.taxi.conversation.jackson.nestedtype;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class JacksonNestedTypeTestConfig {

    //TODO replace with injection from main code, when beans will be ready there
    public static final String JACKSON_NESTED_TYPE_TEST_MAPPER_NAME = "NESTED_TYPE_TEST_MAPPER";

    @Bean(JACKSON_NESTED_TYPE_TEST_MAPPER_NAME)
    public ObjectMapper objectMapper() {
        var objectMapper = new ObjectMapper();
        objectMapper.disable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES);
        objectMapper.setSerializationInclusion(JsonInclude.Include.NON_NULL);
        return objectMapper;
    }

}
