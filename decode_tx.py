#!/usr/bin/env python3
import sys
import json
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class TxInput:
    prev_txid: str
    prev_index: int
    script_sig: str
    sequence: int
    witness: List[str] = None

@dataclass
class TxOutput:
    value_sats: int
    value_btc: float
    script_pubkey: str

@dataclass
class Transaction:
    version: int
    flag: int
    is_segwit: bool
    vin: List[TxInput]
    vout: List[TxOutput]
    locktime: int

# helpers
def read_uint_le(b: bytes, offset: int, length: int) -> Tuple[int, int]:
    return int.from_bytes(b[offset:offset+length], 'little'), offset+length

def read_varint(b: bytes, offset: int) -> Tuple[int, int]:
    i = b[offset]; offset += 1
    if i < 0xfd: return i, offset
    if i == 0xfd: val, offset = read_uint_le(b, offset, 2); return val, offset
    if i == 0xfe: val, offset = read_uint_le(b, offset, 4); return val, offset
    val, offset = read_uint_le(b, offset, 8); return val, offset

def parse_tx(tx_hex: str) -> Transaction:
    b = bytes.fromhex(tx_hex)
    offset = 0
    version, offset = read_uint_le(b, offset, 4)
    is_segwit = False
    flag = None
    if offset+2 <= len(b) and b[offset] == 0x00 and b[offset+1] == 0x01:
        is_segwit = True; flag = 0x0001; offset += 2
    vin_count, offset = read_varint(b, offset)
    vin = []
    for _ in range(vin_count):
        prev_txid = b[offset:offset+32][::-1].hex(); offset += 32
        prev_index, offset = read_uint_le(b, offset, 4)
        script_len, offset = read_varint(b, offset)
        script_sig = b[offset:offset+script_len].hex(); offset += script_len
        sequence, offset = read_uint_le(b, offset, 4)
        vin.append(TxInput(prev_txid, prev_index, script_sig, sequence))
    vout_count, offset = read_varint(b, offset)
    vout = []
    for _ in range(vout_count):
        value_sats, offset = read_uint_le(b, offset, 8)
        value_btc = value_sats / 100_000_000
        script_len, offset = read_varint(b, offset)
        script_pubkey = b[offset:offset+script_len].hex(); offset += script_len
        vout.append(TxOutput(value_sats, value_btc, script_pubkey))
    if is_segwit:
        for i in range(len(vin)):
            n_items, offset = read_varint(b, offset)
            items = []
            for _ in range(n_items):
                item_len, offset = read_varint(b, offset)
                item = b[offset:offset+item_len].hex(); offset += item_len
                items.append(item)
            vin[i].witness = items
    locktime, offset = read_uint_le(b, offset, 4)
    return Transaction(version, flag, is_segwit, vin, vout, locktime)

def main():
    if len(sys.argv) < 2:
        print("Usage: python decode_tx.py <tx_hex>")
        sys.exit(1)
    tx_hex = sys.argv[1]
    tx = parse_tx(tx_hex)
    out = {
        "version": tx.version,
        "is_segwit": tx.is_segwit,
        "vin_count": len(tx.vin),
        "vout_count": len(tx.vout),
        "inputs": [],
        "outputs": [],
        "locktime": tx.locktime
    }
    for i, inp in enumerate(tx.vin):
        out["inputs"].append({
            "index": i,
            "prev_txid": inp.prev_txid,
            "prev_index": inp.prev_index,
            "script_sig_hex": inp.script_sig,
            "sequence": hex(inp.sequence),
            "witness": inp.witness
        })
    for i, outp in enumerate(tx.vout):
        out["outputs"].append({
            "index": i,
            "value_satoshis": outp.value_sats,
            "value_btc": outp.value_btc,
            "script_pubkey_hex": outp.script_pubkey
        })
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
import sys
import json
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class TxInput:
    prev_txid: str
    prev_index: int
    script_sig: str
    sequence: int
    witness: List[str] = None

@dataclass
class TxOutput:
    value_sats: int
    value_btc: float
    script_pubkey: str

@dataclass
class Transaction:
    version: int
    flag: int
    is_segwit: bool
    vin: List[TxInput]
    vout: List[TxOutput]
    locktime: int

# helpers
def read_uint_le(b: bytes, offset: int, length: int) -> Tuple[int, int]:
    return int.from_bytes(b[offset:offset+length], 'little'), offset+length

def read_varint(b: bytes, offset: int) -> Tuple[int, int]:
    i = b[offset]; offset += 1
    if i < 0xfd: return i, offset
    if i == 0xfd: val, offset = read_uint_le(b, offset, 2); return val, offset
    if i == 0xfe: val, offset = read_uint_le(b, offset, 4); return val, offset
    val, offset = read_uint_le(b, offset, 8); return val, offset

def parse_tx(tx_hex: str) -> Transaction:
    b = bytes.fromhex(tx_hex)
    offset = 0
    version, offset = read_uint_le(b, offset, 4)
    is_segwit = False
    flag = None
    if offset+2 <= len(b) and b[offset] == 0x00 and b[offset+1] == 0x01:
        is_segwit = True; flag = 0x0001; offset += 2
    vin_count, offset = read_varint(b, offset)
    vin = []
    for _ in range(vin_count):
        prev_txid = b[offset:offset+32][::-1].hex(); offset += 32
        prev_index, offset = read_uint_le(b, offset, 4)
        script_len, offset = read_varint(b, offset)
        script_sig = b[offset:offset+script_len].hex(); offset += script_len
        sequence, offset = read_uint_le(b, offset, 4)
        vin.append(TxInput(prev_txid, prev_index, script_sig, sequence))
    vout_count, offset = read_varint(b, offset)
    vout = []
    for _ in range(vout_count):
        value_sats, offset = read_uint_le(b, offset, 8)
        value_btc = value_sats / 100_000_000
        script_len, offset = read_varint(b, offset)
        script_pubkey = b[offset:offset+script_len].hex(); offset += script_len
        vout.append(TxOutput(value_sats, value_btc, script_pubkey))
    if is_segwit:
        for i in range(len(vin)):
            n_items, offset = read_varint(b, offset)
            items = []
            for _ in range(n_items):
                item_len, offset = read_varint(b, offset)
                item = b[offset:offset+item_len].hex(); offset += item_len
                items.append(item)
            vin[i].witness = items
    locktime, offset = read_uint_le(b, offset, 4)
    return Transaction(version, flag, is_segwit, vin, vout, locktime)

def main():
    if len(sys.argv) < 2:
        print("Usage: python decode_tx.py <tx_hex>")
        sys.exit(1)
    tx_hex = sys.argv[1]
    tx = parse_tx(tx_hex)
    out = {
        "version": tx.version,
        "is_segwit": tx.is_segwit,
        "vin_count": len(tx.vin),
        "vout_count": len(tx.vout),
        "inputs": [],
        "outputs": [],
        "locktime": tx.locktime
    }
    for i, inp in enumerate(tx.vin):
        out["inputs"].append({
            "index": i,
            "prev_txid": inp.prev_txid,
            "prev_index": inp.prev_index,
            "script_sig_hex": inp.script_sig,
            "sequence": hex(inp.sequence),
            "witness": inp.witness
        })
    for i, outp in enumerate(tx.vout):
        out["outputs"].append({
            "index": i,
            "value_satoshis": outp.value_sats,
            "value_btc": outp.value_btc,
            "script_pubkey_hex": outp.script_pubkey
        })
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()

