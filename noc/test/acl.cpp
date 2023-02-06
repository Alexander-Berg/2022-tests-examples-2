#include <fstream>

#include "gmock/gmock.h"
#include <gtest/gtest.h>

#include "../../common/nlohmann/json.hpp"
#include "../../common/type.h"
#include "../src/acl.h"
#include "../src/acl/rule.h"

#define YANET_HELPER_XSTRING(x) #x
#define YANET_HELPER_STRING(x) YANET_HELPER_XSTRING(x)

namespace
{

template<typename... Args>
void UNUSED(Args&&...) {}

std::string get_data_path(const std::string& path)
{
    return std::string(YANET_HELPER_STRING(YANET_CONFIG_TEST_CWD)) + path;
}

using common::ipv4_address_t;
using common::globalBase::eFlowType;

typedef std::map<std::remove_reference<decltype(std::get<0>(acl::result_t::table2.back()))>::type,
                 std::remove_reference<decltype(std::get<1>(acl::result_t::table2.back()))>::type>
    table2_map_t;

class digraph_t
{
public:
	void dump(const acl::result_t& result) const
	{
		dump_header();
		dump_nodes(result);
		dump_links(result);
		dump_trailer();
	}

private:
	void dump_header() const
	{
		printf("digraph G {\n");
		printf("    nodesep=1;\n");
		printf("    ranksep=5;\n");
		printf("    rankdir=LR;\n");
		printf("    node [shape=record fontname=\"Monospace\" fontsize=10];\n");
		printf("    node [width = 5];\n");
		printf("\n");
	}

	void dump_trailer() const
	{
		printf("}\n");
	}

	void dump_nodes(const acl::result_t& result) const
	{
		print_addr_table("node_ipv4_src", "IPv4.S", result.source.ipv4);
		print_addr_table("node_ipv4_dst", "IPv4.D", result.destination.ipv4);
		print_addr_table6("node_ipv6_src", "IPv6.S", result.source.ipv6);
		print_addr_table6("node_ipv6_dst", "IPv6.D", result.destination.ipv6);
		print_array("fragmentation", result.fragmentation);
		print_array("proto", result.transport_protocol);
		print_array("transport_prm1", result.transport_prm1);
		print_array("transport_prm2", result.transport_prm2);
		print_array("transport_prm3", result.transport_prm3);
		print_rules(result.rules_text);

		printf("    %s[label=\"<n>[%s]", "table0", "table0");
		for (const auto& [k, v] : result.table0)
		{
			UNUSED(v);
			auto [k1, k2, k3, k4, k5] = k;
			printf("|{<f%d-%d-%d-%d-%d>%d %d %d %d %d}", k1, k2, k3, k4, k5, k1, k2, k3, k4, k5);
		}
		printf("\"];\n");
		printf("    %s[label=\"<n>[%s]", "table1", "table1");
		for (auto [k, v] : result.table1)
		{
			UNUSED(v);
			auto [k1, k2, k3] = k;
			printf("|{<f%d-%d-%d>%d %d %d}", k1, k2, k3, k1, k2, k3);
		}
		printf("\"];\n");
		printf("    %s[label=\"<n>[%s]", "table2", "table2");
		for (auto [k, v] : result.table2)
		{
			auto [k1, k2] = k;
			printf("|{<f%d-%d>%d-%u}", k1, k2, static_cast<int>(v.type), v.counter_id);
		}
		printf("\"];\n");
	}

	void print_addr_table(const char* node, const char* name, const std::map<uint8_t, std::map<common::ipv4_address_t, tAclGroupId>>& t) const
	{
		printf("    %s[label=\"<n>[%s]", node, name);
		for (const auto& [mask, v] : t)
		{
			for (const auto& [addr, id] : v)
			{
				printf("|{<f%d>%s/%d}", id, addr.toString().data(), mask);
			}
		}
		printf("\"];\n");
	}

	void print_addr_table6(const char* node, const char* name, const std::vector<std::tuple<common::ipv6_address_t, common::ipv6_address_t, tAclGroupId>>& t) const
	{
		printf("    %s[label=\"<n>[%s]", node, name);
		for (const auto& [addr, mask, id] : t)
		{
			printf("|{<f%d>%s/%s}", id, addr.toString().data(), mask.toString().data());
		}
		printf("\"];\n");
	}

