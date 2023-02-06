package ru.yandex.metrika.visor3d.steps;

import java.util.List;
import java.util.Random;
import java.util.function.Supplier;
import java.util.stream.IntStream;

import com.google.protobuf.ByteString;

import ru.yandex.metrika.wv2.proto.EventTypes;
import ru.yandex.metrika.wv2.proto.Events;
import ru.yandex.metrika.wv2.proto.Mutations;
import ru.yandex.metrika.wv2.proto.Pages;
import ru.yandex.metrika.wv2.proto.RecorderProto;

import static java.util.stream.Collectors.toList;
import static java.util.stream.Stream.generate;
import static ru.yandex.metrika.common.test.medium.RandomUtils.getRandomBoolean;
import static ru.yandex.metrika.common.test.medium.RandomUtils.getRandomFloat;
import static ru.yandex.metrika.common.test.medium.RandomUtils.getRandomInt32;
import static ru.yandex.metrika.common.test.medium.RandomUtils.getRandomInt8;
import static ru.yandex.metrika.common.test.medium.RandomUtils.getRandomString;
import static ru.yandex.metrika.common.test.medium.RandomUtils.getRandomUInt16;
import static ru.yandex.metrika.wv2.proto.EventTypes.EventType.blur;
import static ru.yandex.metrika.wv2.proto.EventTypes.EventType.canvasMethod;
import static ru.yandex.metrika.wv2.proto.EventTypes.EventType.canvasProperty;
import static ru.yandex.metrika.wv2.proto.EventTypes.EventType.change;
import static ru.yandex.metrika.wv2.proto.EventTypes.EventType.click;
import static ru.yandex.metrika.wv2.proto.EventTypes.EventType.deviceRotation;
import static ru.yandex.metrika.wv2.proto.EventTypes.EventType.eof;
import static ru.yandex.metrika.wv2.proto.EventTypes.EventType.fatalError;
import static ru.yandex.metrika.wv2.proto.EventTypes.EventType.focus;
import static ru.yandex.metrika.wv2.proto.EventTypes.EventType.hashchange;
import static ru.yandex.metrika.wv2.proto.EventTypes.EventType.input;
import static ru.yandex.metrika.wv2.proto.EventTypes.EventType.keystroke;
import static ru.yandex.metrika.wv2.proto.EventTypes.EventType.mediaMethod;
import static ru.yandex.metrika.wv2.proto.EventTypes.EventType.mediaProperty;
import static ru.yandex.metrika.wv2.proto.EventTypes.EventType.mousedown;
import static ru.yandex.metrika.wv2.proto.EventTypes.EventType.mousemove;
import static ru.yandex.metrika.wv2.proto.EventTypes.EventType.mouseup;
import static ru.yandex.metrika.wv2.proto.EventTypes.EventType.resize;
import static ru.yandex.metrika.wv2.proto.EventTypes.EventType.scroll;
import static ru.yandex.metrika.wv2.proto.EventTypes.EventType.selection;
import static ru.yandex.metrika.wv2.proto.EventTypes.EventType.touchcancel;
import static ru.yandex.metrika.wv2.proto.EventTypes.EventType.touchend;
import static ru.yandex.metrika.wv2.proto.EventTypes.EventType.touchforcechange;
import static ru.yandex.metrika.wv2.proto.EventTypes.EventType.touchmove;
import static ru.yandex.metrika.wv2.proto.EventTypes.EventType.touchstart;
import static ru.yandex.metrika.wv2.proto.EventTypes.EventType.windowblur;
import static ru.yandex.metrika.wv2.proto.EventTypes.EventType.windowfocus;
import static ru.yandex.metrika.wv2.proto.EventTypes.EventType.zoom;

public class WebVisorLogPayloadGenerator {

    private Random random;

    public WebVisorLogPayloadGenerator(Random random) {
        this.random = random;
    }

    public ActivityGenerator activityGenerator() {
        return new ActivityGenerator();
    }

    public ChunkGenerator chunkGenerator() {
        return new ChunkGenerator();
    }

    public PageGenerator pageGenerator() {
        return new PageGenerator();
    }

    public MutationGenerator mutationGenerator() {
        return new MutationGenerator();
    }

