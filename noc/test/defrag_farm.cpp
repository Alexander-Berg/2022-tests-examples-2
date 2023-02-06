#include "gtest/gtest.h"

#include "../src/dataplane.h"
#include "../src/worker.h"

common::log::LogPriority common::log::logPriority = common::log::TLOG_DEBUG;

class mControlPlane: public cControlPlane
{
public:
	mControlPlane(cDataPlane *dataPlane) :
			cControlPlane(dataPlane)
	{
	}
	using cControlPlane::handlePacket_fragment;

	void waitAllWorkers()
	{
	}

	void preparePacket(rte_mbuf* mbuf)
	{
		slowWorker->preparePacket(mbuf);
	}

	using cControlPlane::errors;
	using cControlPlane::mempool;
	using cControlPlane::fragmentation;
	using cControlPlane::slowWorkerMbufs;
	using cControlPlane::slowWorker;
};

class mDataPlane: public cDataPlane
{
public:
	mDataPlane()
	{
		this->controlPlane.reset(new mControlPlane(this));
	}
	using cDataPlane::controlPlane;
	using cDataPlane::globalBases;
	using cDataPlane::currentGlobalBaseId;
};

namespace
{

static common::ipv6_address_t farm_prefix = std::string("2a02:6bc::0");
static common::ipv6_address_t source_prefix = std::string("64:ff9b:1::0");
static common::ipv4_address_t srcIPv4 = std::string("1.1.1.1");
static common::ipv4_address_t dstIPv4 = std::string("2.2.2.2");

class DefragFarmTest: public ::testing::Test
{
protected:
	void SetUp()
	{
	}
	void TearDown()
	{
	}
	static void SetUpTestCase()
	{
		controlPlane =
				static_cast<mControlPlane*>(dataPlane.controlPlane.get());
		dataPlane.init("yadecap-dataplane_test", "../../test/dataplane.conf");
	}
	static void TearDownTestCase()
	{
		clear();
	}

	static void clear()
	{
		common::idp::updateGlobalBase::request request;
		request.emplace_back(
				common::idp::updateGlobalBase::requestType::clear,
				std::tuple<>{});

		controlPlane->updateGlobalBase(request);
	}
	static void setFarm(const common::ipv6_address_t &farm,
			const common::ipv6_address_t &source)
	{

		auto flow = common::globalBase::tFlow
		{ };

		common::idp::updateGlobalBase::request request;
		request.emplace_back(
				common::idp::updateGlobalBase::requestType::updateNat64stateless,
				common::idp::updateGlobalBase::updateNat64stateless::request
				{ 0, 0, flow, farm, source, 0 });

		controlPlane->updateGlobalBase(request);
	}

