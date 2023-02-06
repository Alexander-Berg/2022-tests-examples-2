package ru.yandex.quasar.glagol

import java.net.URI

class DiscoveryResultItemDummy(
    private val dummyName: String,
    private val id: String,
    private val platform: String,
    private var uriStr: String = "wss://192.1.2.3:123",
    private val isAccessible: Boolean = true,
    private val certificate: String? = null,
) : DiscoveryResultItem {

    override fun getName() = dummyName

    override fun getURI() = URI.create(uriStr)

    override fun isAccessible() = isAccessible

    override fun getDeviceId() = id

    override fun getPlatform() = platform

    override fun getId() = DeviceId(id, platform)

    override fun getStereoPairRole(): StereoPairRole? = null

    override fun getCertificate() = certificate

    override fun getServiceName() = "servicetype.io-$dummyName"
}
