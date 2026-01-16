"""
文件查找模块
负责查找 StardewModdingAPI.exe 的位置
"""
import os
from pathlib import Path
from typing import Optional, List


class FileFinder:
    """文件查找器"""
    
    @staticmethod
    def find_smapi_exe() -> Optional[str]:
        """
        在常见位置查找 StardewModdingAPI.exe
        
        Returns:
            StardewModdingAPI.exe 的路径，未找到返回 None
        """
        # 常见的 Steam 游戏安装路径
        common_paths = [
            r"C:\Program Files (x86)\Steam\steamapps\common\Stardew Valley",
            r"C:\Program Files\Steam\steamapps\common\Stardew Valley",
            r"D:\Steam\steamapps\common\Stardew Valley",
            r"E:\Steam\steamapps\common\Stardew Valley",
            r"D:\SteamLibrary\steamapps\common\Stardew Valley",
            r"E:\SteamLibrary\steamapps\common\Stardew Valley",
        ]
        
        # 检查常见路径
        for path in common_paths:
            smapi_path = Path(path) / "StardewModdingAPI.exe"
            if smapi_path.exists():
                return str(smapi_path.resolve())
        
        # 在所有盘符的 Steam 目录中搜索
        for drive in FileFinder._get_available_drives():
            search_paths = [
                Path(f"{drive}:\\Steam\\steamapps\\common\\Stardew Valley"),
                Path(f"{drive}:\\SteamLibrary\\steamapps\\common\\Stardew Valley"),
                Path(f"{drive}:\\Program Files (x86)\\Steam\\steamapps\\common\\Stardew Valley"),
                Path(f"{drive}:\\Program Files\\Steam\\steamapps\\common\\Stardew Valley"),
            ]
            
            for search_path in search_paths:
                smapi_path = search_path / "StardewModdingAPI.exe"
                if smapi_path.exists():
                    return str(smapi_path.resolve())
        
        return None
    
    @staticmethod
    def _get_available_drives() -> List[str]:
        """
        获取所有可用的盘符
        
        Returns:
            盘符列表
        """
        drives = []
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            drive = f"{letter}:"
            if os.path.exists(drive):
                drives.append(letter)
        return drives
    
    @staticmethod
    def get_mods_path(smapi_path: str) -> Optional[str]:
        """
        根据 StardewModdingAPI.exe 路径获取 Mods 目录路径
        
        Args:
            smapi_path: StardewModdingAPI.exe 路径
            
        Returns:
            Mods 目录路径，不存在则返回 None
        """
        smapi_dir = Path(smapi_path).parent
        mods_dir = smapi_dir / "Mods"
        
        if mods_dir.exists() and mods_dir.is_dir():
            return str(mods_dir.resolve())
        
        # 如果不存在，尝试创建
        try:
            mods_dir.mkdir(parents=True, exist_ok=True)
            return str(mods_dir.resolve())
        except Exception as e:
            print(f"创建 Mods 目录失败: {e}")
            return None
