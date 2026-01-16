"""
配置管理模块
负责读取和写入 settings.json 配置文件
"""
import json
import os
from pathlib import Path
from typing import Optional, Dict


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = "settings.json"):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = Path(config_file)
        self.config: Dict[str, str] = {}
        self.load_config()
    
    def load_config(self) -> Dict[str, str]:
        """
        加载配置文件
        
        Returns:
            配置字典
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"加载配置文件失败: {e}")
                self.config = {}
        else:
            self.config = {}
        
        return self.config
    
    def save_config(self) -> bool:
        """
        保存配置文件
        
        Returns:
            是否保存成功
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def get_smapi_path(self) -> Optional[str]:
        """
        获取 StardewModdingAPI.exe 路径
        
        Returns:
            SMAPI 路径，不存在则返回 None
        """
        return self.config.get('smapi_path')
    
    def get_game_mods_path(self) -> Optional[str]:
        """
        获取游戏 Mods 目录路径
        
        Returns:
            游戏 Mods 目录路径，不存在则返回 None
        """
        return self.config.get('game_mods_path')
    
    def get_local_mods_path(self) -> str:
        """
        获取本地 Mods 存储目录路径
        
        Returns:
            本地 Mods 目录路径
        """
        local_path = self.config.get('local_mods_path', './mods')
        # 确保目录存在
        Path(local_path).mkdir(parents=True, exist_ok=True)
        return local_path
    
    def set_paths(self, smapi_path: str, game_mods_path: str, local_mods_path: str = './mods') -> bool:
        """
        设置所有路径
        
        Args:
            smapi_path: StardewModdingAPI.exe 路径
            game_mods_path: 游戏 Mods 目录路径
            local_mods_path: 本地 Mods 存储目录路径
            
        Returns:
            是否保存成功
        """
        self.config['smapi_path'] = str(Path(smapi_path).resolve())
        self.config['game_mods_path'] = str(Path(game_mods_path).resolve())
        self.config['local_mods_path'] = str(Path(local_mods_path).resolve())
        return self.save_config()
    
    def is_configured(self) -> bool:
        """
        检查是否已配置
        
        Returns:
            是否已配置 SMAPI 路径和游戏 Mods 路径
        """
        return bool(self.get_smapi_path() and self.get_game_mods_path())
    
    def has_imported_existing_mods(self) -> bool:
        """
        检查是否已导入现有 Mod
        
        Returns:
            是否已导入
        """
        return self.config.get('existing_mods_imported', False)
    
    def set_existing_mods_imported(self, value: bool = True) -> bool:
        """
        设置已导入现有 Mod 的标记
        
        Args:
            value: 是否已导入
            
        Returns:
            是否保存成功
        """
        self.config['existing_mods_imported'] = value
        return self.save_config()
