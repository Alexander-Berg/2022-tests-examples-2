package ru.yandex.metrika.visor3d.tests;

import java.util.List;

import org.junit.Test;

import ru.yandex.metrika.common.test.medium.ByteString;
import ru.yandex.metrika.visor3d.steps.WebVisorLog;
import ru.yandex.metrika.visord.chunks.EventMessageType;
import ru.yandex.metrika.wv2.proto.RecorderProto;
import ru.yandex.misc.lang.CharsetUtils;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.stream.Collectors.toList;
import static ru.yandex.metrika.visor3d.steps.Visor3dGenerationSteps.protoToJson;

@Stories("Json")
public class Visor3dJsonTest extends Visor3dBaseTest {

    @Test
    @Title("Проверка обработки пустых событий в JSON формате")
    public void visor3dEmptyJsonTest() {
        List<WebVisorLog> chunk = steps.generation().generateWebVisorLogs(5);
        steps.generation().setData(chunk, ByteString.empty(), EventMessageType.WV2_EVENT);

        steps.writeIncorrectChunkAndCheckResult(chunk);
    }

    @Test
    @Title("Проверка обработки событий с неверным типом")
    public void visor3dProtoInsteadOfJsonTest() {
        List<RecorderProto.Buffer.Builder> data = steps.generation().generateRandomWV2Payload();
        String json = protoToJson(RecorderProto.BufferWrapper.newBuilder().addAllBuffer(data.stream().map(RecorderProto.Buffer.Builder::build).collect(toList())));

        List<WebVisorLog> chunk = steps.generation().generateWebVisorLogs(5);
        steps.generation().setData(chunk, ByteString.fromString(json, CharsetUtils.DEFAULT_CHARSET), EventMessageType.WV2_EVENT_PROTO);

        steps.writeIncorrectChunkAndCheckResult(chunk);
    }

    @Test
    @Title("Проверка обработки рандомных даннных в формате JSON")
    public void visor3dRandomJsonTest() {
        List<RecorderProto.Buffer.Builder> buffers = steps.generation().generateRandomWV2Payload();

        List<WebVisorLog> chunk = steps.generation().generateWebVisorLogs(11);
        steps.generation().setData(chunk, buffers, EventMessageType.WV2_EVENT);

        steps.writeCorrectChunkAndCheckResult(chunk);
    }

}
