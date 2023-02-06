package ru.yandex.metrika.visor3d.steps;

import java.io.ByteArrayOutputStream;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Random;
import java.util.stream.LongStream;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.google.gson.reflect.TypeToken;
import com.google.protobuf.InvalidProtocolBufferException;
import com.google.protobuf.util.JsonFormat;
import org.joda.time.DateTime;
import org.springframework.stereotype.Component;

import ru.yandex.metrika.common.test.medium.ByteString;
import ru.yandex.metrika.visord.chunks.EventMessageType;
import ru.yandex.metrika.wv2.proto.EventTypes;
import ru.yandex.metrika.wv2.proto.Events;
import ru.yandex.metrika.wv2.proto.RecorderProto;
import ru.yandex.misc.lang.CharsetUtils;
import ru.yandex.qatools.allure.annotations.Step;

import static java.util.Collections.emptyList;
import static java.util.Collections.shuffle;
import static java.util.Comparator.comparing;
import static java.util.stream.Collectors.toList;
import static org.joda.time.DateTime.now;
import static ru.yandex.metrika.common.test.medium.MultiFormatter.dateFormatter;
import static ru.yandex.metrika.common.test.medium.RandomUtils.getRandomInt32;
import static ru.yandex.metrika.common.test.medium.RandomUtils.getRandomLimitedUInt32;
import static ru.yandex.metrika.common.test.medium.RandomUtils.getRandomUInt64;

@Component
public class Visor3dGenerationSteps {

    private static final Random random = new Random(0);

    private static final WebVisorLogPayloadGenerator payloadProvider = new WebVisorLogPayloadGenerator(random);

    private static final Gson gsonBuilder = new GsonBuilder().create();

    @Step("Сгенерировать данные для WebVisorLog")
    public List<RecorderProto.Buffer.Builder> generateRandomWV2Payload() {
        List<RecorderProto.Buffer.Builder> buffers = payloadProvider.eventGenerator().get(2);
        for (EventTypes.EventType value : EventTypes.EventType.values()) {
            if (value != EventTypes.EventType.UNRECOGNIZED) {
                buffers.add(payloadProvider.eventGenerator().get(value));
            }
        }
        buffers.addAll(payloadProvider.pageGenerator().get(10));
        buffers.addAll(payloadProvider.mutationGenerator().get(10));
        buffers.addAll(payloadProvider.activityGenerator().get(5));
        return buffers;
    }

    @Step("Сгенерировать чанки")
    public List<RecorderProto.Buffer.Builder> generateRandomChunks(int size) {
        return payloadProvider.chunkGenerator().get(size);
    }

    @Step("Сгенерировать активности")
    public List<RecorderProto.Buffer.Builder> generateRandomActivities(int size) {
        return payloadProvider.activityGenerator().get(size);
    }

    @Step("Сгенерировать страницы")
    public List<RecorderProto.Buffer.Builder> generateRandomPages(int size) {
        return payloadProvider.pageGenerator().get(size);
    }

    @Step("Сгенерировать события")
    public List<RecorderProto.Buffer.Builder> generateRandomEvents(int size) {
        return payloadProvider.eventGenerator().get(size);
    }

    @Step("Сгенерировать события")
    public List<RecorderProto.Buffer.Builder> generateRandomEvents(int size, EventTypes.EventType eventType) {
        return payloadProvider.eventGenerator().get(size, eventType);
    }

    @Step("Конвертирование входных данных в ожидаемые данные из YT")
    public static List<EventPacket> eventPacketsFromWebVisorLogs(List<WebVisorLog> logs) {
        List<EventPacket> output = new ArrayList<>();
        for (WebVisorLog entry : logs) {
            if (entry.getType() == 2) { //Json
                List<Package> packages = gsonBuilder.fromJson(
                        entry.getData().toString(CharsetUtils.DEFAULT_CHARSET),
                        new TypeToken<List<Package>>() {
                        }.getType());
                output.addAll(parseToYt(entry, packages));
            } else {
                output.addAll(parseToYt(entry, emptyList()));
            }
        }
        return output;
    }

