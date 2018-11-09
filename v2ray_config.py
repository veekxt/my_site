import json
import uuid

trans_protocol = ["tcp", "kcp", "ws", "http"]
data_protocol = ["vmess", "shadowsocks", "socks", "http", "server_mtproto"]
in_protocol = ["socks", "http"]
use_tls = ["none", "tls"]

config_from = {
    "trans_protocol": 0,
    "tls": 0,
    "data_protocol": 0,
    "in": [{"route": 0, "type": 0, "port": 1080}, {"route": 1, "type": 1, "port": 1081},
           {"route": 0, "type": 0, "port": 1083}, {"route": 1, "type": 1, "port": 1084}],
    "server": "veekxt.com",
    "server_port": 443,
    "reversed_proxy": 0,
    "ws_path": "veekxtwstest",
    "tls_file": "/pa/to/tls",
    "tls_key": "/pa/to/tls/key"
}

v2ray_config_c = {
    "log": {},
    "api": {},
    "dns": {},
    "stats": {},
    "routing": {},
    "policy": {},
    "reverse": {},
    "inbounds": [],
    "outbounds": [],
    "transport": {},
}

v2ray_config_s = {
    "log": {},
    "api": {},
    "dns": {},
    "stats": {},
    "routing": {},
    "policy": {},
    "reverse": {},
    "inbounds": [],
    "outbounds": [],
    "transport": {},
}

inbounds = v2ray_config_c["inbounds"];
outbounds = v2ray_config_c["outbounds"];
routing = v2ray_config_c["routing"];

for i in config_from["in"]:
    inboud = {
        "port": i["port"],
        "protocol": in_protocol[i["type"]],
        "settings": {},
        "tag": "in-" + str(len(inbounds)),
    }
    if inboud["protocol"] == "socks":
        inboud["settings"] = {
            "auth": "noauth",
            "udp": True
        }
    elif inboud["protocol"] == "http":
        inboud["settings"] = {}
    else:
        print("no that protocol:" + str(inboud["protocol"]))
    inbounds.append(inboud)

outbound = {
    "protocol": data_protocol[config_from["data_protocol"]],
    "settings": {},
    "tag": "out-" + str(len(outbounds)),
    "streamSettings": {
        "network": trans_protocol[config_from["trans_protocol"]],
        "security": use_tls[config_from["tls"]],
    }
}

network = outbound["streamSettings"]["network"]
out_set = outbound["settings"]

data_ps = data_protocol[config_from["data_protocol"]]

vmess_uuid = str(uuid.uuid4())

if data_ps=="vmess":
    out_set["vnext"]=[
            {
                "address": config_from["server"],
                "port": config_from["server_port"],
                "users": [
                    {
                        "id": vmess_uuid
                    }
                ]
            }
        ]
    # todo, other protocol

if network == "tcp":
    outbound["tcpSettings"] = {}
elif network == "kcp":
    outbound["kcpSettings"] = {}
elif network == "ws":
    outbound["wsSettings"] = {
        "path": config_from["ws_path"],
    }
elif network == "http":
    outbound["httpSettings"] = {
        "path": config_from["ws_path"],
    }

outbound["tlsSettings"] = {
    "serverName": "v2ray.com",
}

outbounds.append(outbound)

routing["domainStrategy"] = "IPOnDemand";
routing["rules"] = []

rule = {
    "type": "field",
    "ip": [
        "geoip:private"
    ],
    "outboundTag": "direct"
}

routing["rules"].append(rule)

cn_in_tag = []

for i, c in enumerate(inbounds):
    if config_from["in"][i]["route"] == 1:
        cn_in_tag.append(c["tag"])

if len(cn_in_tag) > 0:
    rule = {
        "type": "field",
        "ip": [
            "geoip:cn"
        ],
        "inboundTag": cn_in_tag,
        "outboundTag": "direct"
    }
    routing["rules"].append(rule)

js = json.dumps(v2ray_config_c, sort_keys=True, indent=2, separators=(',', ':'))
print(js)

# for server!
# certificate = {
#     "keyFile"
# }
#
# // certificate = tmp["tlsSettings"]["certificates"];
