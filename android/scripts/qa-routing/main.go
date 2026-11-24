// Verify the routing section exported by the installed APK using the identical Xray core revision.
// Only DNS answers and diagnostic ruleTag labels are injected. No routing condition is replaced.
package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"

	"github.com/xtls/xray-core/common"
	xnet "github.com/xtls/xray-core/common/net"
	"github.com/xtls/xray-core/common/session"
	"github.com/xtls/xray-core/core"
	"github.com/xtls/xray-core/features/routing"
	rsession "github.com/xtls/xray-core/features/routing/session"
	_ "github.com/xtls/xray-core/main/distro/all"
)

type check struct {
	Name, Host, Network, Want string
	OriginalIP                string `json:",omitempty"`
}

func main() {
	if len(os.Args) != 3 {
		panic("usage: go run . <export-directory> <apk-asset-directory>")
	}
	assetPath, err := filepath.Abs(os.Args[2])
	must(err)
	must(os.Setenv("xray.location.asset", assetPath))
	checks := []check{
		{"WeChat resource", "mmbiz.qpic.cn", "tcp", "direct", ""},
		{"WeChat service", "res.wx.qq.com", "tcp", "direct", ""},
		{"Xiaohongshu image CDN", "sns-img-qc.xhscdn.com", "tcp", "direct", ""},
		{"Xiaohongshu video CDN", "sns-video.xhscdn.net", "tcp", "direct", ""},
		{"Douyin video TCP", "v3.douyinvod.com", "tcp", "direct", ""},
		{"Douyin video QUIC", "v3.douyinvod.com", "udp", "direct", ""},
		{"Bilibili video", "upos.bilivideo.com", "tcp", "direct", ""},
		{"Claude website", "claude.com", "tcp", "proxy", ""},
		{"Claude user content", "files.claudeusercontent.com", "tcp", "proxy", ""},
		{"Claude AI", "claude.ai", "tcp", "proxy", ""},
		{"Claude overrides sniffed mainland IP", "claude.com", "tcp", "proxy", "223.5.5.5"},
		{"Gemini exact domain", "gemini.google.com", "tcp", "proxy", ""},
		{"Gemini full match does not include subdomains", "sub.gemini.google.com", "tcp", "direct", ""},
		{"Mainland IPv4", "223.5.5.5", "tcp", "direct", ""},
		{"Mainland IPv6", "2400:3200::1", "tcp", "direct", ""},
		{"Unmatched domain resolved to mainland", "cn.hbtcp-routing-qa.com", "tcp", "direct", ""},
		{"Unmatched domain resolved overseas", "global.hbtcp-routing-qa.com", "tcp", "proxy", ""},
		{"Unmatched IPv4", "8.8.8.8", "tcp", "proxy", ""},
		{"Unmatched IPv6", "2606:4700:4700::1111", "tcp", "proxy", ""},
		{"Suffix boundary", "qq.com.hbtcp-routing-qa.com", "tcp", "proxy", ""},
		{"LAN IPv4", "192.168.10.20", "tcp", "direct", ""},
		{"LAN IPv6", "fd00::10", "tcp", "direct", ""},
		{"LAN hostname", "printer.local", "tcp", "direct", ""},
	}
	var report []map[string]any
	for _, mode := range []string{"split", "global"} {
		data, err := os.ReadFile(filepath.Join(os.Args[1], mode+"-config.json"))
		must(err)
		var config map[string]any
		must(json.Unmarshal(data, &config))
		// Start only the real router/DNS/outbounds; no host listeners or outside network requests.
		config["inbounds"] = []any{}
		hosts := map[string]any{}
		for _, c := range checks {
			hosts[c.Host] = "8.8.8.8"
		}
		for _, host := range []string{"claude.com", "files.claudeusercontent.com", "claude.ai", "gemini.google.com", "sub.gemini.google.com", "cn.hbtcp-routing-qa.com"} {
			hosts[host] = "223.5.5.5"
		}
		config["dns"] = map[string]any{"hosts": hosts, "servers": []any{}}
		rules := config["routing"].(map[string]any)["rules"].([]any)
		for i, rule := range rules {
			rule.(map[string]any)["ruleTag"] = fmt.Sprintf("generated-rule-%02d", i)
		}
		data, err = json.Marshal(config)
		must(err)
		instance, err := core.StartInstance("json", data)
		must(err)
		router := instance.GetFeature(routing.RouterType()).(routing.Router)
		for _, c := range checks {
			address := xnet.ParseAddress(c.Host)
			network := xnet.Network_TCP
			if c.Network == "udp" {
				network = xnet.Network_UDP
			}
			target := xnet.Destination{Address: address, Port: 443, Network: network}
			outbound := &session.Outbound{Target: target}
			if c.OriginalIP != "" {
				outbound.RouteTarget = target
				outbound.Target.Address = xnet.ParseAddress(c.OriginalIP)
			}
			ctx := &rsession.Context{Inbound: &session.Inbound{Tag: "socks"}, Outbound: outbound}
			route, err := router.PickRoute(ctx)
			got, matched := "", ""
			if errors.Is(err, common.ErrNoClue) {
				got = config["outbounds"].([]any)[0].(map[string]any)["tag"].(string)
				matched = "first outbound fallback"
			} else {
				must(err)
				got, matched = route.GetOutboundTag(), route.GetRuleTag()
			}
			want := c.Want
			if mode == "global" {
				want = "proxy"
				if c.Network == "udp" {
					want = "block"
				}
				if c.Name == "LAN IPv4" || c.Name == "LAN IPv6" || c.Name == "LAN hostname" {
					want = "direct"
				}
			}
			if got != want {
				panic(fmt.Sprintf("%s %s: got %s via %s, want %s", mode, c.Name, got, matched, want))
			}
			report = append(report, map[string]any{"mode": mode, "check": c.Name, "host": c.Host, "network": c.Network, "outbound": got, "matched": matched})
		}
		must(instance.Close())
	}
	encoded, err := json.MarshalIndent(report, "", "  ")
	must(err)
	must(os.WriteFile(filepath.Join(os.Args[1], "xray-rule-hits.json"), append(encoded, '\n'), 0644))
	fmt.Printf("PASS: %d actual Xray route decisions\n", len(report))
}

func must(err error) {
	if err != nil {
		panic(err)
	}
}