    public EventGenerator eventGenerator() {
        return new EventGenerator();
    }

    public class ActivityGenerator {
        private ActivityGenerator() {
        }

        public RecorderProto.Buffer.Builder get() {
            return RecorderProto.Buffer.newBuilder()
                    .setStamp(getRandomUInt16(random))
                    .setEnd(true)
                    .setPage(1)
                    .setData(RecorderProto.Wrapper.newBuilder().setActivity(getRandomUInt16(random)));
        }

        public List<RecorderProto.Buffer.Builder> get(int count) {
            return generate((Supplier<RecorderProto.Buffer.Builder>) this::get).limit(count).collect(toList());
        }
    }

    public class ChunkGenerator {
        private ChunkGenerator() {
        }

        public RecorderProto.Buffer.Builder get() {
            return RecorderProto.Buffer.newBuilder()
                    .setStamp(getRandomUInt16(random))
                    .setChunk(randomBytes())
                    .setPage(random.nextInt(20) + 1)
                    .setEnd(getRandomBoolean(random));
        }

        public List<RecorderProto.Buffer.Builder> get(int count) {
            return generate((Supplier<RecorderProto.Buffer.Builder>) this::get).limit(count).collect(toList());
        }

        private ByteString randomBytes() {
            int size = getRandomUInt16(random);
            byte[] bytes = new byte[size];
            for (int i = 0; i < size; i++) {
                bytes[i] = getRandomInt8(random).byteValue();
            }
            return ByteString.copyFrom(bytes);
        }
    }

    public class PageGenerator {
        private PageGenerator() {
        }

        public RecorderProto.Buffer.Builder get() {
            Pages.Page.Builder page = Pages.Page.newBuilder()
                    .setMeta(getMeta())
                    .setFrameId(getRandomInt32(random))
                    .setTabId(getRandomString(random))
                    .setRecordStamp(random.nextLong());
            int contents = random.nextInt(5);
            for (int i = 0; i < contents; i++) {
                page.addContent(getContent());
            }

            return RecorderProto.Buffer.newBuilder()
                    .setStamp(getRandomUInt16(random))
                    .setData(RecorderProto.Wrapper.newBuilder().setPage(page).build())
                    .setPage(1)
                    .setEnd(true);
        }

        public List<RecorderProto.Buffer.Builder> get(int count) {
            return generate((Supplier<RecorderProto.Buffer.Builder>) this::get).limit(count).collect(toList());
        }

        public Pages.Page.Meta.Builder getMeta() {
            Pages.Page.Meta.Builder builder = Pages.Page.Meta.newBuilder()
                    .setDoctype(getRandomString(random))
                    .setTitle(getRandomString(random))
                    .setAddress(getRandomString(random))
                    .setUa(getRandomString(random))
                    .setReferrer(getRandomString(random))
                    .setScreen(Pages.Page.Box.newBuilder().setWidth(random.nextInt(4096)).setHeight(random.nextInt(4096)).build())
                    .setViewport(Pages.Page.Box.newBuilder().setWidth(random.nextInt(4096)).setHeight(random.nextInt(4096)).build())
                    .setLocation(Pages.Page.Location.newBuilder()
                            .setHost(getRandomString(random))
                            .setProtocol("http" + (getRandomBoolean(random) ? "s" : ""))
                            .setPath(getRandomString(random))
                            .build())
                    .addInitialScroll(Pages.Page.Scroll.newBuilder()
                            .setTarget(getRandomUInt16(random))
                            .addScroll(getRandomUInt16(random))
                            .addScroll(getRandomUInt16(random))
                            .addScroll(getRandomUInt16(random))
                            .build())
                    .addInitialScroll(Pages.Page.Scroll.newBuilder()
                            .setTarget(getRandomUInt16(random))
                            .addScroll(getRandomUInt16(random))
                            .addScroll(getRandomUInt16(random))
                            .build());
            if (getRandomBoolean(random)) {
                builder.setHasBase(true)
                        .setBase(getRandomString(random));
            }
            return builder;

        }

