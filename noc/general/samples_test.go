package parser

// items
const (
	sampleMacroOneWord             = "_YANDEXNETS_"
	sampleMacroTwoWords            = "_NOC_NETS_"
	sampleMacroMultipleUnderscores = "_A__B_C_____D_"

	invalidMacroMissingFirstUnderscore = "YANDEXNETS_"
	invalidMacroMissingLastUnderscore  = "_YANDEXNETS"
	invalidMacroMissingBothUnderscores = "YANDEXNETS"
	invalidMacroEmptyName              = "__"
	invalidMacroInvalidSymbols         = "_a!@_b98_d#$_"

	sampleIPv4         = "192.0.2.1"
	sampleIPv4Mapped   = "::ffff:" + sampleIPv4
	sampleBackboneIPv6 = "2a02:6b8:c00::"
	sampleFastboneIPv6 = "2a02:6b8:fc00::"
	sampleIPv6         = "2a02:5180::1509:185:71:76:17"
	sampleIPv6Full     = "2a02:06b8:0c00:0000:0000:0000:0000:0000"

	invalidIPv4Mapped         = ":ffff:" + sampleIPv4
	invalidIPv6TooSmall       = "2a02:6b8:c00:0000"
	invalidIPv6InvalidSymbols = "2a02:06b8:0c00:000k::"

	sampleIPv4Net         = sampleIPv4 + "/12"
	sampleIPv4MappedNet   = sampleIPv4Mapped + "/80"
	sampleIPv6Net         = sampleIPv6 + "/40"
	sampleIPv6BackboneNet = sampleBackboneIPv6 + "/40"
	sampleIPv6FastboneNet = sampleFastboneIPv6 + "/40"
	sampleIPv6FullNet     = sampleIPv6Full + "/40"

	invalidIPv6NetTwoMasks     = sampleIPv6Net + "/16"
	invalidIPv6NetInvalidIP    = invalidIPv6InvalidSymbols + "/40"
	invalidIPv6NetMaskTooBig   = sampleIPv6 + "/129"
	invalidIPv6NetMaskNegative = sampleIPv6 + "/-1"
	invalidIPv6NetMaskNotInt   = sampleIPv6 + "/ff"

	sampleProjectIDShort             = "abcd"
	sampleProjectIDLong              = "10b9936"
	sampleProjectIDSecured           = "8000f800"
	sampleProjectIDRangeShort        = "f800/23"
	sampleProjectIDRangeLong         = "1000000/16"
	sampleProjectIDRangeLowerNotBase = "f800/20"

	invalidProjectIDIPLike            = "010b:9936"
	invalidProjectIDEndFF             = "010b12ff"
	invalidProjectIDTooBig            = "100000000"
	invalidProjectIDRangeTwoMasks     = sampleProjectIDRangeLong + "/4"
	invalidProjectIDRangeMaskTooBig   = sampleProjectIDLong + "/40"
	invalidProjectIDRangeMaskNegative = sampleProjectIDShort + "/-1"
	invalidProjectIDRangeMaskNotInt   = sampleProjectIDLong + "/f"

	sampleProjectBackbone      = sampleProjectIDShort + "@" + sampleIPv6BackboneNet
	sampleProjectFastbone      = sampleProjectIDLong + "@" + sampleIPv6FastboneNet
	sampleProjectSecured       = sampleProjectIDSecured + "@" + sampleIPv6FastboneNet
	sampleProjectRangeBackbone = sampleProjectIDRangeLong + "@" + sampleIPv6BackboneNet

	invalidProjectMultipleIDs     = sampleProjectIDShort + "@" + sampleProjectIDLong + "@" + sampleIPv6BackboneNet
	invalidProjectInvalidID       = invalidProjectIDRangeMaskTooBig + "@" + sampleIPv6FastboneNet
	invalidProjectInvalidNet      = sampleProjectIDRangeLong + "@" + sampleBackboneIPv6
	invalidProjectInsufficientNet = sampleProjectIDLong + "@" + sampleIPv6Net

	sampleHostBasic          = "example.net"
	sampleHostSpecialSymbols = "exa!mple.net"
	sampleHostReal           = "mk8s-master-catcfrjupce9sq1np9fp.ycp.cloud.yandex.net"

	invalidHostInvalidURL = ":example.net"
	invalidHostNoDomain   = "example"
	invalidHostIsRelPath  = "/example.net"
	invalidHostHasSchema  = "https://example.net"
	invalidHostHasRelPath = "example.net/go"
	invalidHostHasParams  = "example.net?a=3"
	invalidHostHasHash    = "example.net#go"
)

