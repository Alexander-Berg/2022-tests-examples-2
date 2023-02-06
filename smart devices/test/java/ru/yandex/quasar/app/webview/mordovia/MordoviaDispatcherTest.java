package ru.yandex.quasar.app.webview.mordovia;

import org.assertj.core.api.Assertions;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mockito;
import org.robolectric.RobolectricTestRunner;
import org.robolectric.shadows.ShadowLooper;

import java.util.Arrays;
import java.util.concurrent.TimeUnit;

import androidx.annotation.NonNull;
import androidx.core.util.Consumer;
import edu.emory.mathcs.backport.java.util.Collections;

@SuppressWarnings("unchecked")
@RunWith(RobolectricTestRunner.class)
public class MordoviaDispatcherTest {

    // effectively @NonNull
    private MordoviaPage page;

    // effectively @NonNull
    private MordoviaDispatcher dispatcher;

    @NonNull
    private final MordoviaCommand c0 = new MordoviaCommand("c0", null, null, null);

    @NonNull
    private final MordoviaCommand c1 = new MordoviaCommand("c1", null, null, null);

    @NonNull
    private final MordoviaCommand c2 = new MordoviaCommand("c2", null, null, null);

    @Before
    public void runBeforeAnyTest() {
        page = Mockito.mock(MordoviaPage.class);

        dispatcher = new MordoviaDispatcher(page, 1000);
    }

    @Test
    public void dispatcher_shouldSendCommand_inIdleState() {
        Assertions.assertThat(dispatcher.getState()).isEqualTo(MordoviaDispatcher.STATE_INIT);

        dispatcher.notifyPageReady();

        Assertions.assertThat(dispatcher.getState()).isEqualTo(MordoviaDispatcher.STATE_IDLE);

        dispatcher.submit(c0);

        Assertions.assertThat(dispatcher.getState()).isEqualTo(MordoviaDispatcher.STATE_BUSY);
        Mockito.verify(page).runCommands(Mockito.eq(Collections.singletonList(c0)), Mockito.any());
    }

    @Test
    public void dispatcher_shouldBufferCommands_inInitState() {
        Assertions.assertThat(dispatcher.getState()).isEqualTo(MordoviaDispatcher.STATE_INIT);

        dispatcher.submit(c0);

        Assertions.assertThat(dispatcher.getState()).isEqualTo(MordoviaDispatcher.STATE_INIT);
        Mockito.verify(page, Mockito.never()).runCommands(Mockito.eq(Collections.singletonList(c0)), Mockito.any());

        dispatcher.submit(c1);

        Assertions.assertThat(dispatcher.getState()).isEqualTo(MordoviaDispatcher.STATE_INIT);
        Mockito.verify(page, Mockito.never()).runCommands(Mockito.eq(Collections.singletonList(c1)), Mockito.any());
        Mockito.verify(page, Mockito.never()).runCommands(Mockito.eq(Arrays.asList(c0, c1)), Mockito.any());

        dispatcher.notifyPageReady();

        Assertions.assertThat(dispatcher.getState()).isEqualTo(MordoviaDispatcher.STATE_BUSY);
        Mockito.verify(page).runCommands(Mockito.eq(Arrays.asList(c0, c1)), Mockito.any());
    }

    @Test
    public void dispatcher_shouldNotSendCommands_inSendingState() {
        Assertions.assertThat(dispatcher.getState()).isEqualTo(MordoviaDispatcher.STATE_INIT);

        dispatcher.notifyPageReady();

        Assertions.assertThat(dispatcher.getState()).isEqualTo(MordoviaDispatcher.STATE_IDLE);

        dispatcher.submit(c0);

        Assertions.assertThat(dispatcher.getState()).isEqualTo(MordoviaDispatcher.STATE_BUSY);
        Mockito.verify(page, Mockito.never()).runCommands(Mockito.eq(Collections.singletonList(c1)), Mockito.any());
        Mockito.verify(page, Mockito.never()).runCommands(Mockito.eq(Arrays.asList(c0, c1)), Mockito.any());
    }

    @Test
    public void dispatcher_shouldReturnToIdleState_ifCallbackWasCalled() {
        dispatcher.notifyPageReady();

        ArgumentCaptor<Consumer<Boolean>> captor = ArgumentCaptor.forClass(Consumer.class);

        dispatcher.submit(c0);

        Assertions.assertThat(dispatcher.getState()).isEqualTo(MordoviaDispatcher.STATE_BUSY);
        Mockito.verify(page).runCommands(Mockito.eq(Collections.singletonList(c0)), captor.capture());

        captor.getValue().accept(true);
        ShadowLooper.runUiThreadTasks();

        Assertions.assertThat(dispatcher.getState()).isEqualTo(MordoviaDispatcher.STATE_IDLE);
    }

