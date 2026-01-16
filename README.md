# 星露谷 Mod 管理器

一个前后端分离、模块化设计的星露谷物语 Mod 管理工具。

## 使用前须知

使用此Mod管理器前，应先正确安装SMAPI

## 系统要求

- Python 3.8+
- PyQt6 6.6.0+
- Windows 系统（支持 Steam 版星露谷物语）

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

或使用 uv：

```bash
uv pip install -r requirements.txt
```

### 2. 运行程序

```bash
python main.py
```

## 使用说明

### 首次启动

1. 程序会自动搜索 StardewModdingAPI.exe 的位置
2. 如果找到，自动填充路径；如果未找到，需要手动选择
3. 点击"确定"保存配置

### 添加 Mod

支持直接鼠标拖入添加，也可以按如下方式添加：

1. 点击"添加 Mod"按钮
2. 选择 Mod 的 ZIP 压缩包
3. Mod 会被复制到本地 `mods/` 目录

### 启用 Mod

1. 在"本地 Mod 列表"中选择要启用的 Mod
2. 点击"启用"按钮
3. Mod 会被解压并移动到游戏的 Mods 目录

### 禁用 Mod

1. 在"已启用 Mod 列表"中选择要禁用的 Mod
2. 点击"禁用"按钮
3. Mod 会从游戏的 Mods 目录中删除（本地副本仍保留）

### 删除 Mod

1. 在"本地 Mod 列表"中选择要删除的 Mod
2. 点击"删除"按钮
3. 如果 Mod 已启用，会先自动禁用再删除
