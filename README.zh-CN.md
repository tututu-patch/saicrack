# Paint Tool SAI Crack v2
PaintTool SAI 软件破解（Ver.1 / Ver.2）

**语言：** [English](README.md) | 中文

---

如需下载最新软件包，请前往官方网站：

https://www.systemax.jp/en/sai/devdept.html

## 支持的包

| 包名 | 程序 | 说明 |
|---|---|---|
| `sai2-20241123-32bit-en` / `64bit` | `sai2.exe` | 旧版 SAI2 — 替换 N + 生成许可证即可 |
| `sai2-20260702b-32bit-en` / `64bit` | `sai2.exe` | **新版 SAI2** — 还需重加密内部 RSA 数据 |
| `sai-1.2.5-ful-en.exe` / `sai-1.2.6-Beta.3-ful-en.exe` | `sai.exe` | SAI1 — 替换 N + 重加密 SEV0 块 |

## 环境要求

- **Python** — https://www.python.org/downloads  
  - 推荐 **Python 3** → 使用 `saicrack_py3.py`  
  - Python 2 → 使用 `saicrack_py2.py`  
  - `saicrack_v2.py` 与 v2 逻辑相同（别名）
- 下载对应系统的 SAI 压缩包 / 安装包（64 位系统建议用 **64-bit**）

## 使用步骤（SAI2）

### 1. 将脚本与 `sai2.exe` 放在同一目录

解压官方 zip 后，把 `saicrack_py3.py` 复制到 `sai2.exe` 所在文件夹。

### 2. 运行破解脚本

在该文件夹打开 **CMD** 或 **PowerShell**，执行：

```bat
python saicrack_py3.py
```

脚本会提示输入 **System ID**。

提示：

- 在文件夹空白处右键 → **在终端中打开** / **Open CMD**
- 或：`cd /d "D:\path\to\sai2"` 后再运行上面的命令

### 3. 打开 SAI2 获取 System ID

打开 SAI2 → **Other** → **System ID ...**

会弹出显示 System ID（8 位十六进制）的窗口。

参考图：

![Tutorial1](Images/Tuto1.png)

![Tutorial2](Images/Tuto2.png)

![Tutorial3](Images/Tuto3.png)

### 4. 输入 System ID

把 SAI2 里显示的 System ID 粘贴到命令行，按 **Enter**。

- 长度必须是 **8**
- 仅允许 `0-9` `a-f` `A-F`
- **不要**加 `0x` 或空格

### 5. 关闭 SAI2，然后输入 OK

请**完全退出** SAI2（确认没有 `sai2.exe` 进程）。  
在命令行输入：

```text
OK
```

然后按 **Enter**。

### 6. 完成

看到 **Crack success!** 后，如有提示可再按 Enter 结束脚本。

生成 / 修改的文件：

| 文件 | 说明 |
|---|---|
| `license.slc` | 绑定当前 System ID 的 128 字节许可证 |
| `sai-crack.slc` | 相同许可证（兼容 SAI1 的 `sai-*.slc` 搜索） |
| `sai2.exe.<时间戳>.bak` | patch 前的原始程序备份 |

重新启动 SAI2 即可。

## 使用步骤（SAI1）

1. 从 `sai-*-ful-en.exe` 中提取 `sai.exe`（安装包在第一个 `PK\x03\x04` 之后是 zip 数据）。
2. 将 `saicrack_py3.py` 与 `sai.exe` 放在同一目录。
3. 运行 `python saicrack_py3.py`，输入 System ID，关闭程序后输入 `OK`。
4. 保持 `license.slc` / `sai-crack.slc` 与 `sai.exe` 同目录。

提取示例（Python）：

```bat
python -c "from pathlib import Path; import zipfile; p=Path('sai-1.2.5-ful-en.exe'); d=p.read_bytes(); i=d.find(b'PK\x03\x04'); zipfile.ZipFile(__import__('io').BytesIO(d[i:])).extractall('sai1_extracted'); print('ok')"
```

## v2 会做什么（简要）

1. 按你的 System ID 生成 `license.slc`（在替换后的模数 **N'** 下用已知私钥指数签名）
2. 把程序里的公钥模数 **N 替换为 N'**
3. 重加密仍依赖旧 **N** 的内部 RSA 包装数据（**新版 SAI2** 与 **SAI1** 需要）

旧版 v1 脚本只替换 **N**，**无法完整处理** `sai2-20260702b`。

## 恢复备份

```bat
copy /y sai2.exe.***********.bak sai2.exe
```

## 脚本文件

| 文件 | 用途 |
|---|---|
| `saicrack_py3.py` | **推荐**（Python 3） |
| `saicrack_py2.py` | Python 2 / 同 v2 逻辑 |
| `saicrack_v2.py` | v2 别名 |

版本：**2.0.0**

## 重要声明（ATTENTION NOTICE）

www.painttoolsai.cn 是未经授权的销售渠道。SYSTEMAX 从未授权任何人销售其产品。

该渠道购买正版许可证后，将同一许可证低价转售给多名用户，违反产品许可协议。

发现非法分发的许可证后可能被吊销。

请勿从未经授权的销售方购买。

## 说明（Notice）

建议从官网下载 SAI：

https://www.systemax.jp/en/sai/devdept.html

---

[English README](README.md)