	template<typename T>
	void print_array(const char* name, const T& t) const
	{
		printf("    %s[label=\"<n>[%s]", name, name);
		for (unsigned int i = 0; i < t.size(); ++i)
		{
			if (t[i] != 0)
			{
				printf("|{<f%d>%d}", i, i);
			}
		}
		printf("\"];\n");
	}

	void print_rules(std::map<uint32_t, std::string> rules_text) const
	{
		printf("    rules[label=\"<n>[rules]");
		for (const auto& [id, text] : rules_text)
		{
			printf("|{<f%d>%d %s}", id, id, text.c_str());
		}
		printf("\"];\n");
	}

	void dump_links(const acl::result_t& result) const
	{
		print_addr_table_links<0>("node_ipv4_src", result.source.ipv4, result.table1);
		print_addr_table_links<1>("node_ipv4_dst", result.destination.ipv4, result.table1);
		print_addr_table_links6<0>("node_ipv6_src", result.source.ipv6, result.table1);
		print_addr_table_links6<1>("node_ipv6_dst", result.destination.ipv6, result.table1);
		print_array_links<0>("fragmentation", "black", result.fragmentation, result.table0);
		print_array_links<1>("proto", "red", result.transport_protocol, result.table0);
		print_array_links<2>("transport_prm1", "blue", result.transport_prm1, result.table0);
		print_array_links<3>("transport_prm2", "green", result.transport_prm2, result.table0);
		print_array_links<4>("transport_prm3", "orange", result.transport_prm3, result.table0);

		table2_map_t table2;
		table2.insert(result.table2.begin(), result.table2.end());

		for (auto [k0, v0] : result.table0)
		{
			for (auto [k1, v1] : result.table1)
			{
				if (table2.count(std::make_tuple(v0, v1)))
				{
					auto [p1, p2, p3, p4, p5] = k0;
					auto [p6, p7, p8] = k1;
					printf("    table0:<f%d-%d-%d-%d-%d> -> table2:<f0-%d-%d>\n", p1, p2, p3, p4, p5, v0, v1);
					printf("    table1:<f%d-%d-%d> -> table2:<f0-%d-%d>\n", p6, p7, p8, v0, v1);

					const auto& v3 = table2.at(std::make_tuple(v0, v1));
					for (auto id : result.ids_map[v3.counter_id])
					{
						printf("    table2:<f0-%d-%d> -> rules:<f%d>\n", v0, v1, id);
					}
				}
			}
		}
	}

	template<std::size_t N, typename T, typename K>
	void print_addr_table_links(const char* node, const std::map<K, std::map<T, tAclGroupId>>& t, const common::idp::updateGlobalBase::aclTable1::request& table1) const
	{
		for (const auto& [mask, v] : t)
		{
			UNUSED(mask);
			for (const auto& [addr, id] : v)
			{
				UNUSED(addr);
				for (auto [k, v] : table1)
				{
					UNUSED(v);
					auto [k1, k2, k3] = k;
					if (std::get<N>(k) == id)
					{
						printf("    %s:f%d -> table1:<f%d-%d-%d>;\n", node, id, k1, k2, k3);
					}
				}
			}
		}
	}

	template<std::size_t N, typename T, typename K>
	void print_addr_table_links6(const char* node, const std::vector<std::tuple<K, T, tAclGroupId>>& t, const common::idp::updateGlobalBase::aclTable1::request& table1) const
	{
		for (const auto& [addr, mask, id] : t)
		{
			UNUSED(addr, mask);
			for (auto [k, v] : table1)
			{
				UNUSED(v);
				auto [k1, k2, k3] = k;
				if (std::get<N>(k) == id)
				{
					printf("    %s:f%d -> table1:<f%d-%d-%d>;\n", node, id, k1, k2, k3);
				}
			}
		}
	}