// weights
// keep these consistent with the samples above
const (
	ipWeight = "1"

	sampleIPv4NetWeight       = "1048576"
	sampleIPv4MappedNetWeight = "281474976710656"
	sampleIPv6NetWeight       = "309485009821345068724781056"

	singleProjectIDWeight                  = "72057594037927936"
	sampleProjectIDRangeShortWeight        = "36893488147419103232"
	sampleProjectIDRangeLongWeight         = "4722366482869645213696"
	sampleProjectIDRangeLowerNotBaseWeight = "295147905179352825856"

	sampleSingleProjectWeight        = singleProjectIDWeight
	sampleProjectRangeBackboneWeight = sampleProjectIDRangeLongWeight

	hostWeight = "1"
)

// info (parsing results)
// keep these consistent with the samples above
var (
	nilMacroInfo     = (*Macro)(nil)
	nilIPInfo        = (*IP)(nil)
	nilNetInfo       = (*Net)(nil)
	nilProjectIDInfo = (*ProjectID)(nil)
	nilProjectInfo   = (*Project)(nil)
	nilHostInfo      = (*Host)(nil)

	sampleMacroOneWordInfo = &Macro{
		initString: sampleMacroOneWord,
	}
	sampleMacroTwoWordsInfo = &Macro{
		initString: sampleMacroTwoWords,
	}
	sampleMacroMultipleUnderscoresInfo = &Macro{
		initString: sampleMacroMultipleUnderscores,
	}

	sampleIPv4Info = &IP{
		initString: sampleIPv4,

		ipType: IPv4,
	}
	sampleIPv4MappedInfo = &IP{
		initString: sampleIPv4Mapped,

		ipType: IPv4Mapped,
	}
	sampleBackboneIPv6Info = &IP{
		initString: sampleBackboneIPv6,

		ipType: IPv6,
	}
	sampleFastboneIPv6Info = &IP{
		initString: sampleFastboneIPv6,

		ipType: IPv6,
	}
	sampleIPv6Info = &IP{
		initString: sampleIPv6,

		ipType: IPv6,
	}
	sampleIPv6FullInfo = &IP{
		initString: sampleIPv6Full,

		ipType: IPv6,
	}

	sampleIPv4NetInfo = &Net{
		ip:       sampleIPv4Info,
		maskSize: 12,
	}
	sampleIPv4MappedNetInfo = &Net{
		ip:       sampleIPv4MappedInfo,
		maskSize: 80,
	}
	sampleIPv6NetInfo = &Net{
		ip:       sampleIPv6Info,
		maskSize: 40,
	}
	sampleIPv6BackboneNetInfo = &Net{
		ip:       sampleBackboneIPv6Info,
		maskSize: 40,
	}
	sampleIPv6FastboneNetInfo = &Net{
		ip:       sampleFastboneIPv6Info,
		maskSize: 40,
	}
	sampleIPv6FullNetInfo = &Net{
		ip:       sampleIPv6FullInfo,
		maskSize: 40,
	}

	sampleProjectIDShortInfo = &ProjectID{
		baseID:   mustParseUint32FromHex(sampleProjectIDShort),
		maskSize: -1,
	}
	sampleProjectIDLongInfo = &ProjectID{
		baseID:   mustParseUint32FromHex(sampleProjectIDLong),
		maskSize: -1,
	}
	sampleProjectIDSecuredInfo = &ProjectID{
		baseID:   mustParseUint32FromHex(sampleProjectIDSecured),
		maskSize: -1,
	}
	sampleProjectIDRangeShortInfo = &ProjectID{
		baseID:   mustParseUint32FromHex("f800"),
		maskSize: 23,
	}
	sampleProjectIDRangeLongInfo = &ProjectID{
		baseID:   mustParseUint32FromHex("1000000"),
		maskSize: 16,
	}
	sampleProjectIDRangeLowerNotBaseInfo = &ProjectID{
		baseID:   mustParseUint32FromHex("f000"),
		maskSize: 20,
	}

	sampleProjectBackboneInfo = &Project{
		projectID:  sampleProjectIDShortInfo,
		projectNet: sampleIPv6BackboneNetInfo,
	}
	sampleProjectFastboneInfo = &Project{
		projectID:  sampleProjectIDLongInfo,
		projectNet: sampleIPv6FastboneNetInfo,
	}
	sampleProjectSecuredInfo = &Project{
		projectID:  sampleProjectIDSecuredInfo,
		projectNet: sampleIPv6FastboneNetInfo,
	}
	sampleProjectRangeBackboneInfo = &Project{
		projectID:  sampleProjectIDRangeLongInfo,
		projectNet: sampleIPv6BackboneNetInfo,
	}
	invalidProjectInsufficientNetInfo = &Project{
		projectID:  sampleProjectIDLongInfo,
		projectNet: sampleIPv6NetInfo,
	}

	sampleHostBasicInfo = &Host{
		initString: sampleHostBasic,
	}
	sampleHostSpecialSymbolsInfo = &Host{
		initString: sampleHostSpecialSymbols,
	}
	sampleHostRealInfo = &Host{
		initString: sampleHostReal,
	}
)