    @Test
    public void dispatcher_shouldReturnToIdleState_ifCallbackWasNotCalledOnTime() {
        dispatcher.notifyPageReady();
        dispatcher.submit(c0);
        ShadowLooper.idleMainLooper(5, TimeUnit.SECONDS);
        ShadowLooper.runUiThreadTasks();
        Assertions.assertThat(dispatcher.getState()).isEqualTo(MordoviaDispatcher.STATE_IDLE);
    }

    @Test
    public void dispatcher_shouldNotSendCommandTwice_whenSuccess() {
        dispatcher.notifyPageReady();

        ArgumentCaptor<Consumer<Boolean>> captor = ArgumentCaptor.forClass(Consumer.class);

        dispatcher.submit(c0);

        Mockito.verify(page).runCommands(Mockito.eq(Collections.singletonList(c0)), captor.capture());
        captor.getValue().accept(true);
        Mockito.reset(page);

        dispatcher.notifyPageReady();

        Mockito.verify(page, Mockito.never()).runCommands(Mockito.any(), Mockito.any());
    }

    @Test
    public void dispatcher_shouldRetryToSendCommand_whenFailureAndGotNewCommand() {
        dispatcher.notifyPageReady();

        ArgumentCaptor<Consumer<Boolean>> captor = ArgumentCaptor.forClass(Consumer.class);

        dispatcher.submit(c0);

        Mockito.verify(page).runCommands(Mockito.eq(Collections.singletonList(c0)), captor.capture());

        dispatcher.submit(c1);
        captor.getValue().accept(false);

        Mockito.verify(page).runCommands(Mockito.eq(Arrays.asList(c0, c1)), Mockito.any());
    }

    @Test
    public void dispatcher_shouldRetryToSendCommand_whenFailureAndReadyWasCalled() {
        dispatcher.notifyPageReady();

        ArgumentCaptor<Consumer<Boolean>> captor = ArgumentCaptor.forClass(Consumer.class);

        dispatcher.submit(c0);

        Mockito.verify(page).runCommands(Mockito.eq(Collections.singletonList(c0)), captor.capture());

        dispatcher.notifyPageReady();
        captor.getValue().accept(false);

        Mockito.verify(page, Mockito.times(2)).runCommands(Mockito.eq(Collections.singletonList(c0)), Mockito.any());
    }

    @Test
    public void dispatcher_shouldNotRetryToSendCommand_whenFailureAndNothingElseHappened() {
        dispatcher.notifyPageReady();

        ArgumentCaptor<Consumer<Boolean>> captor = ArgumentCaptor.forClass(Consumer.class);

        dispatcher.submit(c0);

        Mockito.verify(page).runCommands(Mockito.eq(Collections.singletonList(c0)), captor.capture());
        Mockito.reset(page);

        captor.getValue().accept(false);

        Mockito.verify(page, Mockito.never()).runCommands(Mockito.any(), Mockito.any());
    }

    @Test
    public void dispatcher_shouldResendCommandsInCorrectOrder_whenFailure() {
        dispatcher.notifyPageReady();

        ArgumentCaptor<Consumer<Boolean>> captor = ArgumentCaptor.forClass(Consumer.class);
        dispatcher.submit(c0);
        dispatcher.submit(c1);
        Mockito.verify(page).runCommands(Mockito.eq(Collections.singletonList(c0)), captor.capture());
        dispatcher.submit(c2);

        captor.getValue().accept(false);
        dispatcher.notifyPageReady();

        Mockito.verify(page).runCommands(Mockito.eq(Arrays.asList(c0, c1, c2)), Mockito.any());
    }

    @Test
    public void dispatcher_shouldNotSendOutdatedCommands() {
        dispatcher = new MordoviaDispatcher(page, 0);
        dispatcher.submit(c0);
        dispatcher.notifyPageReady();
        Assertions.assertThat(dispatcher.getState()).isEqualTo(MordoviaDispatcher.STATE_IDLE);
        Mockito.verify(page, Mockito.never()).runCommands(Mockito.any(), Mockito.any());
    }
}
