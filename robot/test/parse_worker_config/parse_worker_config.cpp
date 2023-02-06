#include "util/string/join.h"
#include <robot/blrt/library/config/parse_blrt_config.h>
#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>


namespace NBlrt {

    void ParseWorkerConfig(const TVector<TString>& configNames) {
        const auto workerCommonOpts = NMercury::TCommonOpts {
            .ConfigFile = "blrt_config.pb.txt",
            .ConfigOverrideFiles = configNames,
            .ConfigDirPath = JoinFsPaths(BuildRoot(), "robot/blrt/packages/worker_configs"),
        };

        UNIT_ASSERT_NO_EXCEPTION_C(
            ParseBlrtConfig(workerCommonOpts),
            "Failed to parse worker configs " << JoinSeq(" ", configNames));
    }

}


Y_UNIT_TEST_SUITE(ParseWorkerConfigTests) {
    Y_UNIT_TEST(ProdMainConfigTest) {
        NBlrt::ParseWorkerConfig({"blrt_config_override_perf.pb.txt", "blrt_config_override_main.pb.txt", "blrt_config_override_main_perf.pb.txt"});
        NBlrt::ParseWorkerConfig({"blrt_config_override_dyn.pb.txt", "blrt_config_override_main.pb.txt", "blrt_config_override_main_dyn.pb.txt"});
    }
    Y_UNIT_TEST(PreStableConfigTest) {
        NBlrt::ParseWorkerConfig({"blrt_config_override_perf.pb.txt", "blrt_config_override_prestable.pb.txt", "blrt_config_override_prestable_perf.pb.txt"});
        NBlrt::ParseWorkerConfig({"blrt_config_override_dyn.pb.txt", "blrt_config_override_prestable.pb.txt", "blrt_config_override_prestable_dyn.pb.txt"});
    }
    Y_UNIT_TEST(TestsConfigTest) {
        NBlrt::ParseWorkerConfig({"blrt_config_override_perf.pb.txt", "blrt_config_override_test.pb.txt"});
        NBlrt::ParseWorkerConfig({"blrt_config_override_dyn.pb.txt", "blrt_config_override_test.pb.txt"});
    }
    Y_UNIT_TEST(ProdDataCampConfigTest) {
        NBlrt::ParseWorkerConfig({"blrt_config_override_perf.pb.txt", "blrt_config_override_datacamp.pb.txt", "blrt_config_override_main_datacamp.pb.txt"});
        NBlrt::ParseWorkerConfig({"blrt_config_override_dyn.pb.txt", "blrt_config_override_datacamp.pb.txt", "blrt_config_override_main_datacamp.pb.txt"});
    }
    Y_UNIT_TEST(PrestableDataCampConfigTest) {
        NBlrt::ParseWorkerConfig({"blrt_config_override_perf_datacamp.pb.txt", "blrt_config_override_prestable_datacamp.pb.txt"});
    }
    Y_UNIT_TEST(DevLocalConfigTest) {
        NBlrt::ParseWorkerConfig({"blrt_config_override_perf.pb.txt", "blrt_config_override_dev_local.pb.txt"});
        NBlrt::ParseWorkerConfig({"blrt_config_override_dyn.pb.txt", "blrt_config_override_dev_local.pb.txt"});
    }
    Y_UNIT_TEST(DevVanillaConfigTest) {
        NBlrt::ParseWorkerConfig({"blrt_config_override_perf.pb.txt", "blrt_config_override_dev_vanilla.pb.txt"});
        NBlrt::ParseWorkerConfig({"blrt_config_override_dyn.pb.txt", "blrt_config_override_dev_vanilla.pb.txt"});
    }
    Y_UNIT_TEST(AcceptanceConfigTest) {
        NBlrt::ParseWorkerConfig({"blrt_config_override_perf.pb.txt", "blrt_config_override_prestable.pb.txt", "blrt_config_override_acceptance_perf.pb.txt"});
        NBlrt::ParseWorkerConfig({"blrt_config_override_dyn.pb.txt", "blrt_config_override_prestable.pb.txt", "blrt_config_override_acceptance_dyn.pb.txt"});
    }
    Y_UNIT_TEST(OfferAcceptanceConfigTest) {
        NBlrt::ParseWorkerConfig({"blrt_config_override_perf.pb.txt", "blrt_config_override_prestable_datacamp.pb.txt", "blrt_config_override_offer_acceptance_perf.pb.txt"});
    }

}