    @Step("Конвертирование входных данных в ожидаемые данные WebVisor2")
    public static List<WebVisor2> webVisor2FromWebVisorLogs(List<WebVisorLog> logs) {
        List<WebVisor2> output = new ArrayList<>();
        for (WebVisorLog entry : logs) {
            WebVisor2 wv2 = new WebVisor2();
            wv2.setSeqNum(entry.getPart());
            wv2.setCounterID(entry.getCounterID());
            wv2.setUserID(entry.getUniqID());
            wv2.setHID(entry.getHit().longValue());
            long actualTime = entry.getEventTime() - BrowserInfo.getDeltaTime(entry.getBrowserInfo());
            wv2.setEventTime(actualTime);
            wv2.setDuration(calcDuration(entry));
            wv2.setActivity(0L);
            wv2.setTotalActivity(calcTotalActivity(entry));
            wv2.setUniqContent(0);
            wv2.setHasSubmits(0);
            wv2.setHasEof(calcHasEof(entry));
            output.add(wv2);
        }
        return output;
    }

    @Step("Конвертирование входных данных в cкроллы")
    public static List<ScrollPacket> scrollPacketsFromWebVisorLogs(List<WebVisorLog> logs) {
        List<ScrollPacket> output = new ArrayList<>();
        for (WebVisorLog entry : logs) {
            ScrollPacket cpch = new ScrollPacket();
            cpch.setSec(entry.getPart());
            cpch.setCounterId(entry.getCounterID());
            cpch.setUserId(entry.getUniqID());
            cpch.setHid(entry.getHit().longValue());
            long actualTime = entry.getEventTime() - BrowserInfo.getDeltaTime(entry.getBrowserInfo());
            cpch.setEventDate(dateFormatter.print(actualTime * 1000));
            cpch.setScrollCount(getScrollCount(entry));
            byte[] parsedScrolls = makeTimeEvents(entry);
            cpch.setEventData(new ByteString(parsedScrolls));
            cpch.setBufferType(BrowserInfo.fromBrowserString(entry.getBrowserInfo()).getBufferType());

            //Not normalizing urls here, please supply proper one
            cpch.setUrlNormalized(entry.getURL());

            if (parsedScrolls.length > 0) {
                output.add(cpch);
            }
        }
        return output;
    }

    public static void makeSequence(List<RecorderProto.Buffer.Builder> webVisorLogs) {
        int i = 1;
        for (RecorderProto.Buffer.Builder webVisorLog : webVisorLogs) {
            webVisorLog.setPage(i++);
            webVisorLog.setEnd(false);
        }
        webVisorLogs.get(webVisorLogs.size() - 1).setEnd(true);
    }

    private static byte[] makeTimeEvents(WebVisorLog entry) {
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        RecorderProto.Buffer prevSE = RecorderProto.Buffer.newBuilder().setStamp(0).setData(
                RecorderProto.Wrapper.newBuilder().setEvent(
                        Events.Event.newBuilder().setScrollEvent(Events.ScrollEvent.newBuilder()
                                .setX(0).setY(0).build()).build()
                ).build()).build();
        RecorderProto.Buffer prevE = null;
        RecorderProto.Buffer prevRE = null;
        int notIdle = 0;  // time units.

        List<RecorderProto.Buffer> events = entry.getUnserializedData().getBufferList().stream()
                .filter(it -> it.getData().hasEvent())
                .sorted(comparing(RecorderProto.Buffer::getStamp))
                .collect(toList());

        for (RecorderProto.Buffer buffer : events) {
            Events.Event event = buffer.getData().getEvent();
            if (event.getType() == EventTypes.EventType.resize) {
                Events.ResizeEvent re = event.getResizeEvent();
                if (re == null) {
                    continue;
                }
                if (prevRE == null || !prevRE.getData().getEvent().getResizeEvent().equals(re)) {
                    writeVB(0, baos);
                    writeVB(buffer.getStamp() / 50, baos);
                    writeVB(re.getHeight(), baos);
                    writeVB(re.getPageHeight(), baos);
                } else {
                    continue;
                }
                prevRE = buffer;
            }

            int maxNotIdle = 60000;
            if (prevE != null && !(prevE.getData().getEvent().getTarget() == 0 && prevE.getData().getEvent().getType() == EventTypes.EventType.blur)) {
                int dt = buffer.getStamp() - prevE.getStamp();
                if (dt <= maxNotIdle) {
                    notIdle += dt;
                    if (notIdle < 0) {
                        notIdle = 0;
                    }
                }
            }
            if (event.getType() == EventTypes.EventType.scroll && event.hasScrollEvent() && event.getScrollEvent().getPage()) {
                writeVB(1, baos);
                writeVB(prevSE.getStamp() / 50, baos);
                writeVB(prevSE.getData().getEvent().getScrollEvent().getY(), baos);
                writeVB(mapTimeToWv1Format(notIdle), baos);
                prevSE = buffer;
                notIdle = 0;
            }
            prevE = buffer;
        }
        if (notIdle > 0) {
            writeVB(1, baos);
            writeVB(prevSE.getStamp() / 50, baos);
            writeVB(prevSE.getData().getEvent().getScrollEvent().getY(), baos);
            writeVB(mapTimeToWv1Format(notIdle), baos);
        }

        return baos.toByteArray();
    }

