package ru.yandex.taxi.conversation.chat.angry;

import java.util.List;
import java.util.stream.Stream;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;
import org.mockito.ArgumentCaptor;
import org.mockito.Mockito;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.context.TestPropertySource;

import ru.yandex.mj.generated.server.api.AngrySpaceApiController;
import ru.yandex.mj.generated.server.model.SmmObjectEventRequest;
import ru.yandex.taxi.conversation.AbstractFunctionalTest;
import ru.yandex.taxi.conversation.attachment.AttachmentService;
import ru.yandex.taxi.conversation.attachment.MdsAttachment;
import ru.yandex.taxi.conversation.chat.ChatEnvelopeHelper;
import ru.yandex.taxi.conversation.endpoint.Endpoint;
import ru.yandex.taxi.conversation.envelope.chat.ChatEnvelope;
import ru.yandex.taxi.conversation.handle.chat.angry.SmmObjectEventType;
import ru.yandex.taxi.conversation.logbroker.LogbrokerService;
import ru.yandex.taxi.conversation.logbroker.LogbrokerSessionIdentity;
import ru.yandex.taxi.conversation.util.ResourceHelpers;
import ru.yandex.taxi.conversation.utils.IdGeneratorService;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.params.provider.Arguments.arguments;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static ru.yandex.taxi.conversation.utils.ObjectMapperConfiguration.JSON_OBJECT_MAPPER;

@TestPropertySource(locations = "classpath:/chat/angry/data_test.properties")
public class InAngrySpaceFunctionalTest extends AbstractFunctionalTest {

    private static final String GENERATED_ENVELOP_ID = "randomId";

    private static final String TEST_MDS_ATTACHMENT_ID = "attachmentId";
    private static final String TEST_MDS_ATTACHMENT_NAME = "attachmentName";
    private static final String TEST_MDS_ATTACHMENT_CONTENT_TYPE = "image/png";
    private static final String TEST_MDS_ATTACHMENT_URL = "https://attachment.link";
    private static final long TEST_MDS_ATTACHMENT_SIZE = 1024;
    private static final String TEST_MDS_ATTACHMENT_MDS_BUCKET_NAME = "mdsBucketName";
    private static final String TEST_MDS_ATTACHMENT_MDS_KEY = "mdsKey";

    @Autowired
    private AngrySpaceApiController controller;

    @Autowired
    @Qualifier(JSON_OBJECT_MAPPER)
    private ObjectMapper objectMapper;

    @Autowired
    private LogbrokerService logbrokerService;

    @MockBean
    private IdGeneratorService idGeneratorService;

    @MockBean
    private AttachmentService attachmentService;