	template<std::size_t N, typename T>
	void print_array_links(const char* node, const char* color, const T& t, const common::idp::updateGlobalBase::aclTable0::request& table0) const
	{
		for (unsigned int i = 0; i < t.size(); ++i)
		{
			if (t[i] == 0)
			{
				continue;
			}
			for (auto [k, v] : table0)
			{
				UNUSED(v);
				auto [k1, k2, k3, k4, k5] = k;
				if (std::get<N>(k) == t[i])
				{
					printf("    %s:f%d -> table0:<f%d-%d-%d-%d-%d> [color=%s];\n", node, i, k1, k2, k3, k4, k5, color);
				}
			}
		}
	}
};

auto make_default_acl(tAclId aclId = 1) -> controlplane::base::acl_t
{
	controlplane::base::acl_t acl;
	common::globalBase::tFlow flow{};
	flow.type = common::globalBase::eFlowType::route;

	acl.aclId = aclId;
	acl.nextModules = {"unmatched"};
	acl.nextModuleRules.emplace_back(flow);

	return acl;
}

TEST(ACL, Basic)
{
	auto fw = make_default_acl();
	fw.firewall = R"({":BEGIN":[{"filter":{"direction":"in"},"nextSection":":IN","counters":[2]}],":IN":[{"filter":{"source":["2a02:6b8:ff1c:2030::/ffff:ffff:ffff:fff0::"],"protocol":{"type":"tcp","destination":[80]}},"counters":[5]},{"filter":{"source":["2a02:6b8:ff1c:2030::/ffff:ffff:ffff:ffff::"],"protocol":{"type":"tcp","destination":[81]}},"counters":[6]},{"filter":{"source":["2a02:6b8:ff1c:2030:0:1234::/ffff:ffff:ffff:fff0:ffff:ffff::","2a02:6b8:ff1c:2030:0:4321::/ffff:ffff:ffff:fff0:ffff:ffff::"],"protocol":{"type":"tcp","destination":[82]}},"counters":[7]},{"filter":{"source":["2a02:6b8:ff1c:2030:0:5678::/ffff:ffff:ffff:fff0:ffff:ffff::"],"protocol":{"type":"tcp","destination":[83]}},"counters":[8]},{"filter":{"source":["2a02:6b8:ff1c:2030:aabb:5678::/ffff:ffff:ffff:fff0:ffff:ffff::"],"protocol":{"type":"tcp","destination":[84]}},"counters":[9]},{"nextModule":"drop","counters":[10]}]})"_json;

	std::map<std::string, controlplane::base::acl_t> acls{{"", std::move(fw)}};
	acl::result_t result;
	acl::compile(acls, {{1, {{true, "vlan1"}}}}, result);
}

TEST(ACL, IPv4Only)
{
	struct case_t
	{
		common::ipv4_address_t src;
		uint8_t smask;
		common::ipv4_address_t dst;
		uint8_t dmask;
		uint8_t fragmentation;
		uint8_t proto;
		uint16_t sport;
		uint16_t dport;
		uint8_t flags;

		common::globalBase::eFlowType expected_type;
	};

	auto fw = make_default_acl();
	fw.firewall = R"({
		":BEGIN":[
			{"filter":{"direction":"in"},"nextSection":":IN","id":1}
		],
		":IN":[
			{"filter":{"source":["1.2.3.4"],"protocol":{"type":"tcp","destination":[80]}},"id":2},
			{"nextModule":"drop","id":3}
		]})"_json;

	std::map<std::string, controlplane::base::acl_t> acls{{"acl0", std::move(fw)}};
	acl::result_t result;
	acl::compile(acls, {{1, {{true, "vlan1"}}}}, result);

	const std::vector<case_t> cases = {
	    {ipv4_address_t("1.2.3.4"), 32, ipv4_address_t("0.0.0.0"), 0, 0, 6, 0, 80, 0, eFlowType::route},
	    {ipv4_address_t("1.2.3.5"), 32, ipv4_address_t("0.0.0.0"), 0, 0, 6, 0, 80, 0, eFlowType::drop},
	    {ipv4_address_t("1.2.3.4"), 32, ipv4_address_t("0.0.0.0"), 0, 0, 6, 0, 81, 0, eFlowType::drop},
	    {ipv4_address_t("1.2.3.4"), 32, ipv4_address_t("0.0.0.0"), 0, 0, 20, 0, 80, 0, eFlowType::drop},
	};

	std::map<std::tuple<tAclGroupId, ///< fragmetation state id
	                    tAclGroupId, ///< transport protocol group id (@todo)
	                    tAclGroupId, ///< transport source group id (@todo)
	                    tAclGroupId, ///< transport destination group id (@todo)
	                    tAclGroupId>, ///< transport flags group id (@todo)
	         tAclGroupId>
	    table0;
	table0.insert(result.table0.begin(), result.table0.end());

	table2_map_t table2;
	table2.insert(result.table2.begin(), result.table2.end());

	size_t id = 0;
	for (const auto& c : cases)
	{
		tAclGroupId net_src;
		{
			auto it = result.source.ipv4[c.smask].find(c.src);
			if (it == result.source.ipv4[c.smask].end())
			{
				it = result.source.ipv4[0].find(ipv4_address_t("0.0.0.0"));
			}
			net_src = it->second;
		}
		auto net_dst = result.destination.ipv4[c.dmask][c.dst];

		auto fragmentation = result.fragmentation[c.fragmentation];
		auto protocol = result.transport_protocol[c.proto];
		auto prm1 = result.transport_prm1[c.sport];
		auto prm2 = result.transport_prm2[c.dport];
		auto prm3 = result.transport_prm3[c.flags];

		auto v0 = table0[{fragmentation, protocol, prm1, prm2, prm3}];
		auto v1 = result.table1[{1, net_src, net_dst}];
		if (v1 & common::idp::updateGlobalBase::aclTable1::SINGE_FLOW_NETWORK)
		{
			v0 = 0;
			v1 &= ~common::idp::updateGlobalBase::aclTable1::SINGE_FLOW_NETWORK;
		}
		EXPECT_EQ(c.expected_type, (table2[{v0, v1}].type)) << " case " << id << " v0 " << v0 << " v1 " << v1;
		id++;
	}
}

