#!/usr/bin/env python

""" nl80211_c.py: nl80211 attribute policy definitions

Copyright (C) 2016  Dale V. Patterson (wraith.wireless@yandex.com)

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

Redistribution and use in source and binary forms, with or without modifications,
are permitted provided that the following conditions are met:
 o Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
 o Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
 o Neither the name of the orginal author Dale V. Patterson nor the names of any
   contributors may be used to endorse or promote products derived from this
   software without specific prior written permission.

A port of nla_policy definitions found in nl80211.c to python

"""

__name__ = 'nl80211_c'
__license__ = 'GPLv3'
__version__ = '0.0.3'
__date__ = 'April 2016'
__author__ = 'Dale Patterson'
__maintainer__ = 'Dale Patterson'
__email__ = 'wraith.wireless@yandex.com'
__status__ = 'Production'

import struct
import pyric.net.netlink_h as nlh
import pyric.net.wireless.nl80211_h as nl80211h

#static const struct nla_policy nl80211_policy[NUM_NL80211_ATTR] = {
nl80211_policy = {
    nl80211h.NL80211_ATTR_WIPHY:nlh.NLA_U32,
    nl80211h.NL80211_ATTR_WIPHY_NAME:nlh.NLA_STRING,
    nl80211h.NL80211_ATTR_WIPHY_TXQ_PARAMS:nlh.NLA_NESTED,
    nl80211h.NL80211_ATTR_WIPHY_FREQ:nlh.NLA_U32,
    nl80211h.NL80211_ATTR_WIPHY_CHANNEL_TYPE:nlh.NLA_U32,
    nl80211h.NL80211_ATTR_CHANNEL_WIDTH:nlh.NLA_U32,
    nl80211h.NL80211_ATTR_CENTER_FREQ1:nlh.NLA_U32,
    nl80211h.NL80211_ATTR_CENTER_FREQ2:nlh.NLA_U32,
    nl80211h.NL80211_ATTR_WIPHY_RETRY_SHORT:nlh.NLA_U8,
    nl80211h.NL80211_ATTR_WIPHY_RETRY_LONG:nlh.NLA_U8,
    nl80211h.NL80211_ATTR_WIPHY_FRAG_THRESHOLD:nlh.NLA_U32,
    nl80211h.NL80211_ATTR_WIPHY_RTS_THRESHOLD:nlh.NLA_U32,
    nl80211h.NL80211_ATTR_WIPHY_COVERAGE_CLASS:nlh.NLA_U8,
    #nl80211h.NL80211_ATTR_WIPHY_DYN_ACK:nlh.NLA_FLAG,
    nl80211h.NL80211_ATTR_IFTYPE:nlh.NLA_U32,
    nl80211h.NL80211_ATTR_IFINDEX:nlh.NLA_U32,
    nl80211h.NL80211_ATTR_IFNAME:nlh.NLA_STRING,
    nl80211h.NL80211_ATTR_MAC:nlh.NLA_UNSPEC,
    nl80211h.NL80211_ATTR_PREV_BSSID:nlh.NLA_UNSPEC,
    nl80211h.NL80211_ATTR_KEY:nlh.NLA_NESTED,
    nl80211h.NL80211_ATTR_KEY_DATA:nlh.NLA_UNSPEC,
    nl80211h.NL80211_ATTR_KEY_IDX:nlh.NLA_U8,
    nl80211h.NL80211_ATTR_KEY_CIPHER:nlh.NLA_U32,
    nl80211h.NL80211_ATTR_KEY_DEFAULT:nlh.NLA_FLAG,
    nl80211h.NL80211_ATTR_KEY_SEQ:nlh.NLA_UNSPEC,
    nl80211h.NL80211_ATTR_KEY_TYPE:nlh.NLA_U32,
    nl80211h.NL80211_ATTR_BEACON_INTERVAL:nlh.NLA_U32,
    nl80211h.NL80211_ATTR_DTIM_PERIOD:nlh.NLA_U32,
    nl80211h.NL80211_ATTR_BEACON_HEAD:nlh.NLA_UNSPEC,
    nl80211h.NL80211_ATTR_BEACON_TAIL:nlh.NLA_UNSPEC,
    nl80211h.NL80211_ATTR_STA_AID:nlh.NLA_U16,
    nl80211h.NL80211_ATTR_STA_FLAGS:nlh.NLA_NESTED,
    nl80211h.NL80211_ATTR_STA_LISTEN_INTERVAL:nlh.NLA_U16,
    nl80211h.NL80211_ATTR_STA_SUPPORTED_RATES:nlh.NLA_UNSPEC,
    nl80211h.NL80211_ATTR_STA_PLINK_ACTION:nlh.NLA_U8,
    nl80211h.NL80211_ATTR_STA_VLAN:nlh.NLA_U32,
    #nl80211h.NL80211_ATTR_MNTR_FLAGS:nlh.NLA_NESTED,
    nl80211h.NL80211_ATTR_MNTR_FLAGS:nlh.NLA_U32, # it seems to work by adding this attribute for each flag
    nl80211h.NL80211_ATTR_MESH_ID:nlh.NLA_UNSPEC,
    nl80211h.NL80211_ATTR_MPATH_NEXT_HOP:nlh.NLA_U32,
    nl80211h.NL80211_ATTR_REG_ALPHA2:nlh.NLA_STRING,
    nl80211h.NL80211_ATTR_REG_RULES:nlh.NLA_NESTED,
    nl80211h.NL80211_ATTR_BSS_CTS_PROT:nlh.NLA_U8,
    nl80211h.NL80211_ATTR_BSS_SHORT_PREAMBLE:nlh.NLA_U8,
    nl80211h.NL80211_ATTR_BSS_SHORT_SLOT_TIME:nlh.NLA_U8,
    nl80211h.NL80211_ATTR_BSS_BASIC_RATES:nlh.NLA_UNSPEC,
    nl80211h.NL80211_ATTR_BSS_HT_OPMODE:nlh.NLA_U16,
    nl80211h.NL80211_ATTR_MESH_CONFIG:nlh.NLA_NESTED,
    nl80211h.NL80211_ATTR_SUPPORT_MESH_AUTH:nlh.NLA_FLAG,
    nl80211h.NL80211_ATTR_HT_CAPABILITY:nlh.NLA_UNSPEC,
    nl80211h.NL80211_ATTR_MGMT_SUBTYPE:nlh.NLA_U8,
    nl80211h.NL80211_ATTR_IE:nlh.NLA_UNSPEC,
    nl80211h.NL80211_ATTR_SCAN_FREQUENCIES:nlh.NLA_NESTED,
    nl80211h.NL80211_ATTR_SCAN_SSIDS:nlh.NLA_NESTED,
    nl80211h.NL80211_ATTR_SSID:nlh.NLA_UNSPEC,
    nl80211h.NL80211_ATTR_AUTH_TYPE:nlh.NLA_U32,
    nl80211h.NL80211_ATTR_REASON_CODE:nlh.NLA_U16,
    nl80211h.NL80211_ATTR_FREQ_FIXED:nlh.NLA_FLAG,
    nl80211h.NL80211_ATTR_TIMED_OUT:nlh.NLA_FLAG,
    nl80211h.NL80211_ATTR_USE_MFP:nlh.NLA_U32,
    nl80211h.NL80211_ATTR_STA_FLAGS2:nlh.NLA_UNSPEC,
    nl80211h.NL80211_ATTR_CONTROL_PORT:nlh.NLA_FLAG,
    nl80211h.NL80211_ATTR_CONTROL_PORT_ETHERTYPE:nlh.NLA_U16,
    nl80211h.NL80211_ATTR_CONTROL_PORT_NO_ENCRYPT:nlh.NLA_FLAG,
    nl80211h.NL80211_ATTR_PRIVACY:nlh.NLA_FLAG,
    nl80211h.NL80211_ATTR_CIPHER_SUITE_GROUP:nlh.NLA_U32,
    nl80211h.NL80211_ATTR_WPA_VERSIONS:nlh.NLA_U32,
    nl80211h.NL80211_ATTR_PID:nlh.NLA_U32,
    nl80211h.NL80211_ATTR_4ADDR:nlh.NLA_U8,
    nl80211h.NL80211_ATTR_PMKID:nlh.NLA_UNSPEC,
    nl80211h.NL80211_ATTR_DURATION:nlh.NLA_U32,
    nl80211h.NL80211_ATTR_COOKIE:nlh.NLA_U64,
    nl80211h.NL80211_ATTR_TX_RATES:nlh.NLA_NESTED,
    nl80211h.NL80211_ATTR_FRAME:nlh.NLA_UNSPEC,
    nl80211h.NL80211_ATTR_FRAME_MATCH:nlh.NLA_UNSPEC,
    nl80211h.NL80211_ATTR_PS_STATE:nlh.NLA_U32,
    nl80211h.NL80211_ATTR_CQM:nlh.NLA_NESTED,
    nl80211h.NL80211_ATTR_LOCAL_STATE_CHANGE:nlh.NLA_FLAG,
    nl80211h.NL80211_ATTR_AP_ISOLATE:nlh.NLA_U8,
    nl80211h.NL80211_ATTR_WIPHY_TX_POWER_SETTING:nlh.NLA_U32,
    nl80211h.NL80211_ATTR_WIPHY_TX_POWER_LEVEL:nlh.NLA_U32,
    nl80211h.NL80211_ATTR_FRAME_TYPE:nlh.NLA_U16,
    nl80211h.NL80211_ATTR_WIPHY_ANTENNA_TX:nlh.NLA_U32,
    nl80211h.NL80211_ATTR_WIPHY_ANTENNA_RX:nlh.NLA_U32,
    nl80211h.NL80211_ATTR_MCAST_RATE:nlh.NLA_U32,
    nl80211h.NL80211_ATTR_OFFCHANNEL_TX_OK:nlh.NLA_FLAG,
    nl80211h.NL80211_ATTR_KEY_DEFAULT_TYPES:nlh.NLA_NESTED,
    nl80211h.NL80211_ATTR_WOWLAN_TRIGGERS:nlh.NLA_NESTED,
    nl80211h.NL80211_ATTR_STA_PLINK_STATE:nlh.NLA_U8,
    nl80211h.NL80211_ATTR_SCHED_SCAN_INTERVAL:nlh.NLA_U32,
    nl80211h.NL80211_ATTR_REKEY_DATA:nlh.NLA_NESTED,
    nl80211h.NL80211_ATTR_SCAN_SUPP_RATES:nlh.NLA_NESTED,
    nl80211h.NL80211_ATTR_HIDDEN_SSID:nlh.NLA_U32,
    nl80211h.NL80211_ATTR_IE_PROBE_RESP:nlh.NLA_UNSPEC,
    nl80211h.NL80211_ATTR_IE_ASSOC_RESP:nlh.NLA_UNSPEC,
    nl80211h.NL80211_ATTR_ROAM_SUPPORT:nlh.NLA_FLAG,
    nl80211h.NL80211_ATTR_SCHED_SCAN_MATCH:nlh.NLA_NESTED,
    nl80211h.NL80211_ATTR_TX_NO_CCK_RATE:nlh.NLA_FLAG,
    nl80211h.NL80211_ATTR_TDLS_ACTION:nlh.NLA_U8,
    nl80211h.NL80211_ATTR_TDLS_DIALOG_TOKEN:nlh.NLA_U8,
    nl80211h.NL80211_ATTR_TDLS_OPERATION:nlh.NLA_U8,
    nl80211h.NL80211_ATTR_TDLS_SUPPORT:nlh.NLA_FLAG,
    nl80211h.NL80211_ATTR_TDLS_EXTERNAL_SETUP:nlh.NLA_FLAG,
    #nl80211h.NL80211_ATTR_TDLS_INITIATOR:nlh.NLA_FLAG,
    nl80211h.NL80211_ATTR_DONT_WAIT_FOR_ACK:nlh.NLA_FLAG,
    nl80211h.NL80211_ATTR_PROBE_RESP:nlh.NLA_UNSPEC,
    nl80211h.NL80211_ATTR_DFS_REGION:nlh.NLA_U8,
    nl80211h.NL80211_ATTR_DISABLE_HT:nlh.NLA_FLAG,
    nl80211h.NL80211_ATTR_HT_CAPABILITY_MASK:nlh.NLA_UNSPEC,
    nl80211h.NL80211_ATTR_NOACK_MAP:nlh.NLA_U16,
    nl80211h.NL80211_ATTR_INACTIVITY_TIMEOUT:nlh.NLA_U16,
    nl80211h.NL80211_ATTR_BG_SCAN_PERIOD:nlh.NLA_U16,
    nl80211h.NL80211_ATTR_WDEV:nlh.NLA_U64,
    nl80211h.NL80211_ATTR_USER_REG_HINT_TYPE:nlh.NLA_U32,
    nl80211h.NL80211_ATTR_SAE_DATA:nlh.NLA_UNSPEC,
    nl80211h.NL80211_ATTR_VHT_CAPABILITY:nlh.NLA_UNSPEC,
    nl80211h.NL80211_ATTR_SCAN_FLAGS:nlh.NLA_U32,
    nl80211h.NL80211_ATTR_P2P_CTWINDOW:nlh.NLA_U8,
    nl80211h.NL80211_ATTR_P2P_OPPPS:nlh.NLA_U8,
    nl80211h.NL80211_ATTR_ACL_POLICY:nlh.NLA_U32,
    nl80211h.NL80211_ATTR_MAC_ADDRS:nlh.NLA_NESTED,
    nl80211h.NL80211_ATTR_STA_CAPABILITY:nlh.NLA_U16,
    nl80211h.NL80211_ATTR_STA_EXT_CAPABILITY:nlh.NLA_UNSPEC,
    nl80211h.NL80211_ATTR_SPLIT_WIPHY_DUMP:nlh.NLA_FLAG,
    nl80211h.NL80211_ATTR_DISABLE_VHT:nlh.NLA_FLAG,
    nl80211h.NL80211_ATTR_VHT_CAPABILITY_MASK:nlh.NLA_UNSPEC,
    nl80211h.NL80211_ATTR_MDID:nlh.NLA_U16,
    nl80211h.NL80211_ATTR_IE_RIC:nlh.NLA_UNSPEC,
    nl80211h.NL80211_ATTR_PEER_AID:nlh.NLA_U16,
    nl80211h.NL80211_ATTR_CH_SWITCH_COUNT:nlh.NLA_U32,
    nl80211h.NL80211_ATTR_CH_SWITCH_BLOCK_TX:nlh.NLA_FLAG,
    nl80211h.NL80211_ATTR_CSA_IES:nlh.NLA_NESTED,
    nl80211h.NL80211_ATTR_CSA_C_OFF_BEACON:nlh.NLA_UNSPEC,
    nl80211h.NL80211_ATTR_CSA_C_OFF_PRESP:nlh.NLA_UNSPEC,
    nl80211h.NL80211_ATTR_STA_SUPPORTED_CHANNELS:nlh.NLA_UNSPEC,
    nl80211h.NL80211_ATTR_STA_SUPPORTED_OPER_CLASSES:nlh.NLA_UNSPEC,
    nl80211h.NL80211_ATTR_HANDLE_DFS:nlh.NLA_FLAG,
    # not present in nl80211.c
    nl80211h.NL80211_ATTR_SUPPORTED_IFTYPES:nlh.NLA_NESTED,
    nl80211h.NL80211_ATTR_SOFTWARE_IFTYPES:nlh.NLA_NESTED,
    #nl80211h.NL80211_ATTR_WIPHY_BANDS:nlh.NLA_NESTED,
    nl80211h.NL80211_ATTR_SUPPORTED_COMMANDS:nlh.NLA_NESTED,
    nl80211h.NL80211_ATTR_MAX_NUM_SCAN_SSIDS:nlh.NLA_U8,
    nl80211h.NL80211_ATTR_GENERATION: nlh.NLA_U8,
    #nl80211h.NL80211_ATTR_MAC:nlh.NLA_STRING,
    #Not defined in nl80211_h
    #nl80211h.NL80211_ATTR_OPMODE_NOTIF:nlh.NLA_U8,
    #nl80211h.NL80211_ATTR_VENDOR_ID:nlh.NLA_U32,
    #nl80211h.NL80211_ATTR_VENDOR_SUBCMD:nlh.NLA_U32,
    #nl80211h.NL80211_ATTR_VENDOR_DATA:nlh.NLA_UNSPEC,
    #nl80211h.NL80211_ATTR_QOS_MAP:nlh.NLA_UNSPEC,
    #nl80211h.NL80211_ATTR_MAC_HINT:nlh.NLA_UNSPEC,
    #nl80211h.NL80211_ATTR_WIPHY_FREQ_HINT:nlh.NLA_U32,
    #nl80211h.NL80211_ATTR_TDLS_PEER_CAPABILITY:nlh.NLA_U32,
    #nl80211h.NL80211_ATTR_SOCKET_OWNER:nlh.NLA_FLAG,
    #nl80211h.NL80211_ATTR_CSA_C_OFFSETS_TX:nlh.NLA_UNSPEC,
    #nl80211h.NL80211_ATTR_USE_RRM:nlh.NLA_FLAG,
    #nl80211h.NL80211_ATTR_TSID:nlh.NLA_U8,
    #nl80211h.NL80211_ATTR_USER_PRIO:nlh.NLA_U8,
    #nl80211h.NL80211_ATTR_ADMITTED_TIME:nlh.NLA_U16,
    #nl80211h.NL80211_ATTR_SMPS_MODE:nlh.NLA_U8,
    #nl80211h.NL80211_ATTR_MAC_MASK:nlh.NLA_UNSPEC,
    #nl80211h.NL80211_ATTR_WIPHY_SELF_MANAGED_REG:nlh.NLA_FLAG,
    #nl80211h.NL80211_ATTR_NETNS_FD:nlh.NLA_U32,
    #nl80211h.NL80211_ATTR_SCHED_SCAN_DELAY:nlh.NLA_U32,
    #nl80211h.NL80211_ATTR_REG_INDOOR:nlh.NLA_FLAG,
    #nl80211h.NL80211_ATTR_PBSS:nlh.NLA_FLAG
}


