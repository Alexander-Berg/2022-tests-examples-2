package ru.yandex.quasar.glagoldemoapp.picker

import okhttp3.internal.toHexString
import ru.yandex.quasar.glagol.DeviceId
import ru.yandex.quasar.glagol.DiscoveryResultItem
import java.net.URI
import kotlin.random.Random

class TestDevice : DiscoveryResultItem {

    private val platform: String
    private val deviceId: String
    private val id: DeviceId

    constructor(platform: String, deviceId: String) {
        this.platform = platform
        this.deviceId = deviceId
        id = DeviceId(deviceId, platform)
    }

    constructor() {
        platform = PLATFORMS.random()
        deviceId = Random.nextInt(0, 100000).toHexString()
        id = DeviceId(deviceId, platform)
    }

    override fun getName(): String {
        return "test $platform id=$deviceId"
    }

    override fun getURI(): URI {
        return URI.create("test://some/test")
    }

    override fun isAccessible(): Boolean {
        return true
    }

    override fun getDeviceId(): String {
        return deviceId
    }

    override fun getPlatform(): String {
        return platform
    }

    override fun getId(): DeviceId {
        return id
    }

    override fun getCertificate(): String {
        return "certificate"
    }

    companion object {
        val PLATFORMS = listOf("yandexmini", "yandexstation", "yandexstation2")
    }

    override fun equals(other: Any?): Boolean {
        other?.let {
            it as TestDevice
            return platform == it.platform && name == it.name && id == it.id && deviceId == it.deviceId
        }
        return false
    }
}