    private static Stream<Arguments> eventData() {
        return Stream.of(
                // vk item
                arguments(
                        "vk_new_item",
                        TestEvent.newItem().setChannel(Endpoint.Channel.PUBLIC_MESSAGE),
                        "/chat/angry/createOrEditItemEvent.json",
                        "/chat/angry/envelope/in_vk_new_item.json"
                ),
                arguments(
                        "vk_edit_item",
                        TestEvent.editItem().setChannel(Endpoint.Channel.PUBLIC_MESSAGE),
                        "/chat/angry/createOrEditItemEvent.json",
                        "/chat/angry/envelope/in_vk_edit_item.json"
                ),
                arguments(
                        "vk_delete_item",
                        TestEvent.deleteItem().setChannel(Endpoint.Channel.PUBLIC_MESSAGE),
                        "/chat/angry/createOrEditItemEvent.json",
                        "/chat/angry/envelope/in_vk_delete_item.json"
                ),

                // vk message
                arguments(
                        "vk_new_message",
                        TestEvent.newItem().setChannel(Endpoint.Channel.CHAT),
                        "/chat/angry/createOrEditMessageEvent.json",
                        "/chat/angry/envelope/in_vk_new_message.json"
                ),
                arguments(
                        "vk_edit_message",
                        TestEvent.editItem().setChannel(Endpoint.Channel.CHAT),
                        "/chat/angry/createOrEditMessageEvent.json",
                        "/chat/angry/envelope/in_vk_edit_message.json"
                ),

                // vk item attachments
                arguments(
                        "vk_item_audio_attachment",
                        TestEvent.newItem()
                                .setChannel(Endpoint.Channel.PUBLIC_MESSAGE)
                                .setAttachments("/chat/angry/attachment/vk_item_audio.json"),
                        "/chat/angry/createOrEditItemEvent.json",
                        "/chat/angry/envelope/in_vk_new_item_audio_attachment.json"
                ),
                arguments(
                        "vk_item_document_attachment",
                        TestEvent.newItem()
                                .setChannel(Endpoint.Channel.PUBLIC_MESSAGE)
                                .setAttachments("/chat/angry/attachment/vk_item_document.json")
                                .setAttachmentUrlsForMds(
                                        List.of("https://vk.com/doc56690874?hash=096bb2&no_preview=1")
                                ),
                        "/chat/angry/createOrEditItemEvent.json",
                        "/chat/angry/envelope/in_vk_new_item_document_attachment.json"
                ),
                arguments(
                        "vk_item_default_attachment",
                        TestEvent.newItem()
                                .setChannel(Endpoint.Channel.PUBLIC_MESSAGE)
                                .setAttachments("/chat/angry/attachment/vk_item_link.json"),
                        "/chat/angry/createOrEditItemEvent.json",
                        "/chat/angry/envelope/in_vk_new_item_link_attachment.json"
                ),
                arguments(
                        "vk_item_photo_attachment",
                        TestEvent.newItem()
                                .setChannel(Endpoint.Channel.PUBLIC_MESSAGE)
                                .setAttachments("/chat/angry/attachment/vk_item_photo.json")
                                .setAttachmentUrlsForMds(
                                        List.of(
                                                "https://sun9-11.userapi.com/impg/jpngsl36W?size=1440x1440&type=album",
                                                "https://sun9-48.userapi.com/impg/kIZ6A?size=1440x1440&type=album",
                                                "https://sun9-1.userapi.com/impg/_Ekv3R?size=1440x1440&type=album",
                                                "https://sun9-59.userapi.com/impg/SljhA3?size=1440x1440&type=album",
                                                "https://sun9-30.userapi.com/impg/esbmCMS?size=1440x1440&type=album",
                                                "https://sun9-50.userapi.com/impg/j-DhaYvK?size=1440x1440&type=album"
                                        )
                                ),
                        "/chat/angry/createOrEditItemEvent.json",
                        "/chat/angry/envelope/in_vk_new_item_photo_attachment.json"
                ),
                arguments(
                        "vk_item_sticker_attachment",
                        TestEvent.newItem()
                                .setChannel(Endpoint.Channel.PUBLIC_MESSAGE)
                                .setAttachments("/chat/angry/attachment/vk_item_sticker.json"),
                        "/chat/angry/createOrEditItemEvent.json",
                        "/chat/angry/envelope/in_vk_new_item_sticker_attachment.json"
                ),
                arguments(
                        "vk_item_video_attachment",
                        TestEvent.newItem()
                                .setChannel(Endpoint.Channel.PUBLIC_MESSAGE)
                                .setAttachments("/chat/angry/attachment/vk_item_video.json"),
                        "/chat/angry/createOrEditItemEvent.json",
                        "/chat/angry/envelope/in_vk_new_item_video_attachment.json"
                ),

                // vk message attachments
                arguments(
                        "vk_message_audio_attachment",
                        TestEvent.newMessage()
                                .setChannel(Endpoint.Channel.CHAT)
                                .setAttachments("/chat/angry/attachment/vk_message_audio.json"),
                        "/chat/angry/createOrEditMessageEvent.json",
                        "/chat/angry/envelope/in_vk_new_message_audio_attachment.json"
                ),
                arguments(
                        "vk_message_document_attachment",
                        TestEvent.newMessage()
                                .setChannel(Endpoint.Channel.CHAT)
                                .setAttachments("/chat/angry/attachment/vk_message_document.json")
                                .setAttachmentUrlsForMds(
                                        List.of("https://vk.com/doc359011540_&api=1&no_preview=1")
                                ),
                        "/chat/angry/createOrEditMessageEvent.json",
                        "/chat/angry/envelope/in_vk_new_message_document_attachment.json"
                ),
                arguments(
                        "vk_message_default_attachment",
                        TestEvent.newMessage()
                                .setChannel(Endpoint.Channel.CHAT)
                                .setAttachments("/chat/angry/attachment/vk_message_link.json"),
                        "/chat/angry/createOrEditMessageEvent.json",
                        "/chat/angry/envelope/in_vk_new_message_link_attachment.json"
                ),
                arguments(
                        "vk_message_photo_attachment",
                        TestEvent.newMessage()
                                .setChannel(Endpoint.Channel.CHAT)
                                .setAttachments("/chat/angry/attachment/vk_message_photo.json")
                                .setAttachmentUrlsForMds(
                                        List.of(
                                                "https://sun9-26.userapi.com/impg/07ilt?size=780x1688&type=album",
                                                "https://sun9-42.userapi.com/impg/iKRMV?size=780x1688&type=album"
                                        )
                                ),
                        "/chat/angry/createOrEditMessageEvent.json",
                        "/chat/angry/envelope/in_vk_new_message_photo_attachment.json"
                ),
                arguments(
                        "vk_message_sticker_attachment",
                        TestEvent.newMessage()
                                .setChannel(Endpoint.Channel.CHAT)
                                .setAttachments("/chat/angry/attachment/vk_message_sticker.json"),
                        "/chat/angry/createOrEditMessageEvent.json",
                        "/chat/angry/envelope/in_vk_new_message_sticker_attachment.json"
                ),
                arguments(
                        "vk_message_video_attachment",
                        TestEvent.newMessage()
                                .setChannel(Endpoint.Channel.CHAT)
                                .setAttachments("/chat/angry/attachment/vk_message_video.json"),
                        "/chat/angry/createOrEditMessageEvent.json",
                        "/chat/angry/envelope/in_vk_new_message_video_attachment.json"
                )
        );
    }