# policy for the key attributes
#static const struct nla_policy nl80211_key_policy[NL80211_KEY_MAX + 1] = {
nl80211_key_policy = {
    nl80211h.NL80211_KEY_DATA:nlh.NLA_UNSPEC,
    nl80211h.NL80211_KEY_IDX:nlh.NLA_U8,
    nl80211h.NL80211_KEY_CIPHER:nlh.NLA_U32,
    nl80211h.NL80211_KEY_SEQ:nlh.NLA_UNSPEC,
    nl80211h.NL80211_KEY_DEFAULT:nlh.NLA_FLAG,
    nl80211h.NL80211_KEY_DEFAULT_MGMT:nlh.NLA_FLAG,
    nl80211h.NL80211_KEY_TYPE:nlh.NLA_U32,
    nl80211h.NL80211_KEY_DEFAULT_TYPES:nlh.NLA_NESTED
}

# policy for the key default flags
#static const struct nla_policy
nl80211_key_default_policy = {
    nl80211h.NL80211_KEY_DEFAULT_TYPE_UNICAST:nlh.NLA_FLAG,
    nl80211h.NL80211_KEY_DEFAULT_TYPE_MULTICAST:nlh.NLA_FLAG
}

#/* policy for WoWLAN attributes */
#static const struct nla_policy nl80211_wowlan_policy[NUM_NL80211_WOWLAN_TRIG] = {
nl80211_wowlan_trig_policy = {
    nl80211h.NL80211_WOWLAN_TRIG_ANY:nlh.NLA_FLAG,
    nl80211h.NL80211_WOWLAN_TRIG_DISCONNECT:nlh.NLA_FLAG,
    nl80211h.NL80211_WOWLAN_TRIG_MAGIC_PKT:nlh.NLA_FLAG,
    nl80211h.NL80211_WOWLAN_TRIG_PKT_PATTERN:nlh.NLA_NESTED,
    nl80211h.NL80211_WOWLAN_TRIG_GTK_REKEY_FAILURE:nlh.NLA_FLAG,
    nl80211h.NL80211_WOWLAN_TRIG_EAP_IDENT_REQUEST:nlh.NLA_FLAG,
    nl80211h.NL80211_WOWLAN_TRIG_4WAY_HANDSHAKE:nlh.NLA_FLAG,
    nl80211h.NL80211_WOWLAN_TRIG_RFKILL_RELEASE:nlh.NLA_FLAG,
    nl80211h.NL80211_WOWLAN_TRIG_TCP_CONNECTION:nlh.NLA_NESTED
    #nl80211h.NL80211_WOWLAN_TRIG_NET_DETECT:nlh.NLA_NESTED
}

