package ru.yandex.metrika.visor3d.tests;

import java.util.List;

import org.junit.Test;

import ru.yandex.metrika.visor3d.steps.WebVisorLog;
import ru.yandex.metrika.visord.chunks.EventMessageType;
import ru.yandex.metrika.wv2.proto.EventTypes;
import ru.yandex.metrika.wv2.proto.RecorderProto;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

@Stories("Activity")
public class Visor3dActivityTest extends Visor3dBaseTest {

    @Test
    @Title("Корректность проброса общей активности из пакетов в Логброкер")
    public void visor3dTotalActivityTest() {
        List<RecorderProto.Buffer.Builder> activities = steps.generation().generateRandomActivities(6);

        List<WebVisorLog> chunk = steps.generation().generateWebVisorLogs(2);
        steps.generation().setData(chunk, activities, EventMessageType.WV2_EVENT_PROTO);

        steps.writeCorrectChunkAndCheckResultWithoutYT(chunk);
    }

    @Test
    @Title("Корректность подсчета активности из событий")
    public void visor3dCalculatedActivity() {
        List<RecorderProto.Buffer.Builder> events = steps.generation().generateRandomEvents(4, EventTypes.EventType.mousemove);
        events.addAll(steps.generation().generateRandomEvents(2, EventTypes.EventType.mousedown));
        events.addAll(steps.generation().generateRandomEvents(7, EventTypes.EventType.input));
        events.addAll(steps.generation().generateRandomEvents(4, EventTypes.EventType.scroll));

        List<WebVisorLog> chunk = steps.generation().generateWebVisorLogs(5);
        steps.generation().setData(chunk, events, EventMessageType.WV2_EVENT_PROTO);

        steps.writeCorrectChunkAndCheckResult(chunk);
    }

    @Test
    @Title("Корректность обработки отсутствия активности")
    public void visor3dNoActivity() {
        List<RecorderProto.Buffer.Builder> pages = steps.generation().generateRandomPages(10);

        List<WebVisorLog> chunk = steps.generation().generateWebVisorLogs(5);
        steps.generation().setData(chunk, pages, EventMessageType.WV2_EVENT_PROTO);

        steps.writeCorrectChunkAndCheckResult(chunk);
    }

    @Test
    @Title("Корректность обработки активности")
    public void visor3dActivity() {
        List<RecorderProto.Buffer.Builder> events = steps.generation().generateRandomActivities(5);
        events.addAll(steps.generation().generateRandomEvents(6, EventTypes.EventType.mousemove));
        events.addAll(steps.generation().generateRandomEvents(3, EventTypes.EventType.mousedown));
        events.addAll(steps.generation().generateRandomEvents(7, EventTypes.EventType.input));
        events.addAll(steps.generation().generateRandomEvents(4, EventTypes.EventType.scroll));

        List<WebVisorLog> chunk = steps.generation().generateWebVisorLogs(5);
        steps.generation().setData(chunk, events, EventMessageType.WV2_EVENT_PROTO);

        steps.writeCorrectChunkAndCheckResult(chunk);
    }

}