    private static int mapTimeToWv1Format(int time) {
        int res = time / 50;
        int mod = time % 50;

        if (mod >= 25) {
            res++;
        }
        if (res == 0) {
            res = 1;
        }

        return res;
    }

    private static void writeVB(int n, ByteArrayOutputStream baos) {
        if (n < 0) {
            throw new IllegalArgumentException("Negative value in writeVB");
        }
        while (n > 127) {
            baos.write((n & 127) | 128);
            n >>= 7;
        }
        baos.write(n);
    }

    private static long getScrollCount(WebVisorLog entry) {
        return entry.getUnserializedData().getBufferList().stream()
                .filter(it -> it.getData().hasEvent())
                .filter(it -> it.getData().getEvent().getType() == EventTypes.EventType.scroll)
                .count();
    }

    private static long calcDuration(WebVisorLog entry) {
        return entry.getUnserializedData().getBufferList().stream()
                .filter(it -> it.getData().hasEvent())
                .filter(it -> it.getStamp() >= 0)
                .map(RecorderProto.Buffer::getStamp)
                .max(Integer::compare)
                .orElse(0) / 1000;
    }

    private static long calcTotalActivity(WebVisorLog entry) {
        return entry.getUnserializedData().getBufferList().stream()
                .map(RecorderProto.Buffer::getData)
                .filter(it -> it.getDataCase() == RecorderProto.Wrapper.DataCase.ACTIVITY)
                .map(RecorderProto.Wrapper::getActivity)
                .max(Integer::compare)
                .orElse(0);
    }

    private static int calcHasEof(WebVisorLog entry) {
        boolean hasEof = entry.getUnserializedData().getBufferList().stream()
                .map(RecorderProto.Buffer::getData)
                .filter(RecorderProto.Wrapper::hasEvent)
                .map(RecorderProto.Wrapper::getEvent).anyMatch(it -> it.getType() == EventTypes.EventType.eof);

        return (hasEof ? 1 : 0) << BrowserInfo.fromBrowserString(entry.getBrowserInfo()).getBufferType();

    }

