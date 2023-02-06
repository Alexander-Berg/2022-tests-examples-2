package calculator

import (
	"fmt"
	"sort"
	"strconv"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/suite"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/noc/susanin/internal/logging"
	"a.yandex-team.ru/noc/susanin/internal/zk"
)

type IgpIndexTestSuite struct {
	suite.Suite
	topologies []*zk.Topology
	indexes    []igpIndex
	logger     log.Logger
}

func (suite *IgpIndexTestSuite) SetupTest() {
	var nodes []zk.Node
	for id := 0; id < 10; id++ {
		nodes = append(nodes, zk.Node{
			RouterID: strconv.Itoa(id),
			Name:     "test_router_" + strconv.Itoa(id),
		})
	}
	logger, err := logging.NewLogger(&logging.Config{
		Level:    log.DebugLevel,
		Encoding: "console",
		Sinks:    []string{"stderr"},
	})
	if err == nil {
		suite.logger = logger
	}

	topologyGenerators := []func(nodes []zk.Node) (*zk.Topology, igpIndex){
		generateTopology0,
		generateTopology1,
		generateTopology2,
		generateTopology3,
	}
	for _, topologyGenerator := range topologyGenerators {
		topology, index := topologyGenerator(nodes)
		suite.topologies = append(suite.topologies, topology)
		suite.indexes = append(suite.indexes, index)
	}
}

func (suite *IgpIndexTestSuite) TestIGPIndex() {
	assert.True(suite.T(), suite.logger != nil, "failed to setup logger")
	for id, topology := range suite.topologies {
		topologyIndex := buildTopologyIndex(topology)
		igpIndex := buildIGPIndex(zk.TraceSettings{}, topologyIndex, suite.logger)
		assert.True(suite.T(), igpIndexEqual(suite.indexes[id], igpIndex),
			"topology №"+strconv.Itoa(id)+" test failed")
	}
}

func TestSuite(t *testing.T) {
	suite.Run(t, new(IgpIndexTestSuite))
}

// Two nodes with a link
func generateTopology0(nodes []zk.Node) (*zk.Topology, igpIndex) {
	var links []zk.Link
	links = append(links,
		generateTestLink(0, 0, 1, 1))
	topology := zk.Topology{
		Revision: "test_topology_0",
		Nodes:    nodes,
		Links:    links,
	}
	index := make(igpIndex)
	index[&nodes[0]] = make(map[*zk.Node]igpPath)
	index[&nodes[0]][&nodes[1]] = generateIGPPath(0, 1, 1, nodes, links, [][][]int{{{0}}})
	return &topology, index
}

// Two nodes with a double link
func generateTopology1(nodes []zk.Node) (*zk.Topology, igpIndex) {
	var links []zk.Link
	links = append(links,
		generateTestLink(0, 0, 1, 1),
		generateTestLink(1, 0, 1, 1))
	topology := zk.Topology{
		Revision: "test_topology_1",
		Nodes:    nodes,
		Links:    links,
	}
	index := make(igpIndex)
	index[&nodes[0]] = make(map[*zk.Node]igpPath)
	index[&nodes[0]][&nodes[1]] = generateIGPPath(0, 1, 1, nodes, links,
		[][][]int{{{0, 1}}})
	return &topology, index
}

// Triangle topology with double links
func generateTopology2(nodes []zk.Node) (*zk.Topology, igpIndex) {
	var links []zk.Link
	links = append(links,
		generateTestLink(0, 0, 1, 1),
		generateTestLink(1, 0, 1, 3),
		generateTestLink(2, 0, 2, 2),
		generateTestLink(3, 2, 0, 2),
		generateTestLink(4, 2, 1, 3),
		generateTestLink(5, 2, 1, 3))
	topology := zk.Topology{
		Revision: "test_topology_2",
		Nodes:    nodes,
		Links:    links,
	}
	index := make(igpIndex)
	index[&nodes[0]] = make(map[*zk.Node]igpPath)
	index[&nodes[2]] = make(map[*zk.Node]igpPath)
	index[&nodes[0]][&nodes[1]] = generateIGPPath(0, 1, 1, nodes, links, [][][]int{{{0}}})
	index[&nodes[0]][&nodes[2]] = generateIGPPath(0, 2, 2, nodes, links, [][][]int{{{2}}})
	index[&nodes[2]][&nodes[0]] = generateIGPPath(2, 0, 2, nodes, links, [][][]int{{{3}}})
	index[&nodes[2]][&nodes[1]] = generateIGPPath(2, 1, 3, nodes, links, [][][]int{{{4, 5}}, {{3}, {0}}})
	return &topology, index
}

