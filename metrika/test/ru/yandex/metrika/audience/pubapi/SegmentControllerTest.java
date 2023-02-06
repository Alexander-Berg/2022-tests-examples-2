package ru.yandex.metrika.audience.pubapi;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.runners.MockitoJUnitRunner;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import ru.yandex.audience.uploading.SegmentUploadingService;
import ru.yandex.audience.uploading.UploadingSegment;
import ru.yandex.metrika.spring.auth.TargetUserHandlerMethodArgumentResolver;

import static org.mockito.Matchers.anyObject;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@RunWith(MockitoJUnitRunner.class)
public class SegmentControllerTest {

    @Mock
    SegmentUploadingService segmentUploadingService;

    @InjectMocks
    SegmentController segmentController;

    @InjectMocks
    TargetUserHandlerMethodArgumentResolver userArgResolver;

    @Test
    public void returnsOkWhenConfirmClientId() throws Exception {
        SegmentController.ClientIdSegmentRequestUploadingWrapper requestObject =
                new SegmentController.ClientIdSegmentRequestUploadingWrapper(clientIdSegmentRequestUploading());
        String requestJson = new ObjectMapper().writeValueAsString(requestObject);
        String url = "/v1/management/segment/client_id/123/confirm";
        MockMvc mockMvc = MockMvcBuilders.standaloneSetup(segmentController)
                .setCustomArgumentResolvers(userArgResolver)
                .build();
        mockMvc.perform(post(url)
                .accept(MediaType.parseMediaType("application/json;charset=UTF-8"))
                .header("Content-Type", "application/json;charset=UTF-8")
                .content(requestJson))
                .andExpect(status().isOk())
        ;
    }

    private ClientIdSegmentRequestUploading clientIdSegmentRequestUploading() {
        ClientIdSegmentRequestUploading request = new ClientIdSegmentRequestUploading();
        request.setCounterId(321);
        request.setName("asd");
        return request;
    }

    @Before
    public void setup() throws Exception {
        when(segmentUploadingService.confirm(anyObject(), anyObject())).thenReturn(new UploadingSegment());
    }

}