    private static List<EventPacket> parseToYt(WebVisorLog log, List<Package> packages) {
        List<EventPacket> output = new ArrayList<>();
        List<RecorderProto.Buffer> bufferList = log.getUnserializedData().getBufferList();
        BrowserInfo browserInfo = BrowserInfo.fromBrowserString(log.getBrowserInfo());

        for (int i = 0; i < bufferList.size(); i++) {
            RecorderProto.Buffer buffer = bufferList.get(i);
            EventPacket packet = new EventPacket();

            //Key values
            packet.setCounterId(log.getCounterID());
            packet.setUserId(Long.parseUnsignedLong(log.getUniqID().toString()));
            packet.setHit((long) Integer.parseUnsignedInt(log.getHit().toString()));
            packet.setPart(log.getPart());
            packet.setBufferType(browserInfo.getBufferType());

            long actualTime = log.getEventTime() - browserInfo.getDeltaTime();
            packet.setDate(dateFormatter.print(new DateTime(actualTime * 1000)));
            packet.setIndex(i);

            //Other
            packet.setIsDataLastPart(buffer.getEnd());
            packet.setDataPart(buffer.getPage());
            packet.setTime1((buffer.getStamp() >>> 24) & 0xff);
            packet.setTime2((buffer.getStamp() >>> 16) & 0xff);
            packet.setTime3((buffer.getStamp() >>> 8) & 0xff);
            packet.setTime4(buffer.getStamp() & 0xff);
            packet.setCodeFeatures(browserInfo.getCodeFeatures());
            packet.setCodeVersion(browserInfo.getCodeVersion());

            //data and serialization
            byte[] data = new byte[0];
            if (packages.isEmpty()) { //we got proto
                packet.setSerialization(3000);
                RecorderProto.Wrapper.DataCase dataCase = buffer.getData().getDataCase();

                if (dataCase.getNumber() == 0) { //data not set, aka chunk
                    packet.setType("chunk");
                    data = buffer.getChunk().toByteArray();
                } else if (dataCase == RecorderProto.Wrapper.DataCase.EVENT) {
                    packet.setType("event");
                    data = buffer.getData().getEvent().toByteArray();
                } else if (dataCase == RecorderProto.Wrapper.DataCase.MUTATION) {
                    packet.setType("mutation");
                    data = buffer.getData().getMutation().toByteArray();
                } else if (dataCase == RecorderProto.Wrapper.DataCase.PAGE) {
                    packet.setType("page");
                    data = buffer.getData().getPage().toByteArray();
                } else if (dataCase == RecorderProto.Wrapper.DataCase.ACTIVITY) {
                    continue;
                }
            } else { //json
                Package p = packages.get(i);
                packet.setType(p.getType().toString());
                if (p.getType() == PackageType.event) {
                    packet.setSerialization(2001);
                } else {
                    packet.setSerialization(0);
                }

                data = p.getData().getBytes();
                if (p.getType() == PackageType.event && packet.getSerialization() == 2001) { //converted to proto
                    data = buffer.getData().getEvent().toByteArray();
                }
            }

            packet.setCodeVersion(browserInfo.getCodeVersion());
            packet.setCodeFeatures(browserInfo.getCodeFeatures());
            //compression
            packet.setCompression(0);

            packet.setData(data);
            output.add(packet);
        }
        return output;
    }

    public void setData(List<WebVisorLog> webVisorLogs, ByteString data, EventMessageType type) {
        webVisorLogs.forEach(webVisorLog -> {
            webVisorLog.setData(data);
            webVisorLog.setType(type.ordinal());
        });
    }

    public void setData(List<WebVisorLog> webVisorLogs, List<RecorderProto.Buffer.Builder> proto, EventMessageType type) {
        Iterator<List<RecorderProto.Buffer.Builder>> iterator = distribute(proto, webVisorLogs.size()).iterator();
        webVisorLogs.forEach(webVisorLog -> {
            RecorderProto.BufferWrapper.Builder data = RecorderProto.BufferWrapper.newBuilder().addAllBuffer(
                    iterator.next().stream().map(RecorderProto.Buffer.Builder::build).collect(toList())
            );
            if (type == EventMessageType.WV2_EVENT_PROTO) {
                webVisorLog.setData(new ByteString(data.build().toByteArray()));
            } else if (type == EventMessageType.WV2_EVENT) {
                webVisorLog.setData(ByteString.fromString(protoToJson(data), CharsetUtils.DEFAULT_CHARSET));
            } else {
                throw new IllegalArgumentException("Only WV2_EVENT_PROTO ad VW2_EVENT are supported");
            }
            webVisorLog.setUnserializedData(data.build());
            webVisorLog.setType(type.ordinal());
        });
    }

