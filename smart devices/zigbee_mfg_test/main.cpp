#include "ezsp_mfg_channel.h"
#include "telink_mfg_channel.h"

#include <smart_devices/libs/pcba/pcba_ids.h>

#include <yandex_io/libs/base/utils.h>
#include <yandex_io/libs/json_utils/json_utils.h>
#include <yandex_io/libs/logging/logging.h>
#include <yandex_io/libs/logging/setup/setup.h>
#include <yandex_io/libs/terminate_waiter/terminate_waiter.h>

#include <library/cpp/getopt/small/last_getopt.h>
#include <library/cpp/getopt/small/modchooser.h>

#include <util/generic/cast.h>
#include <util/random/random.h>

#include <fstream>
#include <iomanip>

YIO_DEFINE_LOG_MODULE("zigbee");

namespace {

    const std::string PCBA_IDS_PATH = "/sys/devices/platform/pcba_ids/pcba_ids_drv/pcba_ids";
    const std::string PCBA_TOPLED = "topled";

    enum class ZigbeeModuleType: char {
        MGM210PA22JIA2 = '0',
        MGM210PA32JIA2 = '1',
        SZMG21_31A1 = '2',
        SZMG21_27A3 = '3',
        TZ9218_27A1 = '4',
    };

    std::optional<ZigbeeModuleType> getZigbeeModuleType() {
        auto pcbaIds = quasar::loadPCBAIds(PCBA_IDS_PATH);

        if (!pcbaIds || !pcbaIds->hasPCBA(PCBA_TOPLED)) {
            return std::nullopt;
        }

        const auto& topled = pcbaIds->getPCBA(PCBA_TOPLED);

        if (topled.assembly.size() < 2) {
            return std::nullopt;
        }

        return static_cast<ZigbeeModuleType>(topled.assembly[1]);
    }

    constexpr uint32_t TEST_REQUEST_MAGIC = 0x7354a637;
    constexpr uint32_t TEST_RESPONSE_MAGIC = 0x54aa99d7;

    struct TestFrame {
        uint32_t macHeader = 0;
        uint32_t magic;
        uint32_t sessionId;
        uint32_t packetId;
        uint32_t value;
        uint8_t lqi;
        int8_t rssi;
    };

    enum class TestFrameStatus {
        LOST = 0,
        OK,
        CORRUPTED, // should never happen
        UNKNOWN,
    };

    struct TestFrameInfo {
        TestFrameStatus status;
        uint32_t value;
        uint8_t rxLqi;
        int8_t rxRssi;
        uint8_t txLqi;
        int8_t txRssi;
    };

    class MfgTestBase
        : public TMainClassArgs,
          public IMfgChannel::IListener,
          public std::enable_shared_from_this<MfgTestBase> {
    public:
        MfgTestBase()
        {
        }

    protected:
        void RegisterOptions(NLastGetopt::TOpts& opts) override {
            opts.AddHelpOption('h');
            opts.AddLongOption("port", "TTY port")
                .Required()
                .StoreResult(&port_);
            opts.AddLongOption("channel", "radio channel")
                .Optional()
                .StoreResult(&channel_)
                .DefaultValue(11);
            opts.AddLongOption("power", "transmit power in dBm")
                .Optional()
                .StoreResult(&power_)
                .DefaultValue(0);
            opts.AddLongOption("session", "unique session ID")
                .Required()
                .StoreResult(&sessionId_);
            opts.AddLongOption('v', "verbose", "enable verbose output")
                .Optional()
                .NoArgument()
                .SetFlag(&verbose_);
        }

        int DoRun(NLastGetopt::TOptsParseResult&& /* options */) override {
            quasar::Logging::initLoggingToStdout(verbose_ ? "debug" : "info", "%+");

            setup();

            auto moduleType = getZigbeeModuleType();
            if (!moduleType) {
                YIO_LOG_ERROR_EVENT("MfgTestClient.BadZigbeeModuleType", "Failed to get Zigbee module type");
                return 1;
            }

            YIO_LOG_INFO("Zigbee module type: " << ToUnderlying(*moduleType));

            switch (*moduleType) {
                case ZigbeeModuleType::MGM210PA22JIA2:
                case ZigbeeModuleType::MGM210PA32JIA2:
                    YIO_LOG_INFO("Using EZSP implementation");
                    mfg_ = std::make_shared<EzspMfgChannel>(port_);
                    break;
                case ZigbeeModuleType::TZ9218_27A1:
                    YIO_LOG_INFO("Using Telink implementation");
                    mfg_ = std::make_shared<TelinkMfgChannel>(port_);
                    break;
                default:
                    YIO_LOG_ERROR_EVENT("MfgTestClient.BadZigbeeModuleType", "Unsupported Zigbee module type");
                    return 1;
            }

            mfg_->start(shared_from_this());

            try {
                eui64_ = mfg_->getEui64();
                YIO_LOG_INFO("EUI64: " << quasar::Hex(eui64_));
            } catch (const std::exception& e) {
                YIO_LOG_WARN("Failed to get EUI64: " << e.what());
            }

            mfg_->setChannel(channel_);

            mfg_->setPower(power_);

            run();

            mfg_->stop();

            teardown();

            return 0;
        }

        virtual void setup() {
        }
        virtual void run() = 0;
        virtual void teardown() {
        }

        virtual void handleTestFrame(TestFrame frame, uint8_t lqi, int8_t rssi) = 0;

    private:
        void onPacketReceived(uint8_t lqi, int8_t rssi, const std::vector<uint8_t>& payload) override {
            if (payload.size() != sizeof(TestFrame)) {
                YIO_LOG_DEBUG("Unexpected packet size, skipping");
                return;
            }

            TestFrame frame;
            memcpy(&frame, payload.data(), sizeof(frame));

            handleTestFrame(frame, lqi, rssi);
        }

    protected:
        std::shared_ptr<IMfgChannel> mfg_;
        IMfgChannel::Eui64 eui64_;

        std::string port_;
        uint8_t channel_;
        int8_t power_;
        uint32_t sessionId_;
        bool verbose_;
    };

