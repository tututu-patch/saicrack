# -*- coding: utf-8 -*-
"""SAI cracker 2.0.0 - Python 3"""
import os, shutil, time, re, struct
from pathlib import Path

OLD_N = bytes.fromhex(
    "83b0bc5cd161ae1e3a64687c416db3224887bb18d72bcab089cfc2c65c2ebbcf"
    "45223a869c86a7cba905840dc0fa0d5c03e7ba00963296ec50a5bdadefffa294"
    "ec1ff90e39a23d2116d76185dd9665cb77b4fe1c28632f75742c1ddbc083bd05"
    "d89a15d1af1baaaeb0be4c17c1fd28408cd6b6b78a86a766576affeaa7df2ebf"
)
NEW_N = bytes.fromhex(
    "090ae84e68968802862f9e2945e5f50d8b14205ca1d7c8114ee171bcda926115"
    "e190812f12b2dfbe786092ac7f9a050fa976982f9147e9fceed444f1608de213"
    "4c60f4e63768f4c7a0d602ea9d92ee39646fa629859d646c66baa4dc5925bd35"
    "af384f9882add2ad2d9aa4eee85d8849447c1accdc9fb3ddc369343cec828f9b"
)
N_OLD = int.from_bytes(OLD_N, "little")
N_NEW = int.from_bytes(NEW_N, "little")
E = 65537
D = 0x30C1B95A4BC06DC9FB29FA981CCCCC5826E7FBEF2F251E41E4F25C79CB3D415A0130E88D12CFFAB07196D39C52229D553FA71C032CBE7900E9CB1C03317B34D70667F886E488A2E4C2DFC3BBC225E4709C2A5CDAF4611CF6399AB07F2B86C854940966B607B16BA1F68A18B5FD94141760AA4AFEDD3965E57475FCE84F5F1D35


def reencrypt_blob(blob):
    C = int.from_bytes(blob, "little")
    if not (0 < C < N_OLD):
        return None
    m = pow(C, E, N_OLD)
    be = m.to_bytes(128, "big")
    if be[:2] != b"\x00\x01" or be.count(0xFF) < 30:
        return None
    out = pow(m, D, N_NEW).to_bytes(128, "little")
    if pow(int.from_bytes(out, "little"), E, N_NEW) != m:
        raise ValueError("reencrypt verify failed")
    return out


def find_and_reencrypt_blobs(data):
    """Re-encrypt known/likely RSA-wrapped blobs under OLD_N.

    Full-file scanning is expensive; use targeted candidates:
      1) fixed marker used by new SAI2 AES-key wrap
      2) 128-byte block immediately before public modulus N (SAI1 SEV0)
      3) nearby aligned blocks around N (defensive)
    """
    ba = bytearray(data)
    patched = []
    candidates = set()

    # 1) new SAI2 wrapped AES material marker (first 32 bytes of ciphertext)
    mark = bytes.fromhex(
        "1c6281ebd5b83e4e9c3a5a69b9d445417e7795c4c2e5f6cd7c1569de00888b9a"
    )
    pos = 0
    while True:
        j = data.find(mark, pos)
        if j < 0:
            break
        candidates.add(j)
        pos = j + 1

    # 2/3) around public modulus
    npos = data.find(OLD_N)
    if npos >= 0:
        for delta in (128, 256, 384, 512, 0):
            p = npos - delta
            if p >= 0:
                candidates.add(p)

    for i in sorted(candidates):
        if i in patched:
            continue
        if i + 128 > len(ba):
            continue
        blk = bytes(ba[i:i + 128])
        out = reencrypt_blob(blk)
        if out is not None:
            ba[i:i + 128] = out
            patched.append(i)
    return bytes(ba), patched


def create_license(sysid, path="license.slc"):
    if len(sysid) != 8 or re.findall(r"[^0-9a-fA-F]", sysid):
        print("System ID must be 8 hex characters.")
        return False
    M = int("000000010000000000000001000000000000000000000000%s00000001" % sysid.upper(), 16)
    ans = pow(M, D, N_NEW)
    slc = []
    while ans:
        slc.append(ans & 0xFF)
        ans >>= 8
    if len(slc) > 128:
        print("Internal error.")
        return False
    if len(slc) < 128:
        slc.extend([0] * (128 - len(slc)))
    Path(path).write_bytes(struct.pack("<128B", *slc))
    return True


def patch_bytes(data):
    info = {"n_pos": -1, "blob_positions": [], "patched_n": False}
    if data.find(OLD_N) < 0:
        if data.find(NEW_N) >= 0:
            info["n_pos"] = data.find(NEW_N)
            info["note"] = "N already patched"
            info["ok"] = True
            return data, info
        info["error"] = "RSA modulus N not found (unsupported version)"
        return data, info

    data2, blobs = find_and_reencrypt_blobs(data)
    info["blob_positions"] = blobs
    pos = data2.find(OLD_N)
    if pos < 0:
        info["error"] = "N disappeared unexpectedly"
        return data, info
    ba = bytearray(data2)
    ba[pos:pos + 128] = NEW_N
    info["n_pos"] = pos
    info["patched_n"] = True
    info["ok"] = True
    return bytes(ba), info


def find_exe():
    for name in ("sai2.exe", "sai.exe"):
        if Path(name).is_file():
            return name
    return None


def docrack():
    exe = find_exe()
    if not exe:
        print("sai2.exe / sai.exe does not exist.")
        return False

    for saifile in os.listdir("."):
        if os.path.isfile(saifile) and re.match(r"(sai2|sai)\.exe\.\d{10}\.bak$", saifile):
            try:
                os.remove(saifile)
            except Exception:
                pass

    bakfile = "%s.%s.bak" % (exe, int(time.time()))
    try:
        shutil.copy(exe, bakfile)
    except Exception:
        print("Backup failed: maybe no write permission.")
        return False

    while True:
        sysid = input("System ID: ").strip()
        if len(sysid) == 8 and not re.findall(r"[^0-9a-fA-F]", sysid):
            break
        print("System ID must be 8 hex chars.")

    if not create_license(sysid, "license.slc"):
        try:
            os.remove(exe)
            os.rename(bakfile, exe)
            print("Restore backup success.")
        except Exception:
            print("Restore backup failed.")
        return False

    try:
        shutil.copy("license.slc", "sai-crack.slc")
    except Exception:
        pass

    while input("*Close SAI if it is opened*, then type OK to continue: ").strip() != "OK":
        pass

    data = Path(exe).read_bytes()
    new_data, info = patch_bytes(data)
    print("Patch info:", info)
    if not info.get("ok"):
        try:
            os.remove(exe)
            os.rename(bakfile, exe)
            print("Restore backup success.")
        except Exception:
            print("Restore backup failed.")
        return False

    Path(exe).write_bytes(new_data)
    print("Patched %s (N @ 0x%X, reencrypted blobs: %d)" % (
        exe, info.get("n_pos", -1), len(info.get("blob_positions", []))))
    return True


if __name__ == "__main__":
    ret = False
    try:
        print("Sai cracker ver 2.0.0\n")
        ret = docrack()
    except Exception as e:
        print(e)
        import traceback
        traceback.print_exc()
        ret = False
    finally:
        print("Crack success!" if ret else "Crack failed!")
        input("Press ENTER key to continue...")
