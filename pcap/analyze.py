#!/usr/bin/env python3
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "scapy",
#     "httpx",
# ]
# ///
#!/usr/bin/env python3
#!/usr/bin/env python3
"""
Simple PCAP Conversation Filter - JSON Output
"""

import os
import sys
import json
import argparse
import re
from collections import defaultdict
import httpx
from pathlib import Path

try:
    from scapy.all import rdpcap, IP, TCP, Raw
except ImportError:
    print("Error: scapy is required. Install it with: pip install scapy --break-system-packages")
    sys.exit(1)

def download_pcap(round_id):
    headers = {
      'Authorization': os.getenv('AUTH_TOKEN')
    }
    data = {'round_id': f'{round_id:03}'}
    resp = httpx.post(
        'https://192.168.0.1:8001/blue/pcap',
        headers=headers,
        verify=False,
        json=data
    )
    resp.raise_for_status()
    print(len(resp.content))

    filename = Path(f'~/Downloads/{round_id:03}.pcap').expanduser().resolve()
    with open(filename, 'wb') as f:
        f.write(resp.content)
    print(f'Downloaded: {filename} ({len(resp.content)} bytes)')

    return filename

def get_conversation_key(packet):
    """Generate a unique key for a TCP conversation."""
    if IP not in packet or TCP not in packet:
        return None

    src_ip = packet[IP].src
    dst_ip = packet[IP].dst
    src_port = packet[TCP].sport
    dst_port = packet[TCP].dport

    # Normalize (bidirectional)
    if (src_ip, src_port) < (dst_ip, dst_port):
        return (src_ip, src_port, dst_ip, dst_port)
    else:
        return (dst_ip, dst_port, src_ip, src_port)


def extract_metadata(packets, src_ip, src_port):
    """Extract team hash and challenge from conversation start."""
    team_hash = None
    challenge = None
    skip_until_idx = 0

    for idx, packet in enumerate(packets):
        if Raw not in packet:
            continue

        try:
            payload = packet[Raw].load.decode('utf-8', errors='replace')
        except:
            continue

        # Look for hash value from client
        if packet[IP].src != src_ip and not team_hash:
            # Check if this looks like a hash (32 hex chars)
            stripped = payload.strip()
            if re.match(r'^[a-fA-F0-9]{32}$', stripped):
                team_hash = stripped
                continue

        # Look for challenge selection (number after "option :")
        if packet[IP].src != src_ip and team_hash and not challenge:
            stripped = payload.strip()
            if stripped.isdigit():
                challenge_num = int(stripped)
                # Map to challenge name
                challenges = {
                    1: "msgBoard",
                    2: "cmdF",
                    3: "TryIt",
                    4: "tc0",
                    5: "encode",
                    6: "netdiag",
                    7: "NB",
                    8: "exit"
                }
                if challenge_num in challenges:
                    challenge = challenges[challenge_num]
                elif src_port == 9999:
                    challenge = 'bitscript'
                else:
                    challenge = f"unknown({stripped})"
                skip_until_idx = idx + 1
                break

    return team_hash, challenge, skip_until_idx


def search_conversations(pcap_file, search_string, case_sensitive=True, metadata_only=False):
    """Search for TCP conversations containing the specified string."""

    try:
        packets = rdpcap(str(pcap_file))
    except Exception as e:
        print(f"Error reading PCAP: {e}", file=sys.stderr)
        sys.exit(1)

    conversations = defaultdict(list)
    matching_conversations = set()

    search_bytes = search_string.encode('utf-8', errors='ignore')
    if not case_sensitive:
        search_bytes = search_bytes.lower()

    # Group packets and find matches
    for packet in packets:
        conv_key = get_conversation_key(packet)
        if not conv_key:
            continue

        conversations[conv_key].append(packet)

        if Raw in packet:
            payload = packet[Raw].load
            search_in = payload if case_sensitive else payload.lower()
            if search_bytes in search_in:
                matching_conversations.add(conv_key)

    # Build JSON output
    results = []

    for conv_key in sorted(matching_conversations):
        src_ip, src_port, dst_ip, dst_port = conv_key
        conv_packets = conversations[conv_key]

        # Extract metadata
        team_hash, challenge, skip_idx = extract_metadata(conv_packets, src_ip, src_port)

        # Build conversation object
        conversation = {
            "conversation": f"{src_ip}:{src_port} <-> {dst_ip}:{dst_port}",
            "team_hash": team_hash,
            "challenge": challenge
        }

        # Add content if not metadata-only
        if not metadata_only:
            content = []

            for idx, packet in enumerate(conv_packets):
                if idx < skip_idx:
                    continue

                if Raw not in packet:
                    continue

                payload = packet[Raw].load
                direction = ">>>" if packet[IP].src == src_ip else "<<<"
                endpoint = f"{packet[IP].src}:{packet[TCP].sport}"

                # Try to decode as text
                try:
                    text = payload.decode('utf-8', errors='replace')
                    content.append({
                        "direction": direction,
                        "endpoint": endpoint,
                        "data": text,
                        "type": "text"
                    })
                except:
                    content.append({
                        "direction": direction,
                        "endpoint": endpoint,
                        "data": payload.hex(),
                        "type": "binary",
                        "size": len(payload)
                    })

            conversation["content"] = content

        results.append(conversation)

    return results


def main():
    parser = argparse.ArgumentParser(description='Search TCP conversations in PCAP')
    parser.add_argument('round_id', type=int, help='Round for PCAP file')
    parser.add_argument('-s', '--search_string', default='AEGIS{', help='String to search for')
    parser.add_argument('-i', '--case-insensitive', action='store_true',
                        help='Case-insensitive search (default is case-sensitive)')
    parser.add_argument('-m', '--metadata-only', action='store_true',
                        help='Show only metadata (conversation, team_hash, challenge)')
    parser.add_argument('-o', '--output-dir', default='./round_json', help='Output dir')
    parser.add_argument('--pretty', action='store_true',
                        help='Pretty-print JSON output')

    args = parser.parse_args()

    pcap_file = download_pcap(args.round_id)

    case_sensitive = not args.case_insensitive
    results = search_conversations(
        pcap_file,
        args.search_string,
        case_sensitive,
        args.metadata_only
    )

    # Output JSON
    if args.pretty:
        json_output = json.dumps(results, indent=2, ensure_ascii=False)
    else:
        json_output = json.dumps(results, ensure_ascii=False)

    if args.output_dir:
        output_file = Path(f'{args.output_dir}/{args.round_id:02}.json').expanduser().resolve()
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(json_output)
        print(f"Output written to {output_file}", file=sys.stderr)
    else:
        print(json_output)


if __name__ == '__main__':
    main()