    class MfgTestServer: public MfgTestBase {
    protected:
        void run() override {
            YIO_LOG_INFO("Listening for test frames on channel " << (uint32_t)channel_);
            waiter_.wait();
        }

        void handleTestFrame(TestFrame frame, uint8_t lqi, int8_t rssi) override {
            if (frame.magic != TEST_REQUEST_MAGIC) {
                YIO_LOG_DEBUG("Wrong magic, skipping");
                return;
            }

            YIO_LOG_DEBUG("Got test request: " << frame.sessionId << " " << frame.packetId << " " << frame.value);

            if (frame.sessionId != sessionId_) {
                YIO_LOG_DEBUG("Wrong session ID, skipping");
                return;
            }

            frame.magic = TEST_RESPONSE_MAGIC;
            frame.lqi = lqi;
            frame.rssi = rssi;

            std::vector<uint8_t> data{(uint8_t*)&frame, (uint8_t*)&frame + sizeof(frame)};

            YIO_LOG_DEBUG("Sending test reply");

            mfg_->sendPacket(data);
        }

    private:
        quasar::TerminateWaiter waiter_;
    };

    class MfgTestClient: public MfgTestBase {
    protected:
        void RegisterOptions(NLastGetopt::TOpts& opts) override {
            MfgTestBase::RegisterOptions(opts);

            opts.AddLongOption("num", "number of packets to send")
                .Optional()
                .StoreResult(&packetNumber_)
                .DefaultValue(0);
            opts.AddLongOption("wait", "seconds to wait for response frames")
                .Optional()
                .StoreResult(&timeout_)
                .DefaultValue(5);
            opts.AddLongOption("report", "path to test report")
                .Optional()
                .StoreResult(&reportPath_);
        }

        void setup() override {
            frames_.resize(packetNumber_);

            for (size_t i = 0; i < packetNumber_; i++) {
                auto& frame = frames_[i];
                frame.status = TestFrameStatus::UNKNOWN;
                frame.value = RandomNumber<uint32_t>();
                frame.rxLqi = 0;
                frame.rxRssi = 0;
                frame.txLqi = 0;
                frame.txRssi = 0;
            }
        }

        void run() override {
            TestFrame frame = {};
            frame.magic = TEST_REQUEST_MAGIC;
            frame.sessionId = sessionId_;

            const auto timePerFrame = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::seconds(timeout_)) / frames_.size();

