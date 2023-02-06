package ru.yandex.metrika.visor3d.tests;

import java.util.List;

import org.junit.Test;

import ru.yandex.metrika.visor3d.steps.WebVisorLog;
import ru.yandex.metrika.visord.chunks.EventMessageType;
import ru.yandex.metrika.wv2.proto.EventTypes;
import ru.yandex.metrika.wv2.proto.RecorderProto;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.stream.Collectors.toList;

@Stories("Scrolls")
public class Visor3dScrollsTest extends Visor3dBaseTest {

    @Test
    @Title("Проверка обработки случайных событий без скроллов")
    public void visor3dNoScrollsTest() {
        List<RecorderProto.Buffer.Builder> data = steps.generation().generateRandomWV2Payload().stream()
                .filter(it -> !(it.getData().hasEvent() && it.getData().getEvent().hasScrollEvent()))
                .filter(it -> !(it.getData().hasEvent() && it.getData().getEvent().hasResizeEvent()))
                .collect(toList());

        List<WebVisorLog> chunk = steps.generation().generateWebVisorLogs(1);
        steps.generation().setData(chunk, data, EventMessageType.WV2_EVENT_PROTO);

        steps.writeCorrectChunkAndCheckResult(chunk);
    }

    @Test
    @Title("Проверка обработки только blur событий с таргетом 0")
    public void visor3dBlurOnlyTest() {
        List<RecorderProto.Buffer.Builder> data = steps.generation().generateRandomEvents(2, EventTypes.EventType.blur);
        data.forEach(it -> it.getDataBuilder().getEventBuilder().setTarget(0));

        List<WebVisorLog> chunk = steps.generation().generateWebVisorLogs(1);
        steps.generation().setData(chunk, data, EventMessageType.WV2_EVENT_PROTO);

        steps.writeCorrectChunkAndCheckResult(chunk);
    }

    @Test
    @Title("Проверка обработки событий с 1 ресайзом")
    public void visor3dOneResizeTest() {
        List<RecorderProto.Buffer.Builder> data = steps.generation().generateRandomEvents(1, EventTypes.EventType.resize);

        List<WebVisorLog> chunk = steps.generation().generateWebVisorLogs(1);
        steps.generation().setData(chunk, data, EventMessageType.WV2_EVENT_PROTO);

        steps.writeCorrectChunkAndCheckResult(chunk);
    }

    @Test
    @Title("Проверка обработки событий с несколькими ресайзами")
    public void visor3dMultipleResizesTest() {
        List<RecorderProto.Buffer.Builder> data = steps.generation().generateRandomEvents(5, EventTypes.EventType.resize);

        List<WebVisorLog> chunk = steps.generation().generateWebVisorLogs(1);
        steps.generation().setData(chunk, data, EventMessageType.WV2_EVENT_PROTO);

        steps.writeCorrectChunkAndCheckResult(chunk);
    }

    @Test
    @Title("Проверка обработки событий с 1 скроллом")
    public void visor3dOneScrollTest() {
        List<RecorderProto.Buffer.Builder> data = steps.generation().generateRandomEvents(1, EventTypes.EventType.scroll);

        List<WebVisorLog> chunk = steps.generation().generateWebVisorLogs(1);
        steps.generation().setData(chunk, data, EventMessageType.WV2_EVENT_PROTO);

        steps.writeCorrectChunkAndCheckResult(chunk);
    }

    @Test
    @Title("Проверка обработки событий с несколькими скроллами")
    public void visor3dMultipleScrollsTest() {
        List<RecorderProto.Buffer.Builder> data = steps.generation().generateRandomEvents(5, EventTypes.EventType.scroll);

        List<WebVisorLog> chunk = steps.generation().generateWebVisorLogs(1);
        steps.generation().setData(chunk, data, EventMessageType.WV2_EVENT_PROTO);

        steps.writeCorrectChunkAndCheckResult(chunk);
    }

    @Test
    @Title("Проверка обработки событий с несколькими скроллами и ресайзами")
    public void visor3dMultipleScrollsAndResizesTest() {
        List<RecorderProto.Buffer.Builder> data = steps.generation().generateRandomEvents(5, EventTypes.EventType.resize);
        data.addAll(steps.generation().generateRandomEvents(5, EventTypes.EventType.scroll));
        steps.generation().shuffleList(data);

        List<WebVisorLog> chunk = steps.generation().generateWebVisorLogs(1);
        steps.generation().setData(chunk, data, EventMessageType.WV2_EVENT_PROTO);

        steps.writeCorrectChunkAndCheckResult(chunk);
    }

    @Test
    @Title("Проверка обработки событий с несколькими скроллами, ресайзами и другими событиями")
    public void visor3dMultipleScrollsResizesAndOtherTest() {
        List<RecorderProto.Buffer.Builder> data = steps.generation().generateRandomEvents(10);
        data.addAll(steps.generation().generateRandomEvents(5, EventTypes.EventType.resize));
        data.addAll(steps.generation().generateRandomEvents(5, EventTypes.EventType.scroll));
        steps.generation().shuffleList(data);

        List<WebVisorLog> chunk = steps.generation().generateWebVisorLogs(1);
        steps.generation().setData(chunk, data, EventMessageType.WV2_EVENT_PROTO);

        steps.writeCorrectChunkAndCheckResult(chunk);
    }

}