#static const struct nla_policy nl80211_wowlan_tcp_policy[NUM_NL80211_WOWLAN_TCP] = {
nl80211_wowlan_tcp_policy = {
    nl80211h.NL80211_WOWLAN_TCP_SRC_IPV4:nlh.NLA_U32,
    nl80211h.NL80211_WOWLAN_TCP_DST_IPV4:nlh.NLA_U32,
    nl80211h.NL80211_WOWLAN_TCP_DST_MAC:nlh.NLA_UNSPEC,
    nl80211h.NL80211_WOWLAN_TCP_SRC_PORT:nlh.NLA_U16,
    nl80211h.NL80211_WOWLAN_TCP_DST_PORT:nlh.NLA_U16,
    nl80211h.NL80211_WOWLAN_TCP_DATA_PAYLOAD:nlh.NLA_UNSPEC,
    nl80211h.NL80211_WOWLAN_TCP_DATA_PAYLOAD_SEQ:nlh.NLA_UNSPEC,
    nl80211h.NL80211_WOWLAN_TCP_DATA_PAYLOAD_TOKEN:nlh.NLA_UNSPEC,
    nl80211h.NL80211_WOWLAN_TCP_DATA_INTERVAL:nlh.NLA_U32,
    nl80211h.NL80211_WOWLAN_TCP_WAKE_PAYLOAD:nlh.NLA_UNSPEC,
    nl80211h.NL80211_WOWLAN_TCP_WAKE_MASK:nlh.NLA_UNSPEC
}