            YIO_LOG_INFO("Sending " << packetNumber_ << " packets on channel " << (uint32_t)channel_ << " waiting max " << timePerFrame.count() << " milliseconds per frame");
            for (size_t i = 0; i < packetNumber_; i++) {
                frame.packetId = i;
                frame.value = frames_[i].value;

                std::vector<uint8_t> data{(uint8_t*)&frame, (uint8_t*)&frame + sizeof(frame)};

                YIO_LOG_DEBUG("Sending packet " << frame.packetId << " with value " << frame.value);
                {
                    std::unique_lock<std::mutex> lk(mutex_);

                    mfg_->sendPacket(data);

                    YIO_LOG_INFO("Waiting for response");
                    cv_.wait_for(lk, timePerFrame, [&] { return frames_[i].status != TestFrameStatus::UNKNOWN; });
                    if (frames_[i].status == TestFrameStatus::UNKNOWN) {
                        frames_[i].status = TestFrameStatus::LOST;
                    }
                }
            }
        }

        void teardown() override {
            Json::Value report;
            report["channel"] = channel_;
            report["power"] = power_;
            report["session"] = sessionId_;
            report["eui64"] = HexEncode(eui64_.data(), eui64_.size());

            Json::Value& frames = report["frames"];
            frames.resize(frames_.size());

            size_t errors = 0;

            uint8_t minRxLqi = std::numeric_limits<uint8_t>::max();
            uint8_t maxRxLqi = std::numeric_limits<uint8_t>::min();
            uint32_t sumRxLqi = 0;

            int8_t minRxRssi = std::numeric_limits<int8_t>::max();
            int8_t maxRxRssi = std::numeric_limits<int8_t>::min();
            int32_t sumRxRssi = 0;

            uint8_t minTxLqi = std::numeric_limits<uint8_t>::max();
            uint8_t maxTxLqi = std::numeric_limits<uint8_t>::min();
            uint32_t sumTxLqi = 0;

            int8_t minTxRssi = std::numeric_limits<int8_t>::max();
            int8_t maxTxRssi = std::numeric_limits<int8_t>::min();
            int32_t sumTxRssi = 0;

            for (size_t i = 0; i < frames_.size(); i++) {
                const auto& frame = frames_[i];

                auto& reportFrame = frames[(Json::ArrayIndex)i];
                reportFrame["ok"] = (frame.status == TestFrameStatus::OK);
                reportFrame["rxLqi"] = frame.rxLqi;
                reportFrame["rxRssi"] = frame.rxRssi;
                reportFrame["txLqi"] = frame.txLqi;
                reportFrame["txRssi"] = frame.txRssi;

                if (frame.status == TestFrameStatus::OK) {
                    minRxLqi = std::min(minRxLqi, frame.rxLqi);
                    maxRxLqi = std::max(maxRxLqi, frame.rxLqi);
                    sumRxLqi += frame.rxLqi;

                    minRxRssi = std::min(minRxRssi, frame.rxRssi);
                    maxRxRssi = std::max(maxRxRssi, frame.rxRssi);
                    sumRxRssi += frame.rxRssi;

                    minTxLqi = std::min(minTxLqi, frame.txLqi);
                    maxTxLqi = std::max(maxTxLqi, frame.txLqi);
                    sumTxLqi += frame.txLqi;

                    minTxRssi = std::min(minTxRssi, frame.txRssi);
                    maxTxRssi = std::max(maxTxRssi, frame.txRssi);
                    sumTxRssi += frame.txRssi;
                }

                std::ostringstream ss;
                ss << "Packet " << i << " ";

                switch (frame.status) {
                    case TestFrameStatus::LOST:
                        errors++;
                        ss << "LOST";
                        break;
                    case TestFrameStatus::OK:
                        ss << "OK";
                        break;
                    case TestFrameStatus::CORRUPTED:
                        errors++;
                        ss << "CORRUPTED";
                        break;
                    case TestFrameStatus::UNKNOWN:
                        // Should never happen
                        YIO_LOG_ERROR_EVENT("MfgTestClient.LogicError", "Unknown frame status for frame " << i << "; should never happen");
                        exit(1);
                }

                ss << " RX LQI " << (int)frame.rxLqi << " RX RSSI " << (int)frame.rxRssi << " TX LQI " << (int)frame.txLqi << " TX RSSI " << (int)frame.txRssi;

                YIO_LOG_INFO(ss.str());
            }

            const int frameCount = std::count_if(frames_.begin(), frames_.end(), [](const TestFrameInfo& frame) { return frame.status != TestFrameStatus::LOST && frame.status != TestFrameStatus::UNKNOWN; });
            const float errorRate = frameCount == 0 ? 1 : (float)errors / frameCount;

            const float avgRxLqi = frameCount == 0 ? maxRxLqi : (float)sumRxLqi / frameCount;
            const float avgRxRssi = frameCount == 0 ? maxRxRssi : (float)sumRxRssi / frameCount;

            const float avgTxLqi = frameCount == 0 ? maxTxLqi : (float)sumTxLqi / frameCount;
            const float avgTxRssi = frameCount == 0 ? maxTxRssi : (float)sumTxRssi / frameCount;

            if (frameCount == 0) {
                minRxLqi = maxRxLqi;
                minRxRssi = maxRxRssi;

                minTxLqi = maxTxLqi;
                minTxRssi = maxTxRssi;
            }

            report["errorRate"] = errorRate;

            auto& reportRxLqi = report["rxLqi"];
            reportRxLqi["min"] = minRxLqi;
            reportRxLqi["avg"] = avgRxLqi;
            reportRxLqi["max"] = maxRxLqi;

            auto& reportRxRssi = report["rxRssi"];
            reportRxRssi["min"] = minRxRssi;
            reportRxRssi["avg"] = avgRxRssi;
            reportRxRssi["max"] = maxRxRssi;

            auto& reportTxLqi = report["txLqi"];
            reportTxLqi["min"] = minTxLqi;
            reportTxLqi["avg"] = avgTxLqi;
            reportTxLqi["max"] = maxTxLqi;

            auto& reportTxRssi = report["txRssi"];
            reportTxRssi["min"] = minTxRssi;
            reportTxRssi["avg"] = avgTxRssi;
            reportTxRssi["max"] = maxTxRssi;

            YIO_LOG_INFO("Error rate: " << std::setprecision(3) << 100.0f * errorRate << "%");

            YIO_LOG_INFO("RX LQI: min " << (int)minRxLqi << " avg " << avgRxLqi << " max " << (int)maxRxLqi);
            YIO_LOG_INFO("RX RSSI: min " << (int)minRxRssi << " avg " << avgRxRssi << " max " << (int)maxRxRssi);

            YIO_LOG_INFO("TX LQI: min " << (int)minTxLqi << " avg " << avgTxLqi << " max " << (int)maxTxLqi);
            YIO_LOG_INFO("TX RSSI: min " << (int)minTxRssi << " avg " << avgTxRssi << " max " << (int)maxTxRssi);

            if (!reportPath_.empty()) {
                std::ofstream f(reportPath_);
                f << quasar::jsonToString(report);
                f.close();

                YIO_LOG_INFO("Test report saved to " << reportPath_);
            }
        }