// projectIDs extra examples
// keep these consistent with the samples above
var (
	sampleProjectIDRangeShortLowerInfo = &ProjectID{
		baseID:   sampleProjectIDRangeShortInfo.baseID,
		maskSize: -1,
	}
	sampleProjectIDRangeShortUpperInfo = &ProjectID{
		baseID:   mustParseUint32FromHex("f9ff"),
		maskSize: -1,
	}

	sampleProjectIDRangeLongLowerInfo = &ProjectID{
		baseID:   sampleProjectIDRangeLongInfo.baseID,
		maskSize: -1,
	}
	sampleProjectIDRangeLongUpperInfo = &ProjectID{
		baseID:   mustParseUint32FromHex("100ffff"),
		maskSize: -1,
	}

	sampleProjectIDRangeLowerNotBaseLowerInfo = &ProjectID{
		baseID:   sampleProjectIDRangeLowerNotBaseInfo.baseID,
		maskSize: -1,
	}
	sampleProjectIDRangeLowerNotBaseUpperInfo = &ProjectID{
		baseID:   mustParseUint32FromHex("ffff"),
		maskSize: -1,
	}

	sampleOuterProjectIDRange = &ProjectID{
		baseID:   mustParseUint32FromHex("1000"),
		maskSize: 20,
	}
	sampleInnerProjectIDRange = &ProjectID{
		baseID:   mustParseUint32FromHex("1800"),
		maskSize: 24,
	}
	// must not intersect with the two project IDs above
	sampleNoIntersectProjectIDRange = &ProjectID{
		baseID:   mustParseUint32FromHex("100000"),
		maskSize: 16,
	}

	sampleBiggestProjectIDRange = &ProjectID{
		baseID:   0,
		maskSize: 0,
	}
)

