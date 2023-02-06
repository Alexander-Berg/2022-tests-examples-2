package config

import (
	"bufio"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestConfig(t *testing.T) {
	text := `# SVC: (9699      ) [rclb] hiring-api.taxi.yandex.net
# LB: (815       ) [vla1-4lb26a-25d.yndx.net] vla1-4lb26a-25d
# VS: (2839890   ) TCP:2a02:6b8:0:3400:0:71d:0:4fb:80
#virtual_server 2a02:6b8:0:3400:0:71d:0:4fb 80 {
virtual_server 183.221.13.12 80 {
        protocol TCP
          
        quorum_up   "/etc/keepalived/quorum.sh up   2a02:6b8:0:3400:0:71d:0:4fb,b-100,1"
        quorum_down "/etc/keepalived/quorum.sh down 2a02:6b8:0:3400:0:71d:0:4fb,b-100,1"
        quorum 1
        hysteresis 0
          
        alpha
        omega
        lvs_method TUN
        lvs_sched wrr
        
        delay_loop 10
        virtualhost hiring-api.taxi.yandex.net
        
        real_server 2a02:6b8:c0f:490a:0:1315:2f20:0 80 {
                # RS: (3139501   ) [rdgw2g7xkpf67xzv.vla.yp-c.yandex.net] 2a02:6b8:c0f:490a:0:1315:2f20:0
                # RS state ID: 299670640
                weight 4

                 HTTP_GET {
                        url {
                                path /
                                status_code 200
 	                               
                        }
                        connect_ip 2a02:6b8:0:3400:0:71d:0:4fb
                        connect_port 80
                        bindto 2a02:6b8:0:300::4:b26a
                        connect_timeout 1
                        fwmark 2274
                        
                        nb_get_retry 1
                        
                        delay_before_retry 1
                
                }
        }
        real_server 2a02:6b8:c15:2889:0:1315:e34e:0 80 {
                # RS: (3181044   ) [taxi-hiring-api-pre-stable-3.vla.yp-c.yandex.net] 2a02:6b8:c15:2889:0:1315:e34e:0
                # RS state ID: 299670639
                weight 10
                
                HTTP_GET {
                        url {
                                path /
                                status_code 200
                                
                        }
                        connect_ip 2a02:6b8:0:3400:0:71d:0:4fb
                        connect_port 80
                        bindto 2a02:6b8:0:300::4:b26a
                        connect_timeout 1
                        fwmark 4919
                        
                        nb_get_retry 1
                        
                        delay_before_retry 1
          
                }
        }
        
}`

	refCfg := []ConfItem{ConfItem{
		File:   "test.cfg",
		Name:   "virtual_server",
		Values: []string{"183.221.13.12", "80"},
		SubItems: []ConfItem{ConfItem{
			File:     "test.cfg",
			Name:     "protocol",
			Values:   []string{"TCP"},
			SubItems: []ConfItem(nil)},
			ConfItem{
				File:     "test.cfg",
				Name:     "quorum_up",
				Values:   []string{"/etc/keepalived/quorum.sh up   2a02:6b8:0:3400:0:71d:0:4fb,b-100,1"},
				SubItems: []ConfItem(nil)},
			ConfItem{
				File:     "test.cfg",
				Name:     "quorum_down",
				Values:   []string{"/etc/keepalived/quorum.sh down 2a02:6b8:0:3400:0:71d:0:4fb,b-100,1"},
				SubItems: []ConfItem(nil)},
			ConfItem{
				File:     "test.cfg",
				Name:     "quorum",
				Values:   []string{"1"},
				SubItems: []ConfItem(nil)},
			ConfItem{File: "test.cfg", Name: "hysteresis", Values: []string{"0"}, SubItems: []ConfItem(nil)},
			ConfItem{File: "test.cfg", Name: "alpha", Values: []string(nil), SubItems: []ConfItem(nil)},
			ConfItem{File: "test.cfg", Name: "omega", Values: []string(nil), SubItems: []ConfItem(nil)},
			ConfItem{File: "test.cfg", Name: "lvs_method", Values: []string{"TUN"}, SubItems: []ConfItem(nil)},
			ConfItem{File: "test.cfg", Name: "lvs_sched", Values: []string{"wrr"}, SubItems: []ConfItem(nil)},
			ConfItem{File: "test.cfg", Name: "delay_loop", Values: []string{"10"}, SubItems: []ConfItem(nil)},
			ConfItem{File: "test.cfg", Name: "virtualhost", Values: []string{"hiring-api.taxi.yandex.net"}, SubItems: []ConfItem(nil)},
			ConfItem{File: "test.cfg", Name: "real_server", Values: []string{"2a02:6b8:c0f:490a:0:1315:2f20:0", "80"}, SubItems: []ConfItem{
				ConfItem{File: "test.cfg", Name: "weight", Values: []string{"4"}, SubItems: []ConfItem(nil)},
				ConfItem{File: "test.cfg", Name: "HTTP_GET", Values: []string(nil), SubItems: []ConfItem{
					ConfItem{File: "test.cfg", Name: "url", Values: []string(nil), SubItems: []ConfItem{
						ConfItem{File: "test.cfg", Name: "path", Values: []string{"/"}, SubItems: []ConfItem(nil)},
						ConfItem{File: "test.cfg", Name: "status_code", Values: []string{"200"}, SubItems: []ConfItem(nil)}}},
					ConfItem{File: "test.cfg", Name: "connect_ip", Values: []string{"2a02:6b8:0:3400:0:71d:0:4fb"}, SubItems: []ConfItem(nil)},
					ConfItem{File: "test.cfg", Name: "connect_port", Values: []string{"80"}, SubItems: []ConfItem(nil)},
					ConfItem{File: "test.cfg", Name: "bindto", Values: []string{"2a02:6b8:0:300::4:b26a"}, SubItems: []ConfItem(nil)},
					ConfItem{File: "test.cfg", Name: "connect_timeout", Values: []string{"1"}, SubItems: []ConfItem(nil)},
					ConfItem{File: "test.cfg", Name: "fwmark", Values: []string{"2274"}, SubItems: []ConfItem(nil)},
					ConfItem{File: "test.cfg", Name: "nb_get_retry", Values: []string{"1"}, SubItems: []ConfItem(nil)},
					ConfItem{File: "test.cfg", Name: "delay_before_retry", Values: []string{"1"}, SubItems: []ConfItem(nil)}}}}},
			ConfItem{File: "test.cfg", Name: "real_server", Values: []string{"2a02:6b8:c15:2889:0:1315:e34e:0", "80"}, SubItems: []ConfItem{
				ConfItem{File: "test.cfg", Name: "weight", Values: []string{"10"}, SubItems: []ConfItem(nil)},
				ConfItem{File: "test.cfg", Name: "HTTP_GET", Values: []string(nil), SubItems: []ConfItem{
					ConfItem{File: "test.cfg", Name: "url", Values: []string(nil), SubItems: []ConfItem{
						ConfItem{File: "test.cfg", Name: "path", Values: []string{"/"}, SubItems: []ConfItem(nil)},
						ConfItem{File: "test.cfg", Name: "status_code", Values: []string{"200"}, SubItems: []ConfItem(nil)}}},
					ConfItem{File: "test.cfg", Name: "connect_ip", Values: []string{"2a02:6b8:0:3400:0:71d:0:4fb"}, SubItems: []ConfItem(nil)},
					ConfItem{File: "test.cfg", Name: "connect_port", Values: []string{"80"}, SubItems: []ConfItem(nil)},
					ConfItem{File: "test.cfg", Name: "bindto", Values: []string{"2a02:6b8:0:300::4:b26a"}, SubItems: []ConfItem(nil)},
					ConfItem{File: "test.cfg", Name: "connect_timeout", Values: []string{"1"}, SubItems: []ConfItem(nil)},
					ConfItem{File: "test.cfg", Name: "fwmark", Values: []string{"4919"}, SubItems: []ConfItem(nil)},
					ConfItem{File: "test.cfg", Name: "nb_get_retry", Values: []string{"1"}, SubItems: []ConfItem(nil)},
					ConfItem{File: "test.cfg", Name: "delay_before_retry", Values: []string{"1"}, SubItems: []ConfItem(nil)}}}}}}}}

	cfg, err := ParseConfig(bufio.NewScanner(strings.NewReader(text)), "", "test.cfg")
	assert.NoError(t, err)
	assert.Equal(t, refCfg, cfg)
}