        void handleTestFrame(TestFrame frame, uint8_t lqi, int8_t rssi) override {
            if (frame.magic != TEST_RESPONSE_MAGIC) {
                YIO_LOG_DEBUG("Wrong magic, skipping");
                return;
            }

            YIO_LOG_DEBUG("Got test response: " << frame.sessionId << " " << frame.packetId << " " << frame.value);

            if (frame.sessionId != sessionId_) {
                YIO_LOG_DEBUG("Wrong session ID, skipping");
                return;
            }

            if (frame.packetId >= frames_.size()) {
                YIO_LOG_ERROR_EVENT("MfgTestClient.InvalidPacketId", "Packet ID is too large");
                return;
            }

            {
                std::unique_lock<std::mutex> lk(mutex_);
                auto& info = frames_[frame.packetId];
                info.rxLqi = lqi;
                info.rxRssi = rssi;
                info.txLqi = frame.lqi;
                info.txRssi = frame.rssi;

                if (info.status == TestFrameStatus::UNKNOWN) {
                    if (frame.value != info.value) {
                        YIO_LOG_ERROR_EVENT("MfgTestClient.FrameValueCorrupted", "Packet value is corrupted (should not happen)");
                        info.status = TestFrameStatus::CORRUPTED;
                    } else {
                        info.status = TestFrameStatus::OK;
                    }
                } else {
                    YIO_LOG_ERROR_EVENT("MfgTestClient.FrameReceivedAfterTimeout", "Packet " << frame.packetId << " received after timeout (should not happen)");
                }
                cv_.notify_all();
            }
        }

    private:
        size_t packetNumber_;
        int timeout_;
        std::string reportPath_;

        std::vector<TestFrameInfo> frames_;
        std::condition_variable cv_;
        std::mutex mutex_;
    };

} // namespace

int main(int argc, const char* argv[]) {
    auto server = std::make_shared<MfgTestServer>();
    auto client = std::make_shared<MfgTestClient>();

    TModChooser modes;
    modes.SetDescription("Zigbee manufacturing test utility");
    modes.AddMode("server", server.get(), "listen to test frames and reply");
    modes.AddMode("client", client.get(), "send test frames and wait for response");

    return modes.Run(argc, argv);
}