        public Pages.Page.Content.Builder getContent() {
            Pages.Page.Content.Builder builder = Pages.Page.Content.newBuilder()
                    .setId(getRandomUInt16(random))
                    .setName(getRandomString(random))
                    .setParent(getRandomUInt16(random))
                    .setContent(getRandomString(random))
                    .setNext(getRandomUInt16(random))
                    .setPrev(getRandomUInt16(random));
            int attributes = random.nextInt(10);
            for (int i = 0; i < attributes; i++) {
                builder.putAttributes(getRandomString(random), getRandomString(random));
            }
            return builder;
        }
    }

    public class MutationGenerator {
        public RecorderProto.Buffer.Builder get() {
            Mutations.Mutation.Builder mutation = Mutations.Mutation.newBuilder()
                    .setTarget(getRandomUInt16(random))
                    .setStamp(getRandomUInt16(random))
                    .setFrameId(getRandomInt32(random));

            Mutations.Mutation.Meta.Builder meta = Mutations.Mutation.Meta.newBuilder()
                    .setIndex(getRandomUInt16(random));

            int changes = random.nextInt(10);
            for (int i = 0; i < changes; i++) {
                meta.addChanges(getChanges());
            }

            mutation.setMeta(meta);

            return RecorderProto.Buffer.newBuilder()
                    .setStamp(getRandomUInt16(random))
                    .setData(RecorderProto.Wrapper.newBuilder().setMutation(mutation).build())
                    .setPage(1)
                    .setEnd(true);
        }

        public List<RecorderProto.Buffer.Builder> get(int count) {
            return generate((Supplier<RecorderProto.Buffer.Builder>) this::get).limit(count).collect(toList());
        }

        public Mutations.Mutation.Changes.Builder getChanges() {
            Mutations.Mutation.Changes.Builder builder = Mutations.Mutation.Changes.newBuilder();

            int deletes = random.nextInt(10);
            for (int i = 0; i < deletes; i++) {
                builder.addA(getDelete());
            }

            int adds = random.nextInt(10);
            for (int i = 0; i < adds; i++) {
                builder.addB(getAdd());
            }

            int attrCh = random.nextInt(10);
            for (int i = 0; i < attrCh; i++) {
                builder.addC(getAttributeChange());
            }

            int textCh = random.nextInt(10);
            for (int i = 0; i < textCh; i++) {
                builder.addD(getTextChange());
            }
            return builder;
        }

        public Mutations.Mutation.Delete.Builder getDelete() {
            return Mutations.Mutation.Delete.newBuilder()
                    .setId(getRandomUInt16(random))
                    .setPr(getRandomUInt16(random))
                    .setNx(getRandomUInt16(random))
                    .setPa(getRandomUInt16(random))
                    .setI(getRandomUInt16(random));
        }

        public Mutations.Mutation.Add.Builder getAdd() {
            Mutations.Mutation.Add.Builder builder = Mutations.Mutation.Add.newBuilder()
                    .setId(getRandomUInt16(random))
                    .setNm(getRandomString(random))
                    .setPa(getRandomUInt16(random))
                    .setNs(getRandomString(random))
                    .setPr(getRandomUInt16(random))
                    .setCt(getRandomString(random))
                    .setNx(getRandomUInt16(random))
                    .setI(getRandomUInt16(random));
            int attributes = random.nextInt(10);
            for (int i = 0; i < attributes; i++) {
                builder.putAt(getRandomString(random), getRandomString(random));
            }
            return builder;

        }

        public Mutations.Mutation.TextChange.Builder getTextChange() {
            return Mutations.Mutation.TextChange.newBuilder()
                    .setId(getRandomUInt16(random))
                    .setCt(getBeforeAfter())
                    .setI(getRandomUInt16(random));
        }

        public Mutations.Mutation.AttributeChange.Builder getAttributeChange() {
            Mutations.Mutation.AttributeChange.Builder builder = Mutations.Mutation.AttributeChange.newBuilder()
                    .setId(getRandomUInt16(random))
                    .setI(getRandomUInt16(random));

            int attributes = random.nextInt(10);
            for (int i = 0; i < attributes; i++) {
                builder.putAt(getRandomString(random), getBeforeAfter().build());
            }
            return builder;

        }

