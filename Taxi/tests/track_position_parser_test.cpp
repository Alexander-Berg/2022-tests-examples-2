#include <gtest/gtest.h>

#include <models/track_position.hpp>

TEST(TrackPositionParser, NoClid) {
  LogExtra empty_log_extra;
  EXPECT_EQ(PositionsDecoder::Parse("", empty_log_extra),
            std::vector<TrackPosition>());

  auto req1 =
      "timestamp=1510214400\tclid=\tuuid="
      "d6b3292dac044ce1b2d35429ba3d3146\tlon=61.407895\tlat=55."
      "165717\tdirection=256.790000\tspeed=9.000000\tbad=0\tstatus=2\torder_"
      "status=0\tis_home_enabled=0\ttime_gps_orig=1510214400000\ttime_system_"
      "orig=1510214400377\ttime_system_sync=1510214400381";
  std::vector<TrackPosition> pos1;

  EXPECT_EQ(PositionsDecoder::Parse(req1, empty_log_extra), pos1);
}

TEST(TrackPositionParser, Test) {
  LogExtra empty_log_extra;
  EXPECT_EQ(PositionsDecoder::Parse("", empty_log_extra),
            std::vector<TrackPosition>());

  auto req1 =
      "timestamp=1510214400\tclid=1956793543\tuuid="
      "d6b3292dac044ce1b2d35429ba3d3146\tlon=61.407895\tlat=55."
      "165717\tdirection=256.790000\tspeed=9.000000\tbad=0\tstatus=2\torder_"
      "status=0\tis_home_enabled=0\ttime_gps_orig=1510214400000\ttime_system_"
      "orig=1510214400377\ttime_system_sync=1510214400381";
  std::vector<TrackPosition> pos1 = {
      TrackPosition("1956793543", "d6b3292dac044ce1b2d35429ba3d3146", false,
                    1510214400, 61.407895, 55.165717)};

  EXPECT_EQ(PositionsDecoder::Parse(req1, empty_log_extra), pos1);
}

TEST(TrackPositionParser, TestErrorLine) {
  LogExtra empty_log_extra;
  EXPECT_EQ(PositionsDecoder::Parse("", empty_log_extra),
            std::vector<TrackPosition>());

  auto req1 =
      "timestamp=1510214400\tclid=1956793543\tuuid="
      "uuid1\tlon=61.407895\tlat=55."
      "165717\tdirection=256.790000\tspeed=9.000000\tbad=0\tstatus=2\torder_"
      "status=0\tis_home_enabled=0\ttime_gps_orig=1510214400000\ttime_system_"
      "orig=1510214400377\ttime_system_sync=1510214400381\n"

      "tskv\ttimestamp=1510214401\tclid=1956793543\tuuid="
      "uuid2\tlon=6tskv\tlat=55."
      "165717\tdirection=256.790000\tspeed=9.000000\tbad=0\tstatus=2\torder_"
      "status=0\tis_home_enabled=0\ttime_gps_orig=1510214400000\ttime_system_"
      "orig=1510214400377\ttime_system_sync=1510214400381\n"

      "tskv\ttimestamp=1510214402\tclid=1956793543\tuuid="
      "uuid3\tlon=61.407895\tlat=55."
      "165717\tdirection=256.790000\tspeed=9.000000\tbad=0\tstatus=2\torder_"
      "status=0\tis_home_enabled=0\ttime_gps_orig=1510214400000\ttime_system_"
      "orig=1510214400377\ttime_system_sync=1510214400381";

  EXPECT_EQ(PositionsDecoder::Parse(req1, empty_log_extra).size(), 2u);
}

TEST(TrackPositionParser, TestTskv) {
  LogExtra empty_log_extra;
  EXPECT_EQ(PositionsDecoder::Parse("", empty_log_extra),
            std::vector<TrackPosition>());

  auto req1 =
      "tskv\t"
      "timestamp=1510214400\tclid=1956793543\tuuid="
      "d6b3292dac044ce1b2d35429ba3d3146\tlon=61.407895\tlat=55."
      "165717\tdirection=256.790000\tspeed=9.000000\tbad=0\tstatus=2\torder_"
      "status=0\tis_home_enabled=0\ttime_gps_orig=1510214400000\ttime_system_"
      "orig=1510214400377\ttime_system_sync=1510214400381\tchoose_reason=\n"
      "tskv\t"
      "timestamp=1510214400\tclid=1956793544\tuuid="
      "d6b3292dac044ce1b2d35429ba3d3147\tlon=61.407895\tlat=55."
      "165717\tdirection=256.790000\tspeed=9.000000\tbad=0\tstatus=2\torder_"
      "status=0\tis_home_enabled=0\ttime_gps_orig=1510214400000\ttime_system_"
      "orig=1510214400377\ttime_system_sync=1510214400381\tchoose_reason=\n";
  std::vector<TrackPosition> pos1 = {
      TrackPosition("1956793543", "d6b3292dac044ce1b2d35429ba3d3146", false,
                    1510214400, 61.407895, 55.165717),
      TrackPosition("1956793544", "d6b3292dac044ce1b2d35429ba3d3147", false,
                    1510214400, 61.407895, 55.165717),
  };

  EXPECT_EQ(PositionsDecoder::Parse(req1, empty_log_extra), pos1);
}