    @BeforeEach
    public void setUp() {
        Mockito.when(idGeneratorService.generate()).thenReturn(GENERATED_ENVELOP_ID);

        MdsAttachment testAttachment = new MdsAttachment();
        testAttachment.setId(TEST_MDS_ATTACHMENT_ID);
        testAttachment.setName(TEST_MDS_ATTACHMENT_NAME);
        testAttachment.setContentType(TEST_MDS_ATTACHMENT_CONTENT_TYPE);
        testAttachment.setUrl(TEST_MDS_ATTACHMENT_URL);
        testAttachment.setSize(TEST_MDS_ATTACHMENT_SIZE);
        testAttachment.setMdsBucketName(TEST_MDS_ATTACHMENT_MDS_BUCKET_NAME);
        testAttachment.setMdsKey(TEST_MDS_ATTACHMENT_MDS_KEY);
        Mockito.when(attachmentService.upload(any())).thenReturn(testAttachment);
    }

    @Test
    public void testController() {
        assertNotNull(controller);
    }

    @MethodSource("eventData")
    @ParameterizedTest(name = "{0}")
    public void testReceiveEvent(String description,
                                 TestEvent event,
                                 String eventJsonPath,
                                 String envelopeJsonPath) throws Exception {
        SmmObjectEventRequest request = prepareRequest(event, eventJsonPath);
        controller.getDelegate().receiveEvent(request);

        var sessionCaptor = ArgumentCaptor.forClass(LogbrokerSessionIdentity.class);
        var envelopeCaptor = ArgumentCaptor.forClass(byte[].class);

        verify(logbrokerService, times(1))
                .write(sessionCaptor.capture(), envelopeCaptor.capture());

        LogbrokerSessionIdentity sessionIdentity = sessionCaptor.getValue();
        checkSessionIdentity(sessionIdentity, event);

        ChatEnvelope envelope = objectMapper.readValue(envelopeCaptor.getValue(), ChatEnvelope.class);
        checkChatEnvelope(envelope, event, envelopeJsonPath);

        for (String attachmentUrl : event.getAttachmentUrlsForMds()) {
            verify(attachmentService, times(1)).openStream(attachmentUrl);
        }
    }

    private SmmObjectEventRequest prepareRequest(TestEvent event, String eventJsonPath) throws Exception {
        byte[] content = ResourceHelpers.getResource(eventJsonPath);
        String contentString = String.format(new String(content),
                event.getEventType(),
                event.getScreenName(),
                event.getProvider(),
                event.getAttachments()
        );
        return objectMapper.readValue(contentString, SmmObjectEventRequest.class);
    }

    private void checkSessionIdentity(LogbrokerSessionIdentity sessionIdentity, TestEvent event) {
        assertEquals("/functional_test/conversation-out-messages", sessionIdentity.getTopic());
        assertEquals(
                String.format("%s::%s", event.getChannel(), event.getScreenName()),
                sessionIdentity.getSourceId()
        );
    }

    private void checkChatEnvelope(ChatEnvelope envelope, TestEvent event, String envelopeJsonPath) throws Exception {
        byte[] envelopeData = ResourceHelpers.getResource(envelopeJsonPath);
        ChatEnvelope expectedEnvelope = objectMapper.readValue(envelopeData, ChatEnvelope.class);

        ChatEnvelopeHelper.assertEqualsEnvelope(expectedEnvelope, envelope, isNew(event));
    }

    private boolean isNew(TestEvent event) {
        return SmmObjectEventType.MESSAGE_NEW.getValue().equals(event.getEventType()) ||
                SmmObjectEventType.ITEM_NEW.getValue().equals(event.getEventType());
    }
}
