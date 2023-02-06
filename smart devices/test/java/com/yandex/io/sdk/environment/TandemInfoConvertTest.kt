package com.yandex.io.sdk.environment

import android.os.Bundle
import org.hamcrest.Matchers.equalTo
import org.hamcrest.Matchers.nullValue
import org.hamcrest.MatcherAssert.assertThat
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import ru.yandex.quasar.protobuf.ModelObjects.DeviceGroupState

@RunWith(RobolectricTestRunner::class)
class TandemInfoConvertTest {

    @Test
    fun `empty device group state, convert to TandemInfo, got default instance`() {
        val deviceGroupState = DeviceGroupState.newBuilder().build()
        val actualTandemInfo = TandemInfo.from(deviceGroupState)
        val expectedTandemInfo = TandemInfo.getDefaultInstance()
        assertThat(actualTandemInfo, equalTo(expectedTandemInfo))
    }

    @Test
    fun `has no group id, convert to TandemInfo, got unknown group id`() {
        val deviceGroupState = DeviceGroupState.newBuilder().build()

        val actualTandemInfo = TandemInfo.from(deviceGroupState)
        assertThat(actualTandemInfo.groupId, equalTo(TandemInfo.UNKNOWN_GROUP_ID))
    }

    @Test
    fun `has group id, convert to TandemInfo, got the same group id`() {
        val groupId = 42
        val deviceGroupState = DeviceGroupState.newBuilder()
            .setGroupId(groupId)
            .build()

        val actualTandemInfo = TandemInfo.from(deviceGroupState)
        assertThat(actualTandemInfo.groupId, equalTo(groupId))
    }

    @Test
    fun `role is stand alone, convert to TandemInfo, got no paired device`() {
        val deviceGroupState = DeviceGroupState.newBuilder()
            .setLocalRole(DeviceGroupState.Role.STAND_ALONE)
            .setLeader(
                createLeader(DeviceGroupState.ConnectionState.CONNECTED, "platform", "id")
            )
            .setFollower(
                createFollower(DeviceGroupState.ConnectionState.CONNECTED, "platform", "id")
            )
            .build()

        val expectedTandemInfo = TandemInfo(role = TandemRole.STAND_ALONE, pairedDevice = null)
        val actualTandemInfo = TandemInfo.from(deviceGroupState)
        assertThat(actualTandemInfo, equalTo(expectedTandemInfo))
    }

    @Test
    fun `role is follower, convert to TandemInfo, paired device is leader`() {
        val leaderPlatform = "leader_platform"
        val leaderId = "leader_id"
        val deviceGroupState = DeviceGroupState.newBuilder()
            .setLocalRole(DeviceGroupState.Role.FOLLOWER)
            .setLeader(
                createLeader(DeviceGroupState.ConnectionState.CONNECTED, leaderPlatform, leaderId)
            )
            .setFollower(
                createFollower(DeviceGroupState.ConnectionState.CONNECTED, "platform", "id")
            )
            .build()

        val expectedTandemInfo = TandemInfo(
            role = TandemRole.FOLLOWER,
            pairedDevice = createPairedDevice(
                TandemPairedDevice.ConnectionState.CONNECTED,
                leaderPlatform,
                leaderId
            )
        )
        val actualTandemInfo = TandemInfo.from(deviceGroupState)
        assertThat(actualTandemInfo, equalTo(expectedTandemInfo))
    }

    @Test
    fun `role is leader, convert to TandemInfo, paired device is follower`() {
        val followerPlatform = "follower_platform"
        val followerId = "follower_id"
        val deviceGroupState = DeviceGroupState.newBuilder()
            .setLocalRole(DeviceGroupState.Role.LEADER)
            .setLeader(
                createLeader(DeviceGroupState.ConnectionState.CONNECTED, "platform", "id")
            )
            .setFollower(
                createFollower(DeviceGroupState.ConnectionState.CONNECTED, followerPlatform, followerId)
            )
            .build()

        val expectedTandemInfo = TandemInfo(
            role = TandemRole.LEADER,
            pairedDevice = createPairedDevice(
                TandemPairedDevice.ConnectionState.CONNECTED,
                followerPlatform,
                followerId
            )
        )
        val actualTandemInfo = TandemInfo.from(deviceGroupState)
        assertThat(actualTandemInfo, equalTo(expectedTandemInfo))
    }

    @Test
    fun `has role in device group state, convert to TandemInfo, got info with role`() {
        val rolePairs = mapOf(
            DeviceGroupState.Role.STAND_ALONE to TandemRole.STAND_ALONE,
            DeviceGroupState.Role.FOLLOWER to TandemRole.FOLLOWER,
            DeviceGroupState.Role.LEADER to TandemRole.LEADER,
        )

        for (rolePair in rolePairs) {
            val deviceGroupState = DeviceGroupState.newBuilder().setLocalRole(rolePair.key).build()
            val expectedTandemInfo = TandemInfo(role = rolePair.value)
            val actualTandemInfo = TandemInfo.from(deviceGroupState)
            assertThat(actualTandemInfo, equalTo(expectedTandemInfo))
        }
    }