auto generate_firewall_conf(std::size_t size) -> nlohmann::json
{
	if (size < 2)
	{
		throw std::logic_error("`size` must be >= 2");
	}

	// Subtract by the number of predefined rules.
	size -= 2;

	nlohmann::json j;
	j[":BEGIN"] = {
	    {
	        {"filter", {{"direction", "in"}}},
	        {"nextSection", ":IN"},
	        {"id", 1},
	    },
	};

	for (unsigned i = 0; i < size; ++i)
	{
		std::ostringstream s;
		s << "2a02:6b8:ff1c:" << std::setw(4) << std::setfill('0') << std::hex << i + 1 << "::/ffff:ffff:ffff:ffff::";
		j[":IN"][i] = {
		    {"filter", {{"destination", {s.str()}}, {"protocol", {{"type", "tcp"}, {"destination", {i + 1}}}}}},
		    {"id", 5 + i},
		};
	}
	j[":IN"][size] = {
	    {"filter", {{"protocol", {{"type", "tcp"}, {"tcpflags", "established"}}}}},
	    {"id", 5 + size},
	};
	j[":IN"][size + 1] = {
	    {"nextModule", "drop"},
	    {"id", 5 + size + 1},
	};

	return j;
}

TEST(ACL, Over500)
{
	auto fw = make_default_acl();
	fw.firewall = generate_firewall_conf(500);

	std::map<std::string, controlplane::base::acl_t> acls{{"", std::move(fw)}};
	acl::result_t result;
	acl::compile(acls, {{1, {{true, "vlan1"}}}}, result);
}

TEST(ACL, Over1000)
{
	auto fw = make_default_acl();
	fw.firewall = generate_firewall_conf(1000);

	std::map<std::string, controlplane::base::acl_t> acls{{"", std::move(fw)}};
	acl::result_t result;
	acl::compile(acls, {{1, {{true, "vlan1"}}}}, result);
}

TEST(ACL, Over4000)
{
	auto fw = make_default_acl();
	fw.firewall = generate_firewall_conf(4000);

	std::map<std::string, controlplane::base::acl_t> acls{{"", std::move(fw)}};
	acl::result_t result;
	acl::compile(acls, {{1, {{true, "vlan1"}}}}, result);
}

TEST(ACL, Counters)
{
	auto fw = make_default_acl();
	fw.firewall = R"({
		":BEGIN":[{"filter":{"direction":"in"},"nextSection":":IN","id":1}],
		":IN":[
			{"filter":{"source":["1.2.3.4"]},"nextSection":":A_IN","id":2},
			{"filter":{"source":["1.2.3.6"]},"nextSection":":A_IN","id":3},
			{"nextModule":"drop","id":4}
		],
		":A_IN":[
			{"filter":{"source":["1.2.3.4"],"protocol":{"type":"tcp","destination":[80]}},"id":5},
			{"filter":{"source":["1.2.3.5"],"protocol":{"type":"tcp","destination":[80]}},"id":6},
			{"nextModule":"drop","id":7}
		]
	})"_json;

	std::map<std::string, controlplane::base::acl_t> acls{{"", std::move(fw)}};
	acl::result_t result;
	acl::compile(acls, {{1, {{true, "vlan1"}}}}, result);

	auto& ids_map = result.ids_map;
	auto& t = result.table2;
	ASSERT_EQ(ids_map.size(), 5);
	for (auto it : t)
	{
		EXPECT_THAT(it.second.counter_id, ::testing::Ge(1));
		EXPECT_THAT(it.second.counter_id, ::testing::Lt(5));
	}
	EXPECT_THAT(ids_map[0], ::testing::ElementsAre());
	EXPECT_THAT(ids_map[1], ::testing::ElementsAre(1, 3, 7));
	EXPECT_THAT(ids_map[2], ::testing::ElementsAre(1, 2, 7));
	EXPECT_THAT(ids_map[3], ::testing::ElementsAre(1, 2, 5));
	EXPECT_THAT(ids_map[4], ::testing::ElementsAre(1, 4));
}

