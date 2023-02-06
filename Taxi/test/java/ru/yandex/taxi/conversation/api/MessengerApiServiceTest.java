package ru.yandex.taxi.conversation.api;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.context.junit.jupiter.web.SpringJUnitWebConfig;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.web.servlet.config.annotation.EnableWebMvc;

import ru.yandex.mj.generated.server.api.MessengerApiController;
import ru.yandex.mj.generated.server.api.MessengerApiDelegate;

@EnableWebMvc
@AutoConfigureMockMvc(addFilters = false)
@SpringJUnitWebConfig(classes = MessengerApiController.class)
class MessengerApiServiceTest {
    @MockBean
    private MessengerApiDelegate messengerApiDelegate;

    @Autowired
    private MockMvc mockMvc;

    @Test
    void inboundMessage() throws Exception {
//        MockHttpServletRequestBuilder request = MockMvcRequestBuilders
//                .post("/v1/messenger/message")
//                .contentType(MediaType.APPLICATION_JSON_UTF8)
//                .content("{}");
//
//        mockMvc
//                .perform(request)
//                .andExpect(MockMvcResultMatchers.status().isOk());
//
//        System.out.println("qwe");
    }

//    @Test
//    void deliveryReports() {
//    }
}