    @Test
    fun `has connection state in leader, convert to PairedDevice, got paired device with connected state`() {
        val connectionStatePairs = mapOf(
            DeviceGroupState.ConnectionState.NONE to TandemPairedDevice.ConnectionState.NONE,
            DeviceGroupState.ConnectionState.CONNECTING to TandemPairedDevice.ConnectionState.CONNECTING,
            DeviceGroupState.ConnectionState.CONNECTED to TandemPairedDevice.ConnectionState.CONNECTED,
        )
        val platform = "some_platform"
        val deviceId = "some_id"

        for (connectionStatePair in connectionStatePairs) {
            val leader = createLeader(connectionStatePair.key, platform, deviceId)
            val expectedLeader = createPairedDevice(connectionStatePair.value, platform, deviceId)
            val actualLeader = TandemPairedDevice.from(leader)
            assertThat(actualLeader, equalTo(expectedLeader))
        }
    }

    @Test
    fun `has connection state in follower, convert to PairedDevice, got paired device with connected state`() {
        val connectionStatePairs = mapOf(
            DeviceGroupState.ConnectionState.NONE to TandemPairedDevice.ConnectionState.NONE,
            DeviceGroupState.ConnectionState.CONNECTING to TandemPairedDevice.ConnectionState.CONNECTING,
            DeviceGroupState.ConnectionState.CONNECTED to TandemPairedDevice.ConnectionState.CONNECTED,
        )
        val platform = "some_platform"
        val deviceId = "some_id"

        for (connectionStatePair in connectionStatePairs) {
            val follower = createFollower(connectionStatePair.key, platform, deviceId)
            val expectedFollower = createPairedDevice(connectionStatePair.value, platform, deviceId)
            val actualFollower = TandemPairedDevice.from(follower)
            assertThat(actualFollower, equalTo(expectedFollower))
        }
    }

    @Test
    fun `empty platform in leader, convert to PairedDevice, got null`() {
        val leader = createLeader(DeviceGroupState.ConnectionState.CONNECTED, "", "some_id")
        val actualLeader = TandemPairedDevice.from(leader)
        assertThat(actualLeader, nullValue())
    }

    @Test
    fun `empty platform in follower, convert to PairedDevice, got null`() {
        val follower = createFollower(DeviceGroupState.ConnectionState.CONNECTED, "", "some_id")
        val actualFollower = TandemPairedDevice.from(follower)
        assertThat(actualFollower, nullValue())
    }

    @Test
    fun `empty device id in leader, convert to PairedDevice, got null`() {
        val leader = createLeader(DeviceGroupState.ConnectionState.CONNECTED, "some_platform", "")
        val actualLeader = TandemPairedDevice.from(leader)
        assertThat(actualLeader, nullValue())
    }

    @Test
    fun `empty device id in follower, convert to PairedDevice, got null`() {
        val follower =
            createFollower(DeviceGroupState.ConnectionState.CONNECTED, "some_platform", "")
        val actualFollower = TandemPairedDevice.from(follower)
        assertThat(actualFollower, nullValue())
    }

    @Test
    fun `null bundle, convert to TandemInfo, got null`() {
        val bundle: Bundle? = null
        val actualTandemInfo = TandemInfo.Factory.fromBundle(bundle)
        assertThat(actualTandemInfo, nullValue())
    }

    @Test
    fun `convert default TandemIndo to bundle, convert TandemIndo from bundle, both values are equals`() {
        val tandemInfoBefore = TandemInfo.getDefaultInstance()
        val bundleTandemInfo = TandemInfo.toBundle(tandemInfoBefore)
        val tandemInfoAfter = TandemInfo.Factory.fromBundle(bundleTandemInfo)
        assertThat(tandemInfoAfter, equalTo(tandemInfoBefore))
    }

    @Test
    fun `convert full TandemIndo to bundle, convert TandemIndo from bundle, both values are equals`() {
        val tandemInfoBefore = TandemInfo(
            groupId = 42,
            role = TandemRole.FOLLOWER,
            pairedDevice = createPairedDevice(
                TandemPairedDevice.ConnectionState.CONNECTED,
                "leader_platform",
                "leader_id"
            ),
        )
        val bundleTandemInfo = TandemInfo.toBundle(tandemInfoBefore)
        val tandemInfoAfter = TandemInfo.Factory.fromBundle(bundleTandemInfo)
        assertThat(tandemInfoAfter, equalTo(tandemInfoBefore))
    }

    private fun createPairedDevice(
        connectionState: TandemPairedDevice.ConnectionState,
        platform: String,
        deviceId: String
    ): TandemPairedDevice {
        return TandemPairedDevice(connectionState, platform, deviceId)
    }

    private fun createLeader(
        connectionState: DeviceGroupState.ConnectionState,
        platform: String,
        deviceId: String
    ): DeviceGroupState.Leader {
        return DeviceGroupState.Leader.newBuilder()
            .setConnectionState(connectionState)
            .setPlatform(platform)
            .setDeviceId(deviceId)
            .build()
    }

    private fun createFollower(
        connectionState: DeviceGroupState.ConnectionState,
        platform: String,
        deviceId: String
    ): DeviceGroupState.Follower {
        return DeviceGroupState.Follower.newBuilder()
            .setConnectionState(connectionState)
            .setPlatform(platform)
            .setDeviceId(deviceId)
            .build()
    }
}