	static rte_mbuf* createPacketEthernet(uint16_t ether_type)
	{
		rte_mbuf *mbuf = rte_pktmbuf_alloc(controlPlane->mempool);
		rte_pktmbuf_append(mbuf, packetSize);
		rte_ether_hdr* ethernetHeader = rte_pktmbuf_mtod(mbuf, rte_ether_hdr*);
		ethernetHeader->ether_type = rte_cpu_to_be_16(ether_type);

		return mbuf;
	}
	static rte_mbuf* createPacketIPv4(uint16_t fragment, uint8_t proto,
			common::ipv4_address_t src = srcIPv4, common::ipv4_address_t dst = dstIPv4)
	{
		auto mbuf = createPacketEthernet(RTE_ETHER_TYPE_IPV4);

		rte_ipv4_hdr* ipv4Header = rte_pktmbuf_mtod_offset(mbuf, rte_ipv4_hdr*, sizeof(rte_ether_hdr));
		ipv4Header->total_length = rte_be_to_cpu_16(packetSize - sizeof(rte_ether_hdr));
		ipv4Header->version_ihl = 0x05;
		ipv4Header->fragment_offset = fragment;
		ipv4Header->next_proto_id = proto;
		ipv4Header->src_addr = src;
		ipv4Header->dst_addr = dst;

		return mbuf;
	}
	constexpr static uint16_t packetSize = 1024;
	static mDataPlane dataPlane;
	static mControlPlane *controlPlane;
};
mDataPlane DefragFarmTest::dataPlane;
mControlPlane *DefragFarmTest::controlPlane;

TEST_F(DefragFarmTest, Config)
{
	setFarm(farm_prefix, source_prefix);
	EXPECT_EQ(0, controlPlane->errors.size());

	for (const auto &iter : dataPlane.globalBases)
	{
		EXPECT_EQ(ipv6_address_t::convert(farm_prefix),
				iter.second[0]->nat64statelesses[0].defrag_farm_prefix);
		EXPECT_EQ(ipv6_address_t::convert(farm_prefix),
				iter.second[1]->nat64statelesses[0].defrag_farm_prefix);
		EXPECT_EQ(ipv6_address_t::convert(source_prefix),
				iter.second[0]->nat64statelesses[0].defrag_source_prefix);
		EXPECT_EQ(ipv6_address_t::convert(source_prefix),
				iter.second[1]->nat64statelesses[0].defrag_source_prefix);
	}
}

TEST_F(DefragFarmTest, ipv6)
{
	setFarm(farm_prefix, source_prefix);

	auto mbuf = createPacketEthernet(RTE_ETHER_TYPE_IPV6);
	dataplane::metadata *metadata = YADECAP_METADATA(mbuf);
	metadata->network_headerType = rte_cpu_to_be_16(RTE_ETHER_TYPE_IPV6);

	auto prev_not_fragment_packets = controlPlane->fragmentation.getStats().not_fragment_packets;

	controlPlane->handlePacket_fragment(mbuf);

	EXPECT_EQ(1, controlPlane->fragmentation.getStats().not_fragment_packets - prev_not_fragment_packets);
}

TEST_F(DefragFarmTest, preparePacketIPv4)
{
	auto mbuf = createPacketIPv4(0xff, IPPROTO_TCP);
	dataplane::metadata *metadata = YADECAP_METADATA(mbuf);

	controlPlane->preparePacket(mbuf);

	EXPECT_EQ(rte_cpu_to_be_16(RTE_ETHER_TYPE_IPV4), metadata->network_headerType);
	EXPECT_EQ(sizeof(rte_ether_hdr), metadata->network_headerOffset);
	EXPECT_EQ(YANET_NETWORK_FLAG_FRAGMENT | YANET_NETWORK_FLAG_NOT_FIRST_FRAGMENT, metadata->network_flags);
	EXPECT_EQ(IPPROTO_TCP, metadata->transport_headerType);
	EXPECT_EQ(34, metadata->transport_headerOffset);
}

TEST_F(DefragFarmTest, ipv4)
{
	setFarm(farm_prefix, source_prefix);

	auto mbuf = createPacketIPv4(0xff, IPPROTO_TCP);
	dataplane::metadata *metadata = YADECAP_METADATA(mbuf);

	controlPlane->preparePacket(mbuf);

	auto prev_not_fragment_packets = controlPlane->fragmentation.getStats().not_fragment_packets;
	controlPlane->slowWorkerMbufs = {};

	controlPlane->handlePacket_fragment(mbuf);

	EXPECT_EQ(0, controlPlane->fragmentation.getStats().not_fragment_packets - prev_not_fragment_packets);
	EXPECT_EQ(1, controlPlane->slowWorkerMbufs.size());

	EXPECT_EQ(rte_cpu_to_be_16(RTE_ETHER_TYPE_IPV6), metadata->network_headerType);

	const rte_ipv6_hdr* ipv6Header = rte_pktmbuf_mtod_offset(mbuf, rte_ipv6_hdr*, metadata->network_headerOffset);
	EXPECT_EQ("2a02:6bc::202:202", common::ipv6_address_t(ipv6Header->dst_addr).toString());
	EXPECT_EQ("64:ff9b:1::101:101", common::ipv6_address_t(ipv6Header->src_addr).toString());
}

}
