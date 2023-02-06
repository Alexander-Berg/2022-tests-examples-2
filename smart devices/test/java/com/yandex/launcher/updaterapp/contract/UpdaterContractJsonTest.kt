package com.yandex.launcher.updaterapp.contract

import com.yandex.launcher.updaterapp.BaseRobolectricTest
import com.yandex.launcher.updaterapp.contract.events.BaseEvent
import com.yandex.launcher.updaterapp.contract.events.NetworkUnavailableEvent
import com.yandex.launcher.updaterapp.contract.models.Downloadable
import com.yandex.launcher.updaterapp.contract.models.RomUpdate
import com.yandex.launcher.updaterapp.contract.models.Update
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers
import org.hamcrest.Matchers.notNullValue
import org.hamcrest.Matchers.nullValue
import org.json.JSONObject
import org.junit.Test

class UpdaterContractJsonTest : BaseRobolectricTest() {

    @Test
    fun `serialize Update to Json, should deserialize back`() {
        val update: Downloadable = Update("app", "package", "url", "1", 100, 1000)
        val json = UpdaterContractJson.toJson(update)
        val copyUpdate = UpdaterContractJson.fromJson<Downloadable>(json)
        assertThat(update, Matchers.equalTo(copyUpdate))
    }

    @Test
    fun `serialize RomUpdate to Json, should deserialize back`() {
        val update: Downloadable = RomUpdate("app", "url", "1", 100, 1000)
        val json = UpdaterContractJson.toJson(update)
        val copyUpdate = UpdaterContractJson.fromJson<Downloadable>(json)
        assertThat(update, Matchers.equalTo(copyUpdate))
    }

    @Test
    fun `RomUpdate registered in UpdaterContract TypeAdapterFactory`() {
        assertThat(UpdaterContractJson.typeAdapterFactoryDownloadable.subtypeToLabel.containsKey(RomUpdate::class.java), Matchers.equalTo(true))
    }

    @Test
    fun `Update registered in UpdaterContract TypeAdapterFactory`() {
        assertThat(UpdaterContractJson.typeAdapterFactoryDownloadable.subtypeToLabel.containsKey(Update::class.java), Matchers.equalTo(true))
    }

    @Test
    fun `UpdaterContract toJson uses puts 'type_label' for Downloadable`() {

        val json = UpdaterContractJson.toJson<Downloadable>(Update("app", "package", "-", "", 1))
        val typeLabel = JSONObject(json).optString(UpdaterContractJson.GSON_TYPE_LABEL)

        assertThat(typeLabel.isNotEmpty(), Matchers.equalTo(true))
    }

    @Test
    fun `UpdaterContract toJson uses puts 'type_label' for BaseEvent`() {

        val json = UpdaterContractJson.toJson<BaseEvent>(NetworkUnavailableEvent(1))
        val typeLabel = JSONObject(json).optString(UpdaterContractJson.GSON_TYPE_LABEL)

        assertThat(typeLabel.isNotEmpty(), Matchers.equalTo(true))
    }

    @Test
    fun `serialize RomUpdate to json, should deserialize`() {
        val original: Downloadable = RomUpdate("app", "url", "1.1.1", 1L, 2000L)

        val json: String = UpdaterContractJson.toJson(original)
        val copy: Downloadable? = UpdaterContractJson.fromJson(json)

        assertThat(original, Matchers.equalTo(copy))
    }

    @Test
    fun `serialize Update to json, should deserialize`() {
        val original: Downloadable = Update("app", "package", "url", "1.1.1", 1L, 2000L)

        val json: String = UpdaterContractJson.toJson(original)
        val copy: Downloadable? = UpdaterContractJson.fromJson(json)

        assertThat(original, Matchers.equalTo(copy))
    }

    @Test
    fun `romUpdate should deserialize from json`() {
        val json = """{
    "appName": "app",
    "packageName": "rom_update",
    "downloadUrl": "url",
    "versionName": "1.1.1",
    "versionCode": 1,
    "size": 2000,
    "localPath": "",
    "installPriority": "NORMAL"
}"""
        val downloadable: RomUpdate? = UpdaterContractJson.fromJson(json)

        assertThat(downloadable, notNullValue())
    }

    @Test
    fun `romUpdate should not deserialize from json with missing size`() {
        val json = """{
    "appName": "app",
    "packageName": "rom_update",
    "downloadUrl": "url",
    "versionCode": 1,
    "size": 2000,
    "localPath": "",
    "installPriority": "NORMAL"
}"""
        val downloadable: RomUpdate? = UpdaterContractJson.fromJson(json)

        assertThat(downloadable, nullValue())
    }
}