// children/projectIDs
var (
	sampleNetMacroChildren = []string{
		sampleIPv6,
		sampleIPv6BackboneNet,
		sampleMacroOneWord,
		sampleFastboneIPv6,
	}
	sampleHostMacroChildren = []string{
		sampleHostBasic,
		sampleMacroOneWord,
		sampleHostSpecialSymbols,
	}
	sampleMixedMacroChildren = []string{
		sampleHostReal,
		sampleMacroOneWord,
		sampleIPv6BackboneNet,
		sampleHostSpecialSymbols,
		sampleIPv6,
	}
	sampleAnyMacroChildren = []string{
		sampleMacroOneWord,
		sampleMacroTwoWords,
	}
	sampleMacroChildrenNoProjectNet = []string{
		sampleHostBasic,
		sampleMacroOneWord,
		sampleBackboneIPv6,
		sampleHostSpecialSymbols,
		sampleMacroTwoWords,
		sampleIPv6,
	}

	invalidMacroChildrenInvalidHost = []string{
		sampleIPv6,
		sampleIPv4Net,
		sampleIPv6FastboneNet,
		invalidHostNoDomain,
	}
	invalidMacroChildrenContainProject = []string{
		sampleMacroOneWord,
		sampleIPv6FastboneNet,
		sampleMacroTwoWords,
		sampleProjectBackbone,
	}
	invalidMacroChildrenMultipleProjectNets = []string{
		sampleIPv6FastboneNet,
		sampleMacroOneWord,
		sampleHostSpecialSymbols,
		sampleIPv6BackboneNet,
	}

	sampleMacroProjectIDs = []string{
		sampleProjectIDShort,
		sampleProjectIDLong,
		sampleProjectIDRangeShort,
		sampleProjectIDRangeLong,
	}

	invalidMacroProjectIDs = []string{
		sampleProjectIDShort,
		invalidProjectIDRangeTwoMasks,
	}

	sampleNetMacroDefinition = []string{
		sampleIPv6,
		sampleIPv4Net,
		sampleMacroOneWord,
		sampleProjectBackbone,
	}
	sampleHostMacroDefinition = []string{
		sampleHostBasic,
		sampleMacroTwoWords,
		sampleHostSpecialSymbols,
	}
	sampleMixedMacroDefinition = []string{
		sampleHostReal,
		sampleMacroOneWord,
		sampleProjectRangeBackbone,
		sampleHostSpecialSymbols,
		sampleIPv6,
	}
	sampleAnyMacroDefinition = []string{
		sampleMacroMultipleUnderscores,
		sampleMacroTwoWords,
	}

	invalidMacroDefinitionInvalidIP = []string{
		sampleHostBasic,
		invalidIPv6InvalidSymbols,
		sampleIPv4Net,
	}
	invalidMacroDefinitionInvalidProject = []string{
		sampleMacroOneWord,
		sampleMacroTwoWords,
		invalidProjectInvalidID,
		sampleProjectBackbone,
	}

	sampleMacroChildrenNoProjects = []string{
		sampleMacroOneWord,
		sampleIPv6,
	}

	// generating definition from description, keep these consistent
	sampleMacroChildrenToTransform = []string{
		sampleIPv6,
		sampleIPv4Net,
		sampleIPv6BackboneNet,
		sampleMacroOneWord,
		sampleFastboneIPv6,
	}
	sampleMacroProjectIDsToTransform = []string{
		sampleProjectIDShort,
	}
	sampleMacroDefinitionTransformed = []string{
		sampleIPv6,
		sampleIPv4Net,
		sampleFastboneIPv6,
		sampleMacroOneWord,
		sampleProjectBackbone,
	}

	// generating description from definition, keep these consistent
	sampleMacroDefinitionToTransform = []string{
		sampleIPv6,
		sampleMacroTwoWords,
		sampleIPv4Net,
		sampleHostBasic,
		sampleMacroOneWord,
		sampleProjectRangeBackbone,
	}
	sampleMacroChildrenTransformed = []string{
		sampleIPv6,
		sampleMacroTwoWords,
		sampleIPv4Net,
		sampleHostBasic,
		sampleMacroOneWord,
		sampleIPv6BackboneNet,
	}
	sampleMacroProjectIDsTransformed = []string{
		sampleProjectIDShort,
		sampleProjectIDRangeLong,
	}
)