TEST(ACL, OrderDeny)
{
	auto fw = make_default_acl();
	fw.firewall = R"({
		":BEGIN":[
			{"filter":{"direction":"in"}, "nextModule":"drop","id":1},
			{"filter":{"direction":"in", "source":["1.2.3.4"]}, "id":2}
		]
	})"_json;

	std::map<std::string, controlplane::base::acl_t> acls{{"", std::move(fw)}};
	acl::result_t result;
	acl::compile(acls, {{1, {{true, "vlan1"}}}}, result);

	auto& ids_map = result.ids_map;
	auto& t = result.table2;
	ASSERT_EQ(t.size(), 1);
	ASSERT_EQ(ids_map.size(), 2);
	for (auto it : t)
	{
		EXPECT_THAT(it.second.type, ::testing::Eq(common::globalBase::eFlowType::drop));
	}
	EXPECT_THAT(ids_map[0], ::testing::ElementsAre());
	EXPECT_THAT(ids_map[1], ::testing::ElementsAre(1));
}

TEST(ACL, OrderAllow)
{
	auto fw = make_default_acl();
	fw.firewall = R"({
		":BEGIN":[
			{"filter":{"direction":"in", "source":["1.2.3.4"]}, "id":1},
			{"filter":{"direction":"in"}, "nextModule":"drop","id":2}
		]
	})"_json;

	std::map<std::string, controlplane::base::acl_t> acls{{"", std::move(fw)}};
	acl::result_t result;
	acl::compile(acls, {{1, {{true, "vlan1"}}}}, result);

	auto& ids_map = result.ids_map;
	auto& t = result.table2;
	ASSERT_EQ(t.size(), 2);
	ASSERT_EQ(ids_map.size(), 3);

	EXPECT_THAT(t[0].second.type, ::testing::Eq(common::globalBase::eFlowType::route));
	EXPECT_THAT(t[1].second.type, ::testing::Eq(common::globalBase::eFlowType::drop));

	EXPECT_THAT(ids_map[0], ::testing::ElementsAre());
	EXPECT_THAT(ids_map[1], ::testing::ElementsAre(1));
	EXPECT_THAT(ids_map[2], ::testing::ElementsAre(2));
}

TEST(ACL, RouterFW)
{
	auto fw0 = make_default_acl(1);
	fw0.firewall = nlohmann::json::parse(std::ifstream(get_data_path("firewall.yanet-in.m4.conf")), nullptr, false);

	auto fw1 = make_default_acl(2);
	fw1.firewall = nlohmann::json::parse(std::ifstream(get_data_path("firewall.yanet-out.m4.conf")), nullptr, false);

	std::map<std::string, controlplane::base::acl_t> acls{{"acl0", std::move(fw0)}, {"acl1", std::move(fw1)}};
	acl::result_t result;
	acl::compile(acls, {{1, {{true, "vlan1"}}}, {2, {{true, "vlan2"}}}}, result);
}

