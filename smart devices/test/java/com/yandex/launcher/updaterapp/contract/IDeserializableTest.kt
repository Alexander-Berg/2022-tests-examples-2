package com.yandex.launcher.updaterapp.contract

import com.yandex.launcher.updaterapp.BaseRobolectricTest
import com.yandex.launcher.updaterapp.contract.models.RomUpdate
import com.yandex.launcher.updaterapp.contract.models.Update
import org.junit.Test
import java.lang.RuntimeException

class IDeserializableTest : BaseRobolectricTest() {

    @Test
    fun `newly created RomUpdate, checkStructureConsistency should not throw`() {
        val romUpdate = RomUpdate("rom", "package", "1", 1)
        romUpdate.checkStructureConsistency()
    }

    @Test(expected = CheckStructureConsistencyException::class)
    fun `deserialize RomUpdate from json with missing size, checkStructureConsistency should throw`() {
        val json = """{
    "appName": "rom",
    "packageName": "rom.package",
    "downloadUrl": "url",
    "versionCode": 1,
    "localPath": "",
    "installPriority": "NORMAL"
}"""
        val romUpdate = UpdaterContractJson.gson.fromJson(json, RomUpdate::class.java)!!

        kotlin.runCatching {
            romUpdate.checkStructureConsistency()
        }.onFailure { throw CheckStructureConsistencyException() }
    }

    @Test
    fun `newly created Update, checkStructureConsistency should not throw`() {
        val update = Update("app", "package", "url", "1", 1)
        update.checkStructureConsistency()
    }

    @Test(expected = CheckStructureConsistencyException::class)
    fun `deserialize Update from json with missing size, checkStructureConsistency should throw`() {
        val json = """{
    "appName": "app",
    "packageName": "app.package",
    "downloadUrl": "url",
    "versionCode": 1,
    "localPath": "",
    "installPriority": "NORMAL"
}"""
        val update = UpdaterContractJson.gson.fromJson(json, Update::class.java)!!

        kotlin.runCatching {
            update.checkStructureConsistency()
        }.onFailure { throw CheckStructureConsistencyException() }
    }

    class CheckStructureConsistencyException : RuntimeException()
}
