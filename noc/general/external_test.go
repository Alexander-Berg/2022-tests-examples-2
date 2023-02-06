package diff

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestParseOutput(t *testing.T) {
	output := []byte(`diff -BbNru -x CVS /tmp/valid/rules.inc /tmp/invalid/rules.inc
--- /tmp/valid/rules.inc	2020-10-08 17:17:56.000000000 +0300
+++ /tmp/invalid/rules.inc	2020-10-21 14:08:35.000000000 +0300
@@ -2626,11 +2626,6 @@
 # доступ от маркетных сетей
 -A clusterizer-api.http.yandex.net -p tcp --source { _MARKETNETS_ or _CORBANETS_ } --dport 32697 -j ACCEPT
 
-# =========== api-int.mt.yandex.net ===========
-
-# репорт получает от сервиса музыки результаты поиска или каталога
--A api-int.mt.yandex.net -p tcp --source { _SEARCHSAND_ } --dport 80 -j ACCEPT
-
 # =========== time.maps.yandex.net ===========
 
 # Дырка для чекалки
diff -BbNru -x CVS /tmp/valid/services.yaml /tmp/invalid/services.yaml
--- /tmp/valid/services.yaml	2020-10-21 13:18:37.000000000 +0300
+++ /tmp/invalid/services.yaml	2020-10-21 14:08:35.000000000 +0300
@@ -3616,21 +3616,11 @@
   ips: [2a02:6b8:0:3400::364]
   chain_name: oort-prod.stable.qloud-b
 ---
-billing.mt.yandex.net:
-  ips: [2a02:6b8:0:3400::365]
-  no_mss_fix: true
-  append_rules: [billing-l3.mt.yandex.net]
----
 statistics-api-int.vertis.yandex.net:
   ips: [2a02:6b8:0:3400::366]
   no_mss_fix: true
   chain_name: statistics-api-int.vertis
 ---
-music-web.mt.yandex.net:
-  ips: [2a02:6b8:0:3400::369]
-  no_mss_fix: true
-  append_rules: [l7-nonprod.music.yandex.net]
----
 tv-back-balancer.tst.content.yandex.net:
   ips: [2a02:6b8:0:3400::37b]
   chain_name: tv-back-balancer.tst.content
@@ -3673,13 +3663,6 @@
   ips: [5.255.240.81, 2a02:6b8:0:3400::381]
   no_mss_fix: true
 ---
-api-int.mt.yandex.net:
-  ips: [2a02:6b8:0:3400::382]
----
-music-web-partner.music.yandex.net:
-  ips: [2a02:6b8:0:3400::383]
-  no_mss_fix: true
----
 pers-invite.vs.market.yandex.net:
   ips: [2a02:6b8:0:3400::386]
 ---
`)

	expected := []Unified{
		{
			From: "rules.inc	2020-10-08 17:17:56.000000000 +0300",
			To: "rules.inc	2020-10-21 14:08:35.000000000 +0300",
			Hunks: []*Hunk{
				{
					FromLine: 2626,
					ToLine:   2626,
					Lines: []Line{
						{
							Kind:    Equal,
							Content: "# доступ от маркетных сетей\n",
						},
						{
							Kind:    Equal,
							Content: "-A clusterizer-api.http.yandex.net -p tcp --source { _MARKETNETS_ or _CORBANETS_ } --dport 32697 -j ACCEPT\n",
						},
						{
							Kind:    Equal,
							Content: "\n",
						},
						{
							Kind:    Delete,
							Content: "# =========== api-int.mt.yandex.net ===========\n",
						},
						{
							Kind:    Delete,
							Content: "\n",
						},
						{
							Kind:    Delete,
							Content: "# репорт получает от сервиса музыки результаты поиска или каталога\n",
						},
						{
							Kind:    Delete,
							Content: "-A api-int.mt.yandex.net -p tcp --source { _SEARCHSAND_ } --dport 80 -j ACCEPT\n",
						},
						{
							Kind:    Delete,
							Content: "\n",
						},
						{
							Kind:    Equal,
							Content: "# =========== time.maps.yandex.net ===========\n",
						},
						{
							Kind:    Equal,
							Content: "\n",
						},
						{
							Kind:    Equal,
							Content: "# Дырка для чекалки\n",
						},
					},
				},
			},
		},
		{
			From: "services.yaml	2020-10-21 13:18:37.000000000 +0300",
			To: "services.yaml	2020-10-21 14:08:35.000000000 +0300",
			Hunks: []*Hunk{
				{
					FromLine: 3616,
					ToLine:   3616,
					Lines: []Line{
						{
							Kind:    Equal,
							Content: "  ips: [2a02:6b8:0:3400::364]\n",
						},
						{
							Kind:    Equal,
							Content: "  chain_name: oort-prod.stable.qloud-b\n",
						},
						{
							Kind:    Equal,
							Content: "---\n",
						},
						{
							Kind:    Delete,
							Content: "billing.mt.yandex.net:\n",
						},
						{
							Kind:    Delete,
							Content: "  ips: [2a02:6b8:0:3400::365]\n",
						},
						{
							Kind:    Delete,
							Content: "  no_mss_fix: true\n",
						},
						{
							Kind:    Delete,
							Content: "  append_rules: [billing-l3.mt.yandex.net]\n",
						},
						{
							Kind:    Delete,
							Content: "---\n",
						},
						{
							Kind:    Equal,
							Content: "statistics-api-int.vertis.yandex.net:\n",
						},
						{
							Kind:    Equal,
							Content: "  ips: [2a02:6b8:0:3400::366]\n",
						},
						{
							Kind:    Equal,
							Content: "  no_mss_fix: true\n",
						},
						{
							Kind:    Equal,
							Content: "  chain_name: statistics-api-int.vertis\n",
						},
						{
							Kind:    Equal,
							Content: "---\n",
						},
						{
							Kind:    Delete,
							Content: "music-web.mt.yandex.net:\n",
						},
						{
							Kind:    Delete,
							Content: "  ips: [2a02:6b8:0:3400::369]\n",
						},
						{
							Kind:    Delete,
							Content: "  no_mss_fix: true\n",
						},
						{
							Kind:    Delete,
							Content: "  append_rules: [l7-nonprod.music.yandex.net]\n",
						},
						{
							Kind:    Delete,
							Content: "---\n",
						},
						{
							Kind:    Equal,
							Content: "tv-back-balancer.tst.content.yandex.net:\n",
						},
						{
							Kind:    Equal,
							Content: "  ips: [2a02:6b8:0:3400::37b]\n",
						},
						{
							Kind:    Equal,
							Content: "  chain_name: tv-back-balancer.tst.content\n",
						},
					},
				},
				{
					FromLine: 3673,
					ToLine:   3663,
					Lines: []Line{
						{
							Kind:    Equal,
							Content: "  ips: [5.255.240.81, 2a02:6b8:0:3400::381]\n",
						},
						{
							Kind:    Equal,
							Content: "  no_mss_fix: true\n",
						},
						{
							Kind:    Equal,
							Content: "---\n",
						},
						{
							Kind:    Delete,
							Content: "api-int.mt.yandex.net:\n",
						},
						{
							Kind:    Delete,
							Content: "  ips: [2a02:6b8:0:3400::382]\n",
						},
						{
							Kind:    Delete,
							Content: "---\n",
						},
						{
							Kind:    Delete,
							Content: "music-web-partner.music.yandex.net:\n",
						},
						{
							Kind:    Delete,
							Content: "  ips: [2a02:6b8:0:3400::383]\n",
						},
						{
							Kind:    Delete,
							Content: "  no_mss_fix: true\n",
						},
						{
							Kind:    Delete,
							Content: "---\n",
						},
						{
							Kind:    Equal,
							Content: "pers-invite.vs.market.yandex.net:\n",
						},
						{
							Kind:    Equal,
							Content: "  ips: [2a02:6b8:0:3400::386]\n",
						},
						{
							Kind:    Equal,
							Content: "---\n",
						},
					},
				},
			},
		},
	}

	diff, err := parseOutput(output, "/tmp/valid/", "/tmp/invalid/")

	assert.NoError(t, err)
	assert.Equal(t, expected, diff)
}
