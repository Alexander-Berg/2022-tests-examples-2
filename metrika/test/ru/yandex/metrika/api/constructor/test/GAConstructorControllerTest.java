package ru.yandex.metrika.api.constructor.test;


import java.util.List;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.converter.HttpMessageConverter;
import org.springframework.http.converter.json.MappingJackson2HttpMessageConverter;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;
import org.springframework.test.context.web.WebAppConfiguration;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.context.WebApplicationContext;
import org.springframework.web.method.support.HandlerMethodArgumentResolver;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurationSupport;

import ru.yandex.metrika.api.constructor.ga.GAConstructorController;
import ru.yandex.metrika.api.constructor.ga.GAConstructorRequestHandler;
import ru.yandex.metrika.api.constructor.ga.GAConstructorResponse;
import ru.yandex.metrika.spring.params.RenamingProcessor;
import ru.yandex.metrika.spring.quota.QuotaRequestsByIpException;

import static org.hamcrest.Matchers.anything;
import static org.hamcrest.Matchers.is;
import static org.mockito.Mockito.any;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.reset;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.when;
import static org.springframework.http.HttpStatus.BAD_REQUEST;
import static org.springframework.http.HttpStatus.FORBIDDEN;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.asyncDispatch;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration
@WebAppConfiguration
public class GAConstructorControllerTest {

    public static final String ANALYTICS_V3_DATA_GA_URL = "/analytics/v3/data/ga";

    @Autowired
    private GAConstructorController controller;

    @Autowired
    private WebApplicationContext wac;

    private MockMvc mockMvc;

    @Test
    public void successfulResultWhenValidRequest() throws Exception {
        MvcResult result = mockMvc.perform(get(dataRequestUrlWithValidParameters())).andReturn();
        mockMvc.perform(asyncDispatch(result))
                .andExpect(status().isOk())
                .andExpect(jsonPath("kind", anything()));
    }

    @Test
    public void badRequestErrorWhenNoParametersPassed() throws Exception {
        mockMvc.perform(get(dataRequestUrlWithNoParameters()))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error.code", is(BAD_REQUEST.value())));
    }

    @Test
    public void forbiddenErrorWhenQuotaExceeded() throws Exception {
        try {
            doThrow(new QuotaRequestsByIpException("Quota exceeded for X.X.X.X ip"))
                    .when(controller).requestJson(any(), any());
            mockMvc.perform(get(dataRequestUrlWithValidParameters()))
                    .andExpect(status().isForbidden())
                    .andExpect(jsonPath("$.error.code", is(FORBIDDEN.value())));
        } finally {
            reset(controller);
        }
    }

    private String dataRequestUrlWithNoParameters() {
        return ANALYTICS_V3_DATA_GA_URL;
    }

    private String dataRequestUrlWithValidParameters() {
        return ANALYTICS_V3_DATA_GA_URL + "?" +
                "ids=ga:23441518&" +
                "dimensions=ga:date&" +
                "metrics=ga:sessions,ga:users&" +
                "start-date=2016-01-01&" +
                "end-date=2016-01-31&" +
                "max-results=10000&" +
                "start-index=1&" +
                "filters=ga:medium==organic";
    }

    @Before
    public void setup() throws Exception {
        mockMvc = MockMvcBuilders
                .webAppContextSetup(this.wac)
                .build();
    }

    @Configuration
    static class ContextConfiguration extends WebMvcConfigurationSupport {

        @Bean
        public GAConstructorController gaConstructorController() throws Exception {
            return spy(GAConstructorController.class);
        }

        @Bean
        public GAConstructorRequestHandler gaConstructorRequestHandler() {
            GAConstructorRequestHandler service = mock(GAConstructorRequestHandler.class);
            when(service.handleSimple(any(), any())).thenReturn(new GAConstructorResponse());
            return service;
        }


        @Bean
        public RenamingProcessor renamingProcessor() {
            return new RenamingProcessor(true);
        }

        @Override
        public void addArgumentResolvers(List<HandlerMethodArgumentResolver> argumentResolvers) {
            argumentResolvers.add(renamingProcessor());
        }

        @Override
        public void configureMessageConverters(List<HttpMessageConverter<?>> converters) {
            converters.add(new MappingJackson2HttpMessageConverter());
        }
    }
}
