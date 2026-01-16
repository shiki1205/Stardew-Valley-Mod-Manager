# 星露谷 Mod 管理器

一个前后端分离、模块化设计的星露谷物语 Mod 管理工具。

## 功能特性

- 🔍 **自动查找游戏路径** - 自动搜索 StardewModdingAPI.exe 位置
- 📦 **Mod 管理** - 添加、启用、禁用、删除 Mod
- 💾 **配置持久化** - 首次配置后自动保存，后续直接使用
- 🎨 **图形界面** - 基于 PyQt6 的现代化界面
- 🧩 **模块化设计** - 前后端分离，代码清晰易维护

## 项目结构

```
stardewmod/
├── backend/                 # 后端业务逻辑
│   ├── __init__.py
│   ├── config_manager.py   # 配置管理模块
│   ├── file_finder.py      # 文件查找模块
│   └── mod_manager.py      # Mod 管理模块
├── frontend/                # 前端界面
│   ├── __init__.py
│   ├── main_window.py      # 主窗口
│   └── setup_dialog.py     # 首次设置对话框
├── mods/                    # 本地 Mod 存储目录（自动创建）
├── main.py                  # 程序入口
├── settings.json           # 配置文件（自动生成）
├── requirements.txt        # Python 依赖
├── pyproject.toml         # 项目配置
└── README.md              # 本文件
```

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

## 技术架构

### 后端模块

- **ConfigManager**: 负责配置文件的读取和写入
  - 管理 settings.json 配置
  - 提供路径获取和设置接口

- **FileFinder**: 负责查找 StardewModdingAPI.exe
  - 搜索常见 Steam 安装路径
  - 支持多盘符搜索

- **ModManager**: 负责 Mod 的核心操作
  - 添加 Mod 到本地库
  - 启用/禁用 Mod（解压/删除）
  - 列出本地和已启用的 Mod
  - 智能识别 Mod 结构（manifest.json）

### 前端模块

- **MainWindow**: 主窗口界面
  - 显示本地 Mod 列表和已启用 Mod 列表
  - 提供 Mod 操作按钮
  - 状态显示和反馈

- **SetupDialog**: 首次设置对话框
  - 自动查找 SMAPI 路径
  - 手动选择路径
  - 保存配置

## 配置文件

`settings.json` 示例：

```json
{
    "smapi_path": "C:/Program Files (x86)/Steam/steamapps/common/Stardew Valley/StardewModdingAPI.exe",
    "game_mods_path": "C:/Program Files (x86)/Steam/steamapps/common/Stardew Valley/Mods",
    "local_mods_path": "F:/stardewmod/mods"
}
```

## 注意事项

- 仅支持 ZIP 格式的 Mod 压缩包
- Mod 必须包含有效的 `manifest.json` 文件
- 启用 Mod 前请确保游戏已关闭
- 建议定期备份游戏存档

## 系统要求

- Python 3.8+
- PyQt6 6.6.0+
- Windows 系统（支持 Steam 版星露谷物语）

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
