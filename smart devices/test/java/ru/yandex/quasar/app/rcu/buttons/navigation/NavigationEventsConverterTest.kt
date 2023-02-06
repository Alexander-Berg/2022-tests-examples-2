package ru.yandex.quasar.app.rcu.buttons.navigation

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import ru.yandex.quasar.protobuf.ModelObjects.ControlRequest
import ru.yandex.quasar.protobuf.ModelObjects.EmptyMessage
import ru.yandex.quasar.protobuf.ModelObjects.NavigationMessage
import ru.yandex.quasar.protobuf.ModelObjects.NavigationRequest

class NavigationEventsConverterTest {
    @Test
    fun when_navigationTypeIsAction_then_returnActionRequest() {
        val navigationType = NavigationType.ACTION
        val controlRequest = NavigationEventsConverter.convert(navigationType)

        assertTrue(controlRequest.hasOrigin())
        assertEquals(controlRequest.origin, ControlRequest.Origin.TOUCH)
        assertTrue(controlRequest.hasActionRequest())
    }

    @Test
    fun when_navigationTypeIsGoLeft_then_returnGoLeftRequest() {
        val navigationType = NavigationType.GO_LEFT
        val expectedNavigationRequest = NavigationRequest
            .newBuilder()
            .setGoLeft(
                NavigationMessage.newBuilder()
                    .setVisualMode(EmptyMessage.getDefaultInstance())
            )
            .build()

        val controlRequest = NavigationEventsConverter.convert(navigationType)

        assertTrue(controlRequest.hasOrigin())
        assertEquals(controlRequest.origin, ControlRequest.Origin.TOUCH)
        assertEquals(expectedNavigationRequest, controlRequest.navigationRequest)
    }

    @Test
    fun when_navigationTypeIsGoRight_then_returnGoRightRequest() {
        val navigationType = NavigationType.GO_RIGHT
        val expectedNavigationRequest = NavigationRequest
            .newBuilder()
            .setGoRight(
                NavigationMessage.newBuilder()
                    .setVisualMode(EmptyMessage.getDefaultInstance())
            )
            .build()

        val controlRequest = NavigationEventsConverter.convert(navigationType)

        assertTrue(controlRequest.hasOrigin())
        assertEquals(controlRequest.origin, ControlRequest.Origin.TOUCH)
        assertEquals(expectedNavigationRequest, controlRequest.navigationRequest)
    }

    @Test
    fun when_navigationTypeIsGoDown_then_returnGoDownRequest() {
        val navigationType = NavigationType.GO_DOWN
        val expectedNavigationRequest = NavigationRequest
            .newBuilder()
            .setGoDown(
                NavigationMessage.newBuilder()
                    .setVisualMode(EmptyMessage.getDefaultInstance())
            )
            .build()

        val controlRequest = NavigationEventsConverter.convert(navigationType)

        assertTrue(controlRequest.hasOrigin())
        assertEquals(controlRequest.origin, ControlRequest.Origin.TOUCH)
        assertEquals(expectedNavigationRequest, controlRequest.navigationRequest)
    }

    @Test
    fun when_navigationTypeIsGoUp_then_returnGoUpRequest() {
        val navigationType = NavigationType.GO_UP
        val expectedNavigationRequest = NavigationRequest
            .newBuilder()
            .setGoUp(
                NavigationMessage.newBuilder()
                    .setVisualMode(EmptyMessage.getDefaultInstance())
            )
            .build()

        val controlRequest = NavigationEventsConverter.convert(navigationType)

        assertTrue(controlRequest.hasOrigin())
        assertEquals(controlRequest.origin, ControlRequest.Origin.TOUCH)
        assertEquals(expectedNavigationRequest, controlRequest.navigationRequest)
    }
}
