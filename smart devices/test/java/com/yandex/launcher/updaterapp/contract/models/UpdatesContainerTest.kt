package com.yandex.launcher.updaterapp.contract.models

import android.os.Parcel
import com.yandex.launcher.updaterapp.BaseRobolectricTest
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.equalTo
import org.junit.Test

class UpdatesContainerTest : BaseRobolectricTest() {

    @Test
    fun `should restore RomUpdate from parcel`() {
        val originalRomUpdate = RomUpdate("-", "http", "1.1.1", 100)
        val container = UpdatesContainer(romUpdate = originalRomUpdate)

        val copyContainer = writeToParcelAndReadBack(container)
        assertThat(copyContainer.romUpdate, equalTo(originalRomUpdate))
    }

    @Test
    fun `should restore Updates from parcel`() {
        val container = UpdatesContainer(
            listOf(
                Update("app", "package1", "url", "100", 100),
                Update("app", "package2", "url", "100", 100)
            )
        )

        val copyContainer = writeToParcelAndReadBack(container)

        repeat(container.updates.size) { index ->
            assertThat(copyContainer.updates[index], equalTo(container.updates[index]))
        }
    }

    @Test
    fun `writeToParcelAndReadBack returns different instances`() {
        val originalRomUpdate = RomUpdate("-", "http", "1.1.1", 100)
        val container = UpdatesContainer(listOf(Update("app", "package", "url", "1", 100)), romUpdate = originalRomUpdate)

        val copyContainer = writeToParcelAndReadBack(container)

        assertThat(copyContainer !== container, equalTo(true))
    }
}

private fun writeToParcelAndReadBack(container: UpdatesContainer): UpdatesContainer {
    val parcel = Parcel.obtain()
    container.writeToParcel(parcel, 0)

    val originalBytes = parcel.marshall()
    val newParcel = Parcel.obtain()
    newParcel.unmarshall(originalBytes, 0, originalBytes.size)
    newParcel.setDataPosition(0)

    return UpdatesContainer.CREATOR.createFromParcel(newParcel)
}