#/* policy for coalesce rule attributes */
#static const struct nla_policy nl80211_coalesce_policy[NUM_NL80211_ATTR_COALESCE_RULE] = {
nl80211_coalesce_policy={
    nl80211h.NL80211_ATTR_COALESCE_RULE_DELAY:nlh.NLA_U32,
    nl80211h.NL80211_ATTR_COALESCE_RULE_CONDITION:nlh.NLA_U32,
    nl80211h.NL80211_ATTR_COALESCE_RULE_PKT_PATTERN:nlh.NLA_NESTED
}

#/* policy for GTK rekey offload attributes */
#static const struct nla_policy nl80211_rekey_policy[NUM_NL80211_REKEY_DATA] = {
nl80211_rekey_policy = {
    nl80211h.NL80211_REKEY_DATA_KEK:nlh.NLA_UNSPEC,
    nl80211h.NL80211_REKEY_DATA_KCK:nlh.NLA_UNSPEC,
    nl80211h.NL80211_REKEY_DATA_REPLAY_CTR:nlh.NLA_UNSPEC
}

#static const struct nla_policy nl80211_match_policy[NL80211_SCHED_SCAN_MATCH_ATTR_MAX + 1] = {
nl80211_sched_scan_match_policy = {
    nl80211h.NL80211_SCHED_SCAN_MATCH_ATTR_SSID:nlh.NLA_UNSPEC,
    nl80211h.NL80211_SCHED_SCAN_MATCH_ATTR_RSSI:nlh.NLA_U32
}

