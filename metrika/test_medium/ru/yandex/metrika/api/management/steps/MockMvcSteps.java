package ru.yandex.metrika.api.management.steps;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.test.web.servlet.ResultMatcher;
import org.springframework.test.web.servlet.request.MockHttpServletRequestBuilder;
import org.springframework.test.web.servlet.result.MockMvcResultHandlers;

import ru.yandex.metrika.spring.MetrikaApiMessageConverter;

import static org.hamcrest.Matchers.containsString;
import static org.springframework.test.web.servlet.ResultMatcher.matchAll;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.asyncDispatch;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

public class MockMvcSteps {

    protected ObjectMapper objectMapper = new MetrikaApiMessageConverter().getObjectMapper();

    protected <T> T execute(MockMvc mockMvc,
                            MockHttpServletRequestBuilder requestBuilder,
                            Class<T> returnClass) throws Exception {
        MvcResult result = execute(mockMvc, requestBuilder);
        return objectMapper.readValue(result.getResponse().getContentAsString(), returnClass);
    }

    protected MvcResult execute(MockMvc mockMvc,
                                MockHttpServletRequestBuilder requestBuilder) throws Exception {
        return execute(mockMvc, requestBuilder, status().isOk());
    }

    protected MvcResult execute(MockMvc mockMvc,
                                MockHttpServletRequestBuilder requestBuilder,
                                ResultMatcher matcher) throws Exception {
        return execute(mockMvc, requestBuilder, matcher, null);
    }

    protected MvcResult execute(MockMvc mockMvc,
                                MockHttpServletRequestBuilder requestBuilder,
                                ResultMatcher matcher,
                                String message) throws Exception {
        ResultMatcher allMatchers = message != null ?
                matchAll(matcher, jsonPath("$.message", containsString(message))) :
                matcher;
        return mockMvc.perform(requestBuilder
                .header("Authorization", "OAuth fake_token")
                .contentType(MediaType.APPLICATION_JSON))
                .andDo(MockMvcResultHandlers.print())
                .andExpect(allMatchers)
                .andReturn();
    }

    /**
     * При использовании в демоне контроллеров, возвращающих callable, запрос в mockMock делится на 2 части:
     * на сам запрос и ожидание ответа. Причем ошибка может появиться на любом этапе, как первом этапе(валидация содержимого),
     * так и на втором(не нашли элемент в бд и вернули 400)
     */
    protected <T> T executeFullAsyncAndExpectSuccess(MockMvc mockMvc,
                                                     MockHttpServletRequestBuilder requestBuilder,
                                                     Class<T> returnClass) throws Exception {
        MvcResult result = executeFullAsyncAndExpectSuccess(mockMvc, requestBuilder);
        return objectMapper.readValue(result.getResponse().getContentAsString(), returnClass);
    }

    protected MvcResult executeFullAsyncAndExpectSuccess(MockMvc mockMvc,
                                                         MockHttpServletRequestBuilder requestBuilder) throws Exception {


        MvcResult asyncResult = executeAsyncAndExpectOnFirstStep(mockMvc, requestBuilder, status().isOk());

        return mockMvc.perform(asyncDispatch(asyncResult)).andExpect(status().isOk()).andReturn();
    }

    protected MvcResult executeAsyncAndExpectOnFirstStep(MockMvc mockMvc,
                                                         MockHttpServletRequestBuilder requestBuilder,
                                                         ResultMatcher resultMatcher) throws Exception {
        return mockMvc.perform(requestBuilder
                        .contentType(MediaType.APPLICATION_JSON))
                .andDo(MockMvcResultHandlers.print())
                .andExpect(resultMatcher)
                .andReturn();
    }

    protected MvcResult executeAsyncAndExpectOnSecondStep(MockMvc mockMvc,
                                                          MockHttpServletRequestBuilder requestBuilder,
                                                          ResultMatcher resultMatcher) throws Exception {
        MvcResult asyncResult = executeAsyncAndExpectOnFirstStep(mockMvc, requestBuilder, status().isOk());
        return mockMvc.perform(asyncDispatch(asyncResult)).andExpect(resultMatcher).andReturn();
    }

}