    @Step("Конвертация proto в json")
    public static String protoToJson(RecorderProto.BufferWrapperOrBuilder proto) {
        try {
            List<Package> packages = new ArrayList<>();
            for (RecorderProto.Buffer buffer : proto.getBufferList()) {
                Package p = new Package();
                p.setStamp(buffer.getStamp());
                p.setEnd(buffer.getEnd());
                p.setPartNum(buffer.getPage());
                RecorderProto.Wrapper data = buffer.getData();
                JsonObject dataJson = null;
                if (data.getDataCase() == RecorderProto.Wrapper.DataCase.PAGE) {
                    p.setType(PackageType.page);
                    dataJson = JsonParser.parseString(JsonFormat.printer().print(data.getPage())).getAsJsonObject();
                } else if (data.getDataCase() == RecorderProto.Wrapper.DataCase.MUTATION) {
                    p.setType(PackageType.mutation);
                    dataJson = JsonParser.parseString(JsonFormat.printer().print(data.getMutation())).getAsJsonObject();
                } else if (data.getDataCase() == RecorderProto.Wrapper.DataCase.EVENT) {
                    p.setType(PackageType.event);
                    dataJson = JsonParser.parseString(JsonFormat.printer().includingDefaultValueFields().print(data.getEvent())).getAsJsonObject();
                    int metaIdx = data.getEvent().getMetaCase().getNumber();
                    if (metaIdx != 0) {
                        String name = data.getEvent().getDescriptorForType().findFieldByNumber(metaIdx).getJsonName();
                        dataJson.add("meta", dataJson.get(name));
                        dataJson.remove(name);
                    } else {
                        dataJson.add("meta", null);
                    }

                    //keystrokes are put under 'meta' directly, not under 'meta.keystrokes'
                    if (data.getEvent().hasKeystrokesEvent()) {
                        dataJson.add("meta", dataJson.get("meta").getAsJsonObject().get("keystrokes"));
                    }
                }

                if (data.getDataCase() == RecorderProto.Wrapper.DataCase.ACTIVITY) {
                    p.setType(PackageType.activity);
                    p.setData(String.valueOf(data.getActivity()));
                } else {
                    if (dataJson == null) {
                        throw new IllegalArgumentException("Only page, mutation, activity and event can be serialized as json");
                    }
                    p.setData(dataJson.toString());
                }
                packages.add(p);
            }
            return gsonBuilder.toJson(packages);
        } catch (InvalidProtocolBufferException e) {
            throw new RuntimeException(e);
        }
    }

    public List<WebVisorLog> generateWebVisorLogs(int count) {
        return LongStream.range(1, count + 1).mapToObj(Visor3dGenerationSteps::generateWebVisorLog).limit(count).collect(toList());
    }

    @Step("Сгенерировать лог вебвизора")
    public static WebVisorLog generateWebVisorLog(Long counterId) {
        long time = (System.currentTimeMillis() / 1000) - random.nextInt(2000);
        return new WebVisorLog()
                .withCounterID(counterId)
                .withUniqID(getRandomUInt64(random))
                .withBrowserInfo(new BrowserInfo(random.nextInt(2),
                                            time, time + random.nextInt(100),
                                            Math.abs(random.nextLong()), random.nextInt(1000),
                                "1bo6nxnn5zutxu65")
                                .toBrowserString()
                )
                .withURL("https://money.yandex.ru/actions")
                .withHit(new BigInteger(String.valueOf(Math.abs(getRandomInt32(random)))))
                .withPart(Math.toIntExact(getRandomLimitedUInt32(random, 100)))
                .withChecksum(0L)
                .withEventTime(now().getMillis() / 1000);
    }

    public <T> void shuffleList(List<T> list) {
        shuffle(list, random);
    }

    private static <T> List<List<T>> distribute(List<T> list, int parts) {
        List<List<T>> output = new ArrayList<>(parts);
        for (int i = 0; i < parts; i++) {
            output.add(new ArrayList<>());
        }
        int i = 0;
        for (T t : list) {
            output.get(i).add(t);
            i = (i + 1) % parts;
        }
        return output;
    }

}
