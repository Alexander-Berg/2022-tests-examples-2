package com.yandex.launcher.updaterapp.contract.events

import android.os.Bundle
import android.os.Parcel
import com.yandex.launcher.updaterapp.BaseRobolectricTest
import com.yandex.launcher.updaterapp.contract.UpdaterContractJson
import com.yandex.launcher.updaterapp.contract.models.CompactDownloadInfo
import com.yandex.launcher.updaterapp.contract.models.Downloadable
import com.yandex.launcher.updaterapp.contract.models.RomUpdate
import com.yandex.launcher.updaterapp.contract.models.Update
import com.yandex.launcher.updaterapp.core.notification.constants.ErrorCode
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.equalTo
import org.hamcrest.Matchers.instanceOf
import org.hamcrest.Matchers.nullValue
import org.json.JSONObject

import org.junit.Test
import kotlin.reflect.full.memberProperties
import kotlin.reflect.full.superclasses
import kotlin.reflect.jvm.javaType

class EventsTest : BaseRobolectricTest() {

    @Test
    fun `write BoxedEvent with VerificationStartedEvent to parcel, should read back same event class`() {
        val update = Update("app", "package", "url", "1.1.1", 1L, 2000L)
        val originalBoxedEvent = BoxedEvent(VerificationStartedEvent(update))

        val eventFromParcel = writeToParcelAndReadBack(originalBoxedEvent).event

        assertThat(eventFromParcel, instanceOf(VerificationStartedEvent::class.java))
    }

    @Test
    fun `write VerificationFailedEvent to parcel, should read back same downloadable`() {
        val originalUpdate = RomUpdate("app", "url", "1.1.1", 1L, 2000L)
        val originalBoxedEvent = BoxedEvent(VerificationFailedEvent(originalUpdate, true, ErrorCode.UNKNOWN))

        val eventFromParcel = writeToParcelAndReadBack(originalBoxedEvent).event as VerificationFailedEvent

        assertThat(eventFromParcel.downloadable, equalTo(originalUpdate))
    }

    @Test
    fun `write VerificationFailedEvent to parcel, should read back all event's fields`() {
        val originalUpdate = RomUpdate("app", "url", "1.1.1", 1L, 2000L)
        val originalBoxedEvent = BoxedEvent(VerificationFailedEvent(originalUpdate, true, ErrorCode.NETWORK_UNAVAILABLE))

        val eventFromParcel = writeToParcelAndReadBack(originalBoxedEvent).event as VerificationFailedEvent

        assertThat(eventFromParcel.downloadable, equalTo(originalUpdate))
        assertThat(eventFromParcel.downloadableInBlockList, equalTo(true))
    }

    @Test
    fun `writeToParcelAndReadBack returns different instances`() {
        val originalBoxedEvent = BoxedEvent(DownloadProgressChangeEvent(listOf(CompactDownloadInfo("url", "name", "requestName", 100, 50))))
        val boxedEventFromParcel = writeToParcelAndReadBack(originalBoxedEvent)

        assertThat(originalBoxedEvent !== boxedEventFromParcel, equalTo(true))
    }

    @Test
    fun `read from parcel BoxedEvent with bad json, event should be null`() {
        //part of [BoxedEvent.writeToParcel]
        val bundle = Bundle()
        bundle.putString(BoxedEvent.KEY_EVENT, "BadJson")

        val parcel = Parcel.obtain()
        parcel.writeBundle(bundle)

        val originalBytes = parcel.marshall()
        val newParcel = Parcel.obtain()
        newParcel.unmarshall(originalBytes, 0, originalBytes.size)
        newParcel.setDataPosition(0)

        val newBoxedEvent = BoxedEvent.CREATOR.createFromParcel(newParcel)

        assertThat(newBoxedEvent.event, nullValue())
    }

    @Test
    fun `read from parcel BoxedEvent with Unknown event, event should be null`() {

        val update = Update("app", "package", "url", "2", 2)
        val json = JSONObject(UpdaterContractJson.toJson(UpdatedEvent(update)))
            .put(UpdaterContractJson.GSON_TYPE_LABEL, "-100") // put unknown event type label vale
            .toString()

        //part of [BoxedEvent.writeToParcel]
        val bundle = Bundle()
        bundle.putString(BoxedEvent.KEY_EVENT, json)

        val parcel = Parcel.obtain()
        parcel.writeBundle(bundle)

        val originalBytes = parcel.marshall()
        val newParcel = Parcel.obtain()
        newParcel.unmarshall(originalBytes, 0, originalBytes.size)
        newParcel.setDataPosition(0)

        val newBoxedEvent = BoxedEvent.CREATOR.createFromParcel(newParcel)

        assertThat(newBoxedEvent.event, nullValue())
    }

    @Test
    fun `all BaseEvent subclasses should be registered in TypeAdapterFactory`() {
        val sealedSubclasses = BaseEvent::class.sealedSubclasses

        assertThat("BaseEvent should have sealedSubclasses", sealedSubclasses.isEmpty(), equalTo(false))

        val registeredSubtypes = UpdaterContractJson.typeAdapterFactoryBaseEvent.subtypeToLabel

        val notRegisteredSubclasses = sealedSubclasses
            .filter { clazz -> !registeredSubtypes.containsKey(clazz.java) }

        val formattedClasses = notRegisteredSubclasses.joinToString(", ", transform = { it.java.simpleName })
        assertThat(
            "Found BaseEvent subclasses not registered in UpdaterContract.gson=$formattedClasses",
            notRegisteredSubclasses.isEmpty(), equalTo(true)
        )
    }

    @Test
    fun `all BaseEvent subclasses with 'downloadable' field should be marked with IContainsDownloadable`() {
        val sealedSubclasses = BaseEvent::class.sealedSubclasses

        sealedSubclasses.forEach { clazz ->
            clazz.memberProperties.forEach { property ->
                if (property.name == "downloadable" && property.returnType.javaType.typeName == Downloadable::class.java.typeName) {
                    assertThat(
                        "Class=${clazz.java.simpleName} contains downloadable: Downloadable but not marked as IContainsDownloadable",
                        clazz.superclasses.contains(IContainsDownloadable::class), equalTo(true)
                    )
                }
            }
        }
    }
}

private fun writeToParcelAndReadBack(originalBoxedEvent: BoxedEvent): BoxedEvent {
    val parcel = Parcel.obtain()
    originalBoxedEvent.writeToParcel(parcel, 0)

    val originalBytes = parcel.marshall()
    val newParcel = Parcel.obtain()
    newParcel.unmarshall(originalBytes, 0, originalBytes.size)
    newParcel.setDataPosition(0)

    return BoxedEvent.CREATOR.createFromParcel(newParcel)
}