#static const struct nla_policy nl80211_plan_policy[NL80211_SCHED_SCAN_PLAN_MAX + 1] = {
#nl80211_sched_scan_plan_policy = {
#    nl80211h.NL80211_SCHED_SCAN_PLAN_INTERVAL:nlh.NLA_U32,
#    nl80211h.NL80211_SCHED_SCAN_PLAN_ITERATIONS:nlh.NLA_U32
#}


"""
Parsing NL80211_ATTR_WIPHY_BANDS

A hack for extracting supported frequencies from the NL80211_ATTR_WIPHY_BANDS
libnl.nla_parse_nested does not parse the bands structure correctly

 1) Each band( or frequency list) begins with < n > \x01 (\x01 = NL80211_BAND_ATTR_FREQS)
    where n (starting at 1) appears to be the band number
  - the first one seems to happen at 209 (on alfa, intel and rosewill cards at
    least)
  - there may be erroneous band delimiters
   o if valid, the first freq is directly following the band delimiter
  - rosewill card skips \x02\x01, \x03\x01 and uses \x04\x01 for UNII 5 and 4 GHz

 2) Each freq structure appears to be listed as

  +-------+-----+-------+-------+-----------+-----+
  | buff1 | RF  | [unk] | buff2 | freq data | pad |
  +-------+-----+-------+-------+-----------+-----+
      9      4      7      4      <var>       2

  where

   - buff1 =

   +------+-----+------+-----+----------------------+
   | \x00 | <l> | \x00 | cnt | \x00\x08\x00\x01\x00 |
   +------+-----+------+-----+----------------------+

   such that l is the length in bytes of the complete freq.structure to include
   the first and last null byte.and cnt is the number (starting at 0) of the
   current freq in this band.

   - RF is a 4-octet frequency

   - unk = \x04\x00\x03\x00\x04\x00\x04 if present

   - buff2 = \x08\x00\x06\x00

   - pad = < n > \x00 where < n > has been seen as \x05 and  \x07

  3) we can determine where to start identifying frequencies
   - find the band marker
   - if there is buff1 with cnt = 0 4 bytes after the start of the marker
    o 2 bytes for the band marker and 2 bytes for the null byte and flag

  4) we need to identify something other than band markers to determine where
    to pull frequencies from

"""
fSz = 'B'
iSz = 1
fCnt = 'B'
iCnt = 3
fFreq = 'I'
iFreq = 9
first = '\x00{0}\x00\x08\x00\x01\x00'.format(struct.pack(fCnt,0))
lFirst = len(first)
def nl80211_parse_freqs(bands):
    """
     extracts frequencies from bands
     :param bands: packed bytes containing band data
     :returns: list of frequencies found in bands
    """
    # get the band markers
    # for each possible bandmarker determine validity by identifying if there is
    # a freq structure w/ count = 9 following immediately after the bandmarker
    # we have to skip the length portion as well of the freq structure. If so
    # append the index (the end) of the bandmarker
    bandmarkers = []
    #for i in _bandmarkers_('\x01\x01',bands) + _bandmarkers_('\x02\x01',bands):
    #    if bands[i+4:i+4+len(first)] == first: bandmarkers.append(i+2)

    # this works but, how do we know which band number to stop trying?
    for i in xrange(10):
        for j in _bandmarkers_(struct.pack('B',i) + '\x01',bands):
            if bands[j+4:j+4+lFirst] == first:
                bandmarkers.append(j+2)
                break

    l = len(bands)
    rfs = []
    for bm in bandmarkers:
        # get freq structure length and parse out freq
        idx = bm
        cnt = 0
        while idx < l:
            try:
                sz = struct.unpack_from(fSz,bands,idx+iSz)[0]
                if cnt != struct.unpack_from(fCnt,bands,idx+iCnt)[0]: break
                rfs.append(struct.unpack_from(fFreq,bands,idx+iFreq)[0])
            except (struct.error,IndexError):
                break
            cnt += 1
            idx += sz
    return rfs

def _bandmarkers_(marker,bands):
    ms = []
    idx = 0
    while idx < len(bands):
        idx = bands.find(marker,idx)
        if idx == -1: break
        ms.append(idx)
        idx += 2
    return ms