TEST(TrackPositionParser, Invalid) {
  LogExtra empty_log_extra;
  auto req = "bad";
  EXPECT_EQ(PositionsDecoder::Parse(req, empty_log_extra),
            std::vector<TrackPosition>());

  // no clid
  auto req_not_all_data =
      "timestamp=1510214400\tuuid="
      "d6b3292dac044ce1b2d35429ba3d3146\tlon=61.407895\tlat=55."
      "165717\tdirection=256.790000\tspeed=9.000000\tbad=0\tstatus=2\torder_"
      "status=0\tis_home_enabled=0\ttime_gps_orig=1510214400000\ttime_system_"
      "orig=1510214400377\ttime_system_sync=1510214400381";
  EXPECT_EQ(PositionsDecoder::Parse(req_not_all_data, empty_log_extra),
            std::vector<TrackPosition>());

  auto req_broken =
      "timestamp=1529431415\treceive_time=1529431416\tclid=400000010989\tuuid="
      "9f7170e9df6a40b892be070b670b7d30\t"
      "lon=56.258100\tlat=57.985594\tdirection=269.251530\tspeed=17."
      "000000\tbad=0\tstatus=2\torder_status=5\t"
      "order_type=2\ttime_gps_orig=1529431433000\ttime_system_orig="
      "1529431397322\ttime_system_sync=1529431415861\t"
      "satellites_data=JQAkAeBYHAA,GoANAUDYHAA,GMAnALKIAAA,JgAaAhAIHAA,"
      "CGAZAWJYBAA,BiAZAYDAHAA,FMBBAmEAHAA,H0AmAdIYBAA,JCAxAgCQHAA,GEApARBwGAA,"
      "C+A6AWBQHAA,HsAeAVBAHAA,ASATAUJQBAA,CAAVALIIAAA,IaAOAeCwHAA,KIAJAQDgHAA,"
      "A0BSAfIQBAA,I0A6AYKQBAA,DcAIAXJgBAA,KYAUATKYBAA,DEAbAXCgHAA\t"
      "timestamp=1529431416\treceive_time=1529431416\tclid=400000016339\tuuid="
      "8b8065347ba248f5ae3e7cde89c1bb46\t"
      "lon=37.720677\tlat=55.611857\tdirection=44.300000\tspeed=0.000000\tbad="
      "0\tstatus=1\torder_status=0\t"
      "time_gps_orig=1529431416000\ttime_system_orig=1529431416121\ttime_"
      "system_sync=1529431416499\t"
      "aggregated_data={\"l\":{\"accuracy\":\"140.0\",\"altitude\":\"0.0\","
      "\"bearing\":\"null\",\"isBad\":\"false\",\"lat\":\"55.6114044\",\"lon\":"
      "\"37.7205315\",\"provider\":\"lbs-wifi\",\"realTime\":\"292440662\","
      "\"speedMetersPerSecond\":\"null\",\"time\":\"1529431415771\"},\"p\":{"
      "\"accuracy\":\"1.0\",\"altitude\":\"171.1\",\"bearing\":\"44.3\","
      "\"isBad\":\"false\",\"lat\":\"55.6118567\",\"lon\":\"37.7206767\","
      "\"provider\":\"passive\",\"realTime\":\"292440994\","
      "\"speedMetersPerSecond\":\"0.0\",\"time\":\"1529431416000\"}}\n\t"
      "satellites_data=J0APAUDgAAA,H8AZAhCwBAA,CiARAUCgBAA,H8ADAAAYAAA,"
      "HIAqAsBABAA,GAAUAkDYBAA,I4A8AkCQBAA,D8A8AlEABAA,BMAQAUDABAA,FMAsAZBwBAA,"
      "CaAvAXBQBAA,JQAjAeAIBAA,JCAuAWBYBAA\t"
      "timestamp=1529431416\treceive_time=1529431417\tclid=400000000472\tuuid="
      "576d7f4198b343eb8268b0fb079b13a0\t"
      "lon=49.120295\tlat=55.826953\tdirection=89.810000\tspeed=0.000000\tbad="
      "0\tstatus=1\torder_status=0\t"
      "time_gps_orig=1529431416000\ttime_system_orig=1529427984192\ttime_"
      "system_sync=1529431416034\t"
      "satellites_data=GaASAADYAAA,HiAkAaBABAA,KUAUAgKYAAA,HqAsAlIYAAA,"
      "B0ARAdIIAAA,JOAnAhBYBAA,FwAsAfBwBAA,B6AUAkJYAAA,EqBCAlEABAA,BaAVAfDABAA,"
      "DQAFAgJgAAA,KCAKAZDgBAA,JEA0AXCQBAA,C0AYAnCgBAA,AMARAbJQAAA,CqA3AjBQBAA,"
      "IQASAgCwBAA,JcAdAdAIBAA,BIBNAoIQAAA,I4A/AYKQAAA,F4ArAnKIAAA";

  std::vector<TrackPosition> broken_result = {
      TrackPosition("400000016339", "8b8065347ba248f5ae3e7cde89c1bb46", false,
                    1529431416, 37.720677, 55.611857),
      TrackPosition("400000000472", "576d7f4198b343eb8268b0fb079b13a0", false,
                    1529431416, 49.120295, 55.826953)};
  EXPECT_EQ(PositionsDecoder::Parse(req_broken, empty_log_extra),
            broken_result);
}
