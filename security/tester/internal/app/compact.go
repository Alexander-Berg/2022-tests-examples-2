package app

import (
	"strings"

	"a.yandex-team.ru/security/libs/go/semver"
)

const (
	noticeTooOldOpenSSH = `You are using OpenSSH prior to v8.2. "Sudo forward" configuration may not work properly.`
	noticeNoRSAOpenSSH  = `You are using OpenSSH v8.6+, so RSA keys may be missing in the output. This is the expected temporary behavior, don't panic.`
	noticeTooOldPutty   = `You are using Putty prior to v0.76. Please update it to improve agent/putty performance.`
)

type clientBanner struct {
	Prefixes []string
	Checks   []clientBannerCheck
}

type clientBannerCheck struct {
	Constraints *semver.Constraints
	Banner      string
}

var clientBanners = []clientBanner{
	{
		Prefixes: []string{
			"OpenSSH_for_Windows_",
			"OpenSSH_",
		},
		Checks: []clientBannerCheck{
			{
				Constraints: semver.MustParseConstraint("<8.2.0"),
				Banner:      noticeTooOldOpenSSH,
			},
			{
				Constraints: semver.MustParseConstraint(">=8.6.0"),
				Banner:      noticeNoRSAOpenSSH,
			},
		},
	},
	{
		Prefixes: []string{
			"PuTTY-Release-",
			"PuTTY_Release_",
		},
		Checks: []clientBannerCheck{
			{
				Constraints: semver.MustParseConstraint("<0.76"),
				Banner:      noticeTooOldPutty,
			},
		},
	},
}

func clientCompatNotice(rawBanner string) string {
	for _, banner := range clientBanners {
		rawVersion, ok := hasPrefixes(rawBanner, banner.Prefixes)
		if !ok {
			continue
		}

		if idx := strings.IndexFunc(rawVersion, isNotVersionRune); idx > 0 {
			rawVersion = rawVersion[:idx]
		}

		ver, err := semver.NewVersion(rawVersion)
		if err != nil {
			return ""
		}

		for _, check := range banner.Checks {
			if check.Constraints.Check(ver) {
				return check.Banner
			}
		}

		break
	}

	return ""
}

func isNotVersionRune(r rune) bool {
	return r != '.' && (r < '0' || r > '9')
}

func hasPrefixes(s string, prefixes []string) (string, bool) {
	for _, prefix := range prefixes {
		out := strings.TrimPrefix(s, prefix)
		if out != s {
			return out, true
		}
	}

	return "", false
}