TEST(ACL, Via)
{
	auto fw = make_default_acl();
	fw.firewall = R"({
		":BEGIN":[
			{"filter":{"direction":"in", "source":["1.2.3.4"]}, "via": ["port0"], "id":1},
			{"filter":{"direction":"in"}, "nextModule":"drop","id":2}
		]
	})"_json;

	std::map<std::string, controlplane::base::acl_t> acls{{"acl0", std::move(fw)}};
	acl::result_t result;
	acl::compile(acls, {{1, {{true, "port0"}, {true, "port1"}}}}, result);

	const auto& t2 = result.table2;
	ASSERT_EQ(t2.size(), 3);
	EXPECT_THAT(std::get<1>(t2[0].first), ::testing::Eq(3));
	EXPECT_THAT(t2[0].second.type, ::testing::Eq(common::globalBase::eFlowType::drop));
	EXPECT_THAT(t2[0].second.counter_id, ::testing::Eq(1));

	EXPECT_THAT(std::get<1>(t2[1].first), ::testing::Eq(2));
	EXPECT_THAT(t2[1].second.type, ::testing::Eq(common::globalBase::eFlowType::route));
	EXPECT_THAT(t2[1].second.counter_id, ::testing::Eq(2));

	EXPECT_THAT(std::get<1>(t2[2].first), ::testing::Eq(1));
	EXPECT_THAT(t2[2].second.type, ::testing::Eq(common::globalBase::eFlowType::drop));
	EXPECT_THAT(t2[2].second.counter_id, ::testing::Eq(3));

	auto& ids_map = result.ids_map;
	ASSERT_EQ(ids_map.size(), 4);
	EXPECT_THAT(ids_map[0], ::testing::ElementsAre());
	EXPECT_THAT(ids_map[1], ::testing::ElementsAre(2));
	EXPECT_THAT(ids_map[2], ::testing::ElementsAre(1));
	EXPECT_THAT(ids_map[3], ::testing::ElementsAre(2));

	auto& ifaces = result.in_iface_map;
	ASSERT_EQ(ifaces.size(), 2);
	EXPECT_THAT(ifaces["port0"], 1);
	EXPECT_THAT(ifaces["port1"], 2);

	auto& acl_map = result.acl_map;
	ASSERT_EQ(acl_map.size(), 1);
	EXPECT_THAT(acl_map[1], ::testing::ElementsAre(1, 2));
}

TEST(ACL, ViaOut)
{
	auto fw = make_default_acl();
	fw.firewall = R"({
		":BEGIN":[
			{"filter":{"direction":"out", "source":["1.2.3.4"]}, "via": ["port0"], "id":1},
			{"filter":{"direction":"out", "source":["1.2.3.5"]}, "via": ["port1"], "id":1},
			{"filter":{"direction":"out"}, "nextModule":"drop","id":2}
		]
	})"_json;

	std::map<std::string, controlplane::base::acl_t> acls{{"acl0", std::move(fw)}};
	acl::result_t result;
	acl::compile(acls, {{1, {{false, "port0"}, {false, "port1"}, {false, "port2"}, {false, "port3"}}}}, result);

	const auto& t2 = result.table2;
	ASSERT_EQ(t2.size(), 5);
	EXPECT_THAT(std::get<1>(t2[0].first), ::testing::Eq(5));
	EXPECT_THAT(t2[0].second.type, ::testing::Eq(common::globalBase::eFlowType::drop));
	EXPECT_THAT(t2[0].second.counter_id, ::testing::Eq(1));

	EXPECT_THAT(std::get<1>(t2[1].first), ::testing::Eq(4));
	EXPECT_THAT(t2[1].second.type, ::testing::Eq(common::globalBase::eFlowType::logicalPort_egress));
	EXPECT_THAT(t2[1].second.counter_id, ::testing::Eq(2));

	EXPECT_THAT(std::get<1>(t2[2].first), ::testing::Eq(3));
	EXPECT_THAT(t2[2].second.type, ::testing::Eq(common::globalBase::eFlowType::drop));
	EXPECT_THAT(t2[2].second.counter_id, ::testing::Eq(3));

	auto& ids_map = result.ids_map;
	ASSERT_EQ(ids_map.size(), 6);
	EXPECT_THAT(ids_map[0], ::testing::ElementsAre());
	EXPECT_THAT(ids_map[1], ::testing::ElementsAre(2));
	EXPECT_THAT(ids_map[2], ::testing::ElementsAre(1));
	EXPECT_THAT(ids_map[3], ::testing::ElementsAre(2));

	auto& ifaces = result.out_iface_map;
	ASSERT_EQ(ifaces.size(), 4);
	EXPECT_THAT(ifaces["port0"], 1);
	EXPECT_THAT(ifaces["port1"], 2);
	EXPECT_THAT(ifaces["port2"], 3);
	EXPECT_THAT(ifaces["port3"], 3);
}