        public Mutations.Mutation.BeforeAfter.Builder getBeforeAfter() {
            return Mutations.Mutation.BeforeAfter.newBuilder()
                    .setO(getRandomString(random))
                    .setN(getRandomString(random))
                    .setR(getRandomBoolean(random));
        }
    }

    public class EventGenerator {
        private EventGenerator() {
        }

        public RecorderProto.Buffer.Builder get() {
            int eventType = random.nextInt(EventTypes.EventType.values().length - 1);
            return get(EventTypes.EventType.forNumber(eventType));
        }

        public List<RecorderProto.Buffer.Builder> get(int count) {
            return generate((Supplier<RecorderProto.Buffer.Builder>) this::get).limit(count).collect(toList());
        }

        public List<RecorderProto.Buffer.Builder> get(int count, EventTypes.EventType eventType) {
            return IntStream.range(0, count).mapToObj(it -> get(eventType)).collect(toList());
        }

        public RecorderProto.Buffer.Builder get(EventTypes.EventType eventType) {
            Events.Event.Builder event = Events.Event.newBuilder()
                    .setTarget(getRandomInt32(random))
                    .setFrameId(getRandomInt32(random));

            switch (eventType) {
                case mousemove:
                case mouseup:
                case mousedown:
                case click:
                    event.setMouseEvent(getMouseEvent());
                    break;
                case scroll:
                    event.setScrollEvent(getScrollEvent());
                    break;
                case windowblur:
                case windowfocus:
                case focus:
                case blur:
                    event.setWindowEvent(getWindowEvent());
                    break;
                case eof:
                    break; //no payload
                case selection:
                    event.setSelectionEvent(getSelectionEvent());
                    break;
                case input:
                case change:
                    event.setChangeEvent(getChangeEvent());
                    break;
                case touchmove:
                case touchstart:
                case touchend:
                case touchcancel:
                case touchforcechange:
                    event.setTouchEvent(getTouchEvent());
                    break;
                case canvasMethod:
                case mediaMethod:
                    event.setMethodEvent(getMethodEvent());
                    break;
                case canvasProperty:
                case mediaProperty:
                    event.setPropertyEvent(getPropertyEvent());
                    break;
                case zoom:
                    event.setZoomEvent(getZoomEvent());
                    break;
                case resize:
                    event.setResizeEvent(getResizeEvent());
                    break;
                case keystroke:
                    event.setKeystrokesEvent(getKeystrokesEvent());
                    break;
                case deviceRotation:
                    event.setDeviceRotationEvent(getDeviceRotationEvent());
                    break;
                case fatalError:
                    event.setFatalErrorEvent(getFatalErrorEvent());
                    break;
                case hashchange:
                    event.setHashchangeEvent(getHashChangeEvent());
                    break;
                case stylechange:
                    event.setStylechangeEvent(getStyleChangeEvent());
                    break;
                default:
                    throw new IllegalArgumentException(eventType.name() + " event is not covered by tests");
            }

            event.setType(eventType);
            return getEmpty().setData(RecorderProto.Wrapper.newBuilder().setEvent(event).build());
        }

        public RecorderProto.Buffer.Builder getEmpty() {
            return RecorderProto.Buffer.newBuilder()
                    .setStamp(getRandomUInt16(random))
                    .setPage(1)
                    .setEnd(true);
        }

        public Events.MouseEvent.Builder getMouseEvent() {
            return Events.MouseEvent.newBuilder()
                    .setX(random.nextInt(4096))
                    .setY(random.nextInt(4096));
        }

        public Events.ScrollEvent.Builder getScrollEvent() {
            return Events.ScrollEvent.newBuilder()
                    .setX(random.nextInt(4096))
                    .setY(random.nextInt(4096))
                    .setPage(getRandomBoolean(random));
        }

        public Events.WindowEvent.Builder getWindowEvent() {
            return Events.WindowEvent.newBuilder();
        }

        public Events.SelectionEvent.Builder getSelectionEvent() {
            return Events.SelectionEvent.newBuilder()
                    .setStart(random.nextInt(4096))
                    .setEnd(random.nextInt(4096))
                    .setStartNode(random.nextInt(4096))
                    .setEndNode(random.nextInt(4096));
        }