// Cycle on four nodes with a bridge
func generateTopology3(nodes []zk.Node) (*zk.Topology, igpIndex) {
	var links []zk.Link
	links = append(links,
		generateTestLink(0, 0, 1, 100),
		generateTestLink(1, 0, 1, 300),
		generateTestLink(2, 1, 2, 200),
		generateTestLink(3, 1, 2, 200),
		generateTestLink(4, 2, 3, 400),
		generateTestLink(5, 3, 2, 400),
		generateTestLink(6, 1, 3, 600),
		generateTestLink(7, 0, 3, 200),
		generateTestLink(8, 3, 0, 100))
	topology := zk.Topology{
		Revision: "test_topology_0",
		Nodes:    nodes,
		Links:    links,
	}
	index := make(igpIndex)
	index[&nodes[0]] = make(map[*zk.Node]igpPath)
	index[&nodes[1]] = make(map[*zk.Node]igpPath)
	index[&nodes[2]] = make(map[*zk.Node]igpPath)
	index[&nodes[3]] = make(map[*zk.Node]igpPath)

	index[&nodes[0]][&nodes[1]] = generateIGPPath(0, 1, 100, nodes, links, [][][]int{{{0}}})
	index[&nodes[0]][&nodes[2]] = generateIGPPath(0, 2, 300, nodes, links, [][][]int{{{0}, {2, 3}}})
	index[&nodes[0]][&nodes[3]] = generateIGPPath(0, 3, 200, nodes, links, [][][]int{{{7}}})

	index[&nodes[1]][&nodes[0]] = generateIGPPath(1, 0, 700, nodes, links,
		[][][]int{{{6}, {8}}, {{2, 3}, {4}, {8}}})
	index[&nodes[1]][&nodes[2]] = generateIGPPath(1, 2, 200, nodes, links, [][][]int{{{2, 3}}})
	index[&nodes[1]][&nodes[3]] = generateIGPPath(1, 3, 600, nodes, links, [][][]int{{{2, 3}, {4}}, {{6}}})

	index[&nodes[2]][&nodes[0]] = generateIGPPath(2, 0, 500, nodes, links, [][][]int{{{4}, {8}}})
	index[&nodes[2]][&nodes[1]] = generateIGPPath(2, 1, 600, nodes, links, [][][]int{{{4}, {8}, {0}}})
	index[&nodes[2]][&nodes[3]] = generateIGPPath(2, 3, 400, nodes, links, [][][]int{{{4}}})

	index[&nodes[3]][&nodes[0]] = generateIGPPath(3, 0, 100, nodes, links, [][][]int{{{8}}})
	index[&nodes[3]][&nodes[1]] = generateIGPPath(3, 1, 200, nodes, links, [][][]int{{{8}, {0}}})
	index[&nodes[3]][&nodes[2]] = generateIGPPath(3, 2, 400, nodes, links,
		[][][]int{{{8}, {0}, {2, 3}}, {{5}}})
	return &topology, index
}

func generateTestLink(linkNum, source, destination int, metric uint32) zk.Link {
	return zk.Link{
		Name:           "test_link_" + strconv.Itoa(linkNum),
		LocalRouterID:  strconv.Itoa(source),
		RemoteRouterID: strconv.Itoa(destination),
		IGPMetric:      metric,
		Bandwidth:      1.0,
	}
}