TEST(ACL, Lookup)
{
	auto fw = make_default_acl();
	fw.firewall = R"({
		":BEGIN":[{"nextSection":":ALL","id":22}],
		":ALL":[
			{"filter":{"direction":"out", "source":["1.2.3.4"]}, "via": ["port0"], "id":1},
			{"filter":{"direction":"out", "source":["1.2.3.5"]}, "via": ["port1"], "id":2},
			{"filter":{"direction":"out"}, "nextModule":"drop","id":3},
			{"filter":{"direction":"in"},"id":4}
		]
	})"_json;

	std::map<std::string, controlplane::base::acl_t> acls{{"acl0", std::move(fw)}};

	auto ret = acl::unwind(acls, {{1, {{false, "port0"}, {false, "port1"}, {false, "port2"}, {false, "port3"}, {true, "port0"}}}},
	                   {},
	                   {},
	                   {},
	                   {},
	                   {},
	                   {},
	                   {},
	                   {},
	                   {},
	                   {});
	ASSERT_EQ(ret.size(), 6);

	auto stringify = [] (auto& v) { return std::apply([]( auto... e ){ return ( ((e ? *e : "any") + "|") + ... ); }, v );};

	EXPECT_THAT(stringify(ret[0]), ::testing::Eq("port0 |0|any|any|any|any|any|any|any|false|15(0)|22, 4|"));
	EXPECT_THAT(stringify(ret[1]), ::testing::Eq("port2 port3 |1|any|any|any|any|any|any|any|false|0(0)|22, 3|"));
	EXPECT_THAT(stringify(ret[2]), ::testing::Eq("port1 |1|1.2.3.5/255.255.255.255|any|any|any|any|any|any|false|21(0)|22, 2|"));
	EXPECT_THAT(stringify(ret[3]), ::testing::Eq("port1 |1|any|any|any|any|any|any|any|false|0(0)|22, 3|"));
	EXPECT_THAT(stringify(ret[4]), ::testing::Eq("port0 |1|1.2.3.4/255.255.255.255|any|any|any|any|any|any|false|21(0)|22, 1|"));
	EXPECT_THAT(stringify(ret[5]), ::testing::Eq("port0 |1|any|any|any|any|any|any|any|false|0(0)|22, 3|"));
}

TEST(ACL, DefaultAction)
{
	auto fw = make_default_acl();
	fw.firewall = R"({
		":BEGIN":[
			{"filter":{"direction":"in", "source":["1.2.3.4"], "protocol":{"type":"icmp"}}, "id":1}
		]
	})"_json;

	std::map<std::string, controlplane::base::acl_t> acls{{"", std::move(fw)}};

	auto ret = acl::unwind(acls, {{1, {{true, "vlan1"}, {false, "vlan1"}}}},
	                   {},
	                   {},
	                   {},
	                   {},
	                   {},
	                   {},
	                   {},
	                   {},
	                   {},
	                   {});
	ASSERT_EQ(ret.size(), 3);

	auto stringify = [] (auto& v) { return std::apply([]( auto... e ){ return ( ((e ? *e : "any") + "|") + ... ); }, v );};

	EXPECT_THAT(stringify(ret[0]), ::testing::Eq("vlan1 |0|1.2.3.4/255.255.255.255|any|any|1|any|any|any|false|15(0)|1|"));
	EXPECT_THAT(stringify(ret[1]), ::testing::Eq("vlan1 |0|any|any|any|any|any|any|any|false|15(0)||"));
	EXPECT_THAT(stringify(ret[2]), ::testing::Eq("vlan1 |1|any|any|any|any|any|any|any|false|21(0)||"));

	acl::result_t result;
	acl::compile(acls, {{1, {{true, "vlan1"}, {false, "vlan1"}}}}, result);

	auto& ids_map = result.ids_map;
	auto& t = result.table2;
	ASSERT_EQ(t.size(), 3);
	ASSERT_EQ(ids_map.size(), 2);

	EXPECT_THAT(t[0].second.type, ::testing::Eq(common::globalBase::eFlowType::route));
	EXPECT_THAT(t[1].second.type, ::testing::Eq(common::globalBase::eFlowType::route));
	EXPECT_THAT(t[2].second.type, ::testing::Eq(common::globalBase::eFlowType::logicalPort_egress));

	EXPECT_THAT(ids_map[0], ::testing::ElementsAre());
	EXPECT_THAT(ids_map[1], ::testing::ElementsAre(1));
}


} // namespace