        public Events.ChangeEvent.Builder getChangeEvent() {
            return Events.ChangeEvent.newBuilder()
                    .setValue(getRandomString(random))
                    .setChecked(getRandomBoolean(random))
                    .setHidden(getRandomBoolean(random));
        }

        public Events.TouchEvent.SubMeta.Builder getTouchEventSubMeta() {
            return Events.TouchEvent.SubMeta.newBuilder()
                    .setId(getRandomString(random))
                    .setX(getRandomFloat(random) * 4096)
                    .setY(getRandomFloat(random) * 4096)
                    .setForce(getRandomFloat(random));
        }

        public Events.TouchEvent.Builder getTouchEvent() {
            Events.TouchEvent.Builder touches = Events.TouchEvent.newBuilder();
            int touchesNum = random.nextInt(9) + 1;
            for (int i = 0; i < touchesNum; i++) {
                touches.addTouches(getTouchEventSubMeta());
            }
            return touches;
        }

        public Events.ZoomEvent.ZoomPoint.Builder getZoomPoint() {
            return Events.ZoomEvent.ZoomPoint.newBuilder()
                    .setX(random.nextInt(4096))
                    .setY(random.nextInt(4096))
                    .setLevel(getRandomFloat(random));
        }

        public Events.ZoomEvent.Builder getZoomEvent() {
            return Events.ZoomEvent.newBuilder()
                    .setZoomFrom(getZoomPoint())
                    .setZoomTo(getZoomPoint());
        }

        public Events.ResizeEvent.Builder getResizeEvent() {
            return Events.ResizeEvent.newBuilder()
                    .setWidth(random.nextInt(4096))
                    .setHeight(random.nextInt(4096))
                    .setPageWidth(random.nextInt(4096))
                    .setPageHeight(random.nextInt(4096));
        }

        public Events.MethodEvent.Builder getMethodEvent() {
            Events.MethodEvent.Builder builder = Events.MethodEvent.newBuilder()
                    .setMethod(getRandomString(random));
            int args = random.nextInt(9) + 1;
            for (int i = 0; i < args; i++) {
                builder.addArgs(getRandomString(random));
            }
            return builder;
        }

        public Events.PropertyEvent.Builder getPropertyEvent() {
            return Events.PropertyEvent.newBuilder()
                    .setProperty(getRandomString(random))
                    .setValue(getRandomString(random));
        }

        public Events.KeystrokesEvent.KeystrokeEvent.Builder getInnerKeystrokeEvent() {
            return Events.KeystrokesEvent.KeystrokeEvent.newBuilder()
                    .setId(getRandomUInt16(random))
                    .setKey(getRandomString(random))
                    .setIsMeta(getRandomBoolean(random))
                    .setModifier(getRandomString(random));
        }

        public Events.KeystrokesEvent.Builder getKeystrokesEvent() {
            Events.KeystrokesEvent.Builder keystrokes = Events.KeystrokesEvent.newBuilder();
            int events = random.nextInt(19) + 1;
            for (int i = 0; i < events; i++) {
                keystrokes.addKeystrokes(getInnerKeystrokeEvent());
            }
            return keystrokes;
        }

        public Events.DeviceRotationEvent.Builder getDeviceRotationEvent() {
            return Events.DeviceRotationEvent.newBuilder()
                    .setWidth(random.nextInt(4096))
                    .setHeight(random.nextInt(4096))
                    .setOrientation(random.nextInt(4096));
        }

        public Events.FatalErrorEvent.Builder getFatalErrorEvent() {
            return Events.FatalErrorEvent.newBuilder()
                    .setCode(getRandomString(random))
                    .setException(getRandomString(random))
                    .setStack(getRandomString(random));
        }

        public Events.HashchangeEvent.Builder getHashChangeEvent() {
            return Events.HashchangeEvent.newBuilder()
                    .setHash(getRandomString(random));
        }

        public Events.StylechangeEvent.Builder getStyleChangeEvent() {
            return Events.StylechangeEvent.newBuilder()
                    .addChanges(Events.StylechangeRecord.newBuilder()
                            .setTarget(getRandomInt32(random))
                            .setStyle(getRandomString(random))
                            .setOp(getRandomString(random))
                            .setIndex(getRandomInt32(random))
                    );
        }
    }

}
