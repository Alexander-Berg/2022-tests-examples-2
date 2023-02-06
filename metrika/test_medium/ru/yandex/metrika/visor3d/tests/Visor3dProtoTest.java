package ru.yandex.metrika.visor3d.tests;

import java.util.List;
import java.util.stream.Collectors;

import org.junit.Test;

import ru.yandex.metrika.common.test.medium.ByteString;
import ru.yandex.metrika.visor3d.steps.WebVisorLog;
import ru.yandex.metrika.visord.chunks.EventMessageType;
import ru.yandex.metrika.wv2.proto.RecorderProto;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.metrika.visor3d.steps.Visor3dGenerationSteps.makeSequence;

@Stories("Proto")
public class Visor3dProtoTest extends Visor3dBaseTest {

    @Test
    @Title("Проверка обработки пустых событий в PROTO формате")
    public void visor3dEmptyProtoTest() {
        List<WebVisorLog> chunk = steps.generation().generateWebVisorLogs(5);
        steps.generation().setData(chunk, ByteString.empty(), EventMessageType.WV2_EVENT_PROTO);

        steps.writeIncorrectChunkAndCheckResult(chunk);
    }

    @Test
    @Title("Проверка обработки событий с неверным типом")
    public void visor3dJsonInsteadOfProtoTest() {
        List<RecorderProto.Buffer.Builder> buffers = steps.generation().generateRandomWV2Payload();
        List<RecorderProto.Buffer> data = buffers.stream().map(RecorderProto.Buffer.Builder::build).collect(Collectors.toList());

        List<WebVisorLog> chunk = steps.generation().generateWebVisorLogs(5);
        steps.generation().setData(chunk, ByteString.fromBytes(RecorderProto.BufferWrapper.newBuilder().addAllBuffer(data).build().toByteArray()), EventMessageType.WV2_EVENT);

        steps.writeIncorrectChunkAndCheckResult(chunk);
    }

    @Test
    @Title("Проверка обработки рандомных даннных в формате PROTO")
    public void visor3dRandomProtoTest() {
        List<RecorderProto.Buffer.Builder> buffers = steps.generation().generateRandomWV2Payload();
        List<RecorderProto.Buffer.Builder> chunks = steps.generation().generateRandomChunks(15);
        makeSequence(chunks);
        buffers.addAll(chunks);

        List<WebVisorLog> chunk = steps.generation().generateWebVisorLogs(14);
        steps.generation().setData(chunk, buffers, EventMessageType.WV2_EVENT_PROTO);

        steps.writeCorrectChunkAndCheckResultWithMessages(chunk);
    }

}