// generate igpPath by list of links and list of flows of numbers of links from links
func generateIGPPath(source, destination int, metric uint32, nodes []zk.Node, links []zk.Link, routesLinks [][][]int) igpPath {
	var routes []igpRoute
	for _, flowListByNum := range routesLinks {
		var route igpRoute
		for _, flowByNum := range flowListByNum {
			var flow igpFlow
			sourceRouterNum, _ := strconv.Atoi(links[flowByNum[0]].LocalRouterID)
			remoteRouterNum, _ := strconv.Atoi(links[flowByNum[0]].RemoteRouterID)
			flow.source = &nodes[sourceRouterNum]
			flow.destination = &nodes[remoteRouterNum]
			flow.metric = links[flowByNum[0]].IGPMetric
			flow.links = make(map[string]*zk.Link)
			for _, linkNum := range flowByNum {
				flow.links[links[linkNum].Name] = &links[linkNum]
			}
			route = append(route, flow)
		}
		routes = append(routes, route)
	}
	return igpPath{
		source:      &nodes[source],
		destination: &nodes[destination],
		metric:      metric,
		routes:      routes,
	}
}

func getSortedNodesFromMap[T any](nodeMap map[*zk.Node]T) []*zk.Node {
	var nodes []*zk.Node
	for node := range nodeMap {
		nodes = append(nodes, node)
	}
	sort.SliceStable(nodes, sliceNodeLess(nodes))
	return nodes
}

func listEqual[T comparable](listA, listB []T) bool {
	if len(listA) != len(listB) {
		return false
	}
	for idA := range listA {
		if listA[idA] != listB[idA] {
			return false
		}
	}
	return true
}

func igpFlowToString(flow igpFlow) string {
	res := flow.source.RouterID + ";" + flow.destination.RouterID + ";" + fmt.Sprint(flow.metric) + "#"

	var linkNames []string
	for linkName := range flow.links {
		linkNames = append(linkNames, linkName)
	}
	sort.Strings(linkNames)

	for _, linkName := range linkNames {
		res += linkName + ":" + linkToString(flow.links[linkName]) + ";"
	}
	return res
}

func igpFlowListToString(flowList []igpFlow) string {
	var flowListStr []string

	for _, flow := range flowList {
		flowListStr = append(flowListStr, igpFlowToString(flow))
	}
	sort.Strings(flowListStr)

	return strings.Join(flowListStr[:], "\n")
}

func igpRouteListEqual(routeListA, routeListB []igpRoute) bool {
	if len(routeListA) != len(routeListB) {
		return false
	}
	var routeListAStr, routeListBStr []string
	for _, route := range routeListA {
		routeListAStr = append(routeListAStr, igpFlowListToString(route))
	}
	for _, route := range routeListB {
		routeListBStr = append(routeListBStr, igpFlowListToString(route))
	}
	sort.Strings(routeListAStr)
	sort.Strings(routeListBStr)
	return listEqual(routeListAStr, routeListBStr)
}

func igpPathEqual(pathA, pathB igpPath) bool {
	if pathA.source != pathB.source {
		return false
	}
	if pathA.destination != pathB.destination {
		return false
	}
	if pathA.metric != pathB.metric {
		return false
	}
	if !igpRouteListEqual(pathA.routes, pathB.routes) {
		return false
	}
	return true
}

func igpIndexEqual(indexA, indexB igpIndex) bool {
	sourceNodesA, sourceNodesB := getSortedNodesFromMap(indexA), getSortedNodesFromMap(indexB)
	if !listEqual(sourceNodesA, sourceNodesB) {
		return false
	}
	for _, srcNode := range sourceNodesA {
		destNodesA, destNodesB := getSortedNodesFromMap(indexA[srcNode]), getSortedNodesFromMap(indexB[srcNode])
		if !listEqual(destNodesA, destNodesB) {
			return false
		}
		for _, destNode := range destNodesA {
			if !igpPathEqual(indexA[srcNode][destNode], indexB[srcNode][destNode]) {
				return false
			}
		}
	}
	return true
}
