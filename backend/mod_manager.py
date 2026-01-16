"""
Mod 管理模块
负责 Mod 的添加、启用、禁用等操作
"""
import os
import shutil
import zipfile
from pathlib import Path
from typing import List, Dict, Optional
import json
import re


class ModManager:
    """Mod 管理器"""
    
    def __init__(self, local_mods_path: str, game_mods_path: str):
        """
        初始化 Mod 管理器
        
        Args:
            local_mods_path: 本地 Mod 存储路径
            game_mods_path: 游戏 Mods 目录路径
        """
        self.local_mods_path = Path(local_mods_path)
        self.game_mods_path = Path(game_mods_path)
        
        # 确保目录存在
        self.local_mods_path.mkdir(parents=True, exist_ok=True)
        self.game_mods_path.mkdir(parents=True, exist_ok=True)
    
    def list_local_mods(self) -> List[Dict[str, str]]:
        """
        列出本地所有 Mod 压缩包
        
        Returns:
            Mod 列表，每个元素包含 name、filename、path、enabled 和 mod_count
        """
        mods = []
        for file in self.local_mods_path.glob("*.zip"):
            mod_count = self._count_mods_in_zip(file)
            mods.append({
                'name': file.stem,
                'filename': file.name,
                'path': str(file),
                'enabled': self._is_mod_enabled(file.stem),
                'mod_count': mod_count  # 压缩包中包含的 Mod 数量
            })
        return mods
    
    def list_enabled_mods(self) -> List[str]:
        """
        列出所有已启用的 Mod（游戏 Mods 目录中的文件夹）
        
        Returns:
            已启用的 Mod 名称列表
        """
        enabled_mods = []
        if self.game_mods_path.exists():
            for item in self.game_mods_path.iterdir():
                if item.is_dir():
                    enabled_mods.append(item.name)
        return enabled_mods
    
    def _is_mod_enabled(self, mod_name: str) -> bool:
        """
        检查 Mod 是否已启用
        检查游戏 Mods 目录中是否存在以压缩包名命名的主目录
        
        Args:
            mod_name: Mod 名称（压缩包文件名，不含扩展名）
            
        Returns:
            是否已启用
        """
        # 检查游戏 Mods 目录中是否存在以压缩包名命名的主目录
        main_dir = self.game_mods_path / mod_name
        return main_dir.exists() and main_dir.is_dir()
    
    def _count_mods_in_zip(self, zip_path: Path) -> int:
        """
        统计压缩包中包含的 Mod 数量
        
        Args:
            zip_path: 压缩包路径
            
        Returns:
            Mod 数量
        """
        try:
            temp_dir = self.local_mods_path / f"_count_{zip_path.stem}"
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            temp_dir.mkdir()
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            mod_roots = self._find_all_mod_roots(temp_dir)
            count = len(mod_roots)
            
            # 清理临时目录
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            
            return count
        except Exception:
            return 1  # 出错时默认返回 1
    
    def add_mod(self, source_path: str) -> bool:
        """
        添加 Mod 到本地存储
        
        Args:
            source_path: Mod 压缩包源路径
            
        Returns:
            是否添加成功
        """
        try:
            source = Path(source_path)
            if not source.exists():
                print(f"文件不存在: {source_path}")
                return False
            
            if source.suffix.lower() != '.zip':
                print(f"仅支持 ZIP 格式的 Mod 文件")
                return False
            
            # 复制到本地 Mods 目录
            destination = self.local_mods_path / source.name
            shutil.copy2(source, destination)
            print(f"Mod 已添加: {source.name}")
            return True
            
        except Exception as e:
            print(f"添加 Mod 失败: {e}")
            return False
    
    def enable_mod(self, mod_filename: str) -> bool:
        """
        启用 Mod（解压到游戏 Mods 目录）
        解压后保持主目录结构，便于统一管理和禁用
        
        Args:
            mod_filename: Mod 文件名
            
        Returns:
            是否启用成功
        """
        try:
            mod_path = self.local_mods_path / mod_filename
            if not mod_path.exists():
                print(f"Mod 文件不存在: {mod_filename}")
                return False
            
            # 使用压缩包名（不含扩展名）作为主目录名
            mod_name = mod_path.stem
            main_dir = self.game_mods_path / mod_name
            
            # 如果已启用，先删除
            if main_dir.exists():
                shutil.rmtree(main_dir)
            
            # 解压到临时目录
            temp_dir = self.local_mods_path / f"_temp_{mod_name}"
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            temp_dir.mkdir()
            
            with zipfile.ZipFile(mod_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # 查找所有的 Mod 根目录（包含 manifest.json 的目录）
            mod_roots = self._find_all_mod_roots(temp_dir)
            if not mod_roots:
                print(f"未找到有效的 Mod 结构（缺少 manifest.json）")
                shutil.rmtree(temp_dir)
                return False
            
            # 创建主目录
            main_dir.mkdir(parents=True, exist_ok=True)
            
            # 根据 mod 数量决定目录结构
            if len(mod_roots) == 1:
                # 单个 mod：主目录下直接是 mod 文件（manifest.json 等）
                mod_root = mod_roots[0]
                for item in mod_root.iterdir():
                    dest = main_dir / item.name
                    if dest.exists():
                        if dest.is_dir():
                            shutil.rmtree(dest)
                        else:
                            dest.unlink()
                    shutil.move(str(item), str(dest))
                print(f"Mod 已启用: {mod_name}（单个 Mod）")
            else:
                # 多个 mod：主目录下是各个 mod 的文件夹
                for mod_root in mod_roots:
                    mod_folder_name = mod_root.name
                    dest = main_dir / mod_folder_name
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.move(str(mod_root), str(dest))
                print(f"Mod 已启用: {mod_name}（包含 {len(mod_roots)} 个 Mod）")
                for mod_root in mod_roots:
                    print(f"  - {mod_root.name}")
            
            # 清理临时目录
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            
            return True
            
        except Exception as e:
            print(f"启用 Mod 失败: {e}")
            # 清理临时目录和可能创建的主目录
            temp_dir = self.local_mods_path / f"_temp_{Path(mod_filename).stem}"
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            main_dir = self.game_mods_path / Path(mod_filename).stem
            if main_dir.exists():
                shutil.rmtree(main_dir)
            return False
    
    def disable_mod(self, mod_name: str) -> bool:
        """
        禁用 Mod（删除游戏 Mods 目录中的主目录）
        删除整个主目录及其下的所有 Mod
        
        Args:
            mod_name: Mod 名称（压缩包文件名，不含扩展名）
            
        Returns:
            是否禁用成功
        """
        try:
            main_dir = self.game_mods_path / mod_name
            if not main_dir.exists():
                print(f"Mod 未启用: {mod_name}")
                return False
            
            # 统计将要删除的 Mod 数量
            mod_count = len(self._find_all_mod_roots(main_dir))
            
            shutil.rmtree(main_dir)
            print(f"Mod 已禁用: {mod_name}（包含 {mod_count} 个 Mod）")
            return True
            
        except Exception as e:
            print(f"禁用 Mod 失败: {e}")
            return False
    
    def _find_mod_root(self, extract_path: Path) -> Optional[Path]:
        """
        查找 Mod 的根目录（包含 manifest.json 的目录）
        仅返回第一个找到的 Mod（兼容旧版本）
        
        Args:
            extract_path: 解压路径
            
        Returns:
            Mod 根目录路径，未找到返回 None
        """
        mods = self._find_all_mod_roots(extract_path)
        return mods[0] if mods else None
    
    def _find_all_mod_roots(self, extract_path: Path) -> List[Path]:
        """
        查找所有 Mod 的根目录（包含 manifest.json 的目录）
        支持一个压缩包中包含多个 Mod
        
        Args:
            extract_path: 解压路径
            
        Returns:
            Mod 根目录列表
        """
        mod_roots = []
        
        # 检查当前目录
        if (extract_path / "manifest.json").exists():
            mod_roots.append(extract_path)
            return mod_roots
        
        # 递归查找所有包含 manifest.json 的目录（最多三层）
        def find_in_dir(path: Path, depth: int = 0, max_depth: int = 3):
            if depth > max_depth:
                return
            
            try:
                for item in path.iterdir():
                    if item.is_dir():
                        # 如果找到 manifest.json，添加到列表
                        if (item / "manifest.json").exists():
                            mod_roots.append(item)
                        else:
                            # 继续在子目录中查找
                            find_in_dir(item, depth + 1, max_depth)
            except (PermissionError, OSError):
                pass
        
        find_in_dir(extract_path)
        return mod_roots
    
    def _load_json_with_comments(self, file_path: Path) -> dict:
        """
        加载可能包含注释的 JSON 文件（SMAPI 支持带注释的 JSON）
        
        Args:
            file_path: JSON 文件路径
            
        Returns:
            解析后的字典
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 移除单行注释 // ...
            content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
            
            # 移除多行注释 /* ... */
            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
            
            # 移除尾随逗号（JSON 不允许，但 SMAPI 允许）
            content = re.sub(r',(\s*[}\]])', r'\1', content)
            
            return json.loads(content)
        except Exception as e:
            print(f"解析 JSON 文件失败 ({file_path}): {e}")
            raise
    
    def _get_mod_name_from_manifest(self, mod_root: Path) -> Optional[str]:
        """
        从 manifest.json 获取 Mod 的 UniqueID
        注意：此方法主要用于检测已启用状态，不用于文件夹命名
        
        Args:
            mod_root: Mod 根目录
            
        Returns:
            Mod 的 UniqueID，失败返回 None
        """
        try:
            manifest_file = mod_root / "manifest.json"
            if manifest_file.exists():
                manifest = self._load_json_with_comments(manifest_file)
                # 返回 UniqueID 用于准确匹配已启用的 Mod
                return manifest.get('UniqueID', None)
        except Exception as e:
            print(f"读取 manifest.json 失败: {e}")
        
        return None
    
    def delete_local_mod(self, mod_filename: str) -> bool:
        """
        删除本地 Mod 文件
        
        Args:
            mod_filename: Mod 文件名
            
        Returns:
            是否删除成功
        """
        try:
            mod_path = self.local_mods_path / mod_filename
            if not mod_path.exists():
                print(f"Mod 文件不存在: {mod_filename}")
                return False
            
            mod_path.unlink()
            print(f"Mod 已删除: {mod_filename}")
            return True
            
        except Exception as e:
            print(f"删除 Mod 失败: {e}")
            return False
    
    def import_existing_mods(self) -> Dict[str, any]:
        """
        导入游戏目录中已有的 Mod（首次使用时调用）
        将已存在的 Mod 文件夹打包成 ZIP 并保存到本地库
        
        Returns:
            包含导入结果的字典 {success: int, failed: int, mods: List[str]}
        """
        result = {
            'success': 0,
            'failed': 0,
            'mods': [],
            'errors': []
        }
        
        if not self.game_mods_path.exists():
            return result
        
        # 遍历游戏 Mods 目录中的所有文件夹
        for item in self.game_mods_path.iterdir():
            if not item.is_dir():
                continue
            
            mod_name = item.name
            
            # 跳过系统文件夹或特殊文件夹
            if mod_name.startswith('.') or mod_name.startswith('_'):
                continue
            
            # 检查是否包含 manifest.json
            manifest_path = item / "manifest.json"
            if not manifest_path.exists():
                print(f"跳过 '{mod_name}'：缺少 manifest.json")
                continue
            
            # 检查是否已经在本地库中
            zip_filename = f"{mod_name}.zip"
            local_zip_path = self.local_mods_path / zip_filename
            
            if local_zip_path.exists():
                print(f"跳过 '{mod_name}'：本地库中已存在")
                result['mods'].append(mod_name)
                continue
            
            # 打包 Mod 文件夹
            try:
                print(f"正在导入 Mod: {mod_name}")
                
                # 创建 ZIP 文件
                with zipfile.ZipFile(local_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    # 递归添加文件夹中的所有文件
                    for root, dirs, files in os.walk(item):
                        for file in files:
                            file_path = Path(root) / file
                            # 计算相对路径（保持文件夹结构）
                            arcname = file_path.relative_to(item.parent)
                            zipf.write(file_path, arcname)
                
                result['success'] += 1
                result['mods'].append(mod_name)
                print(f"成功导入: {mod_name}")
                
            except Exception as e:
                result['failed'] += 1
                error_msg = f"{mod_name}: {str(e)}"
                result['errors'].append(error_msg)
                print(f"导入 Mod '{mod_name}' 失败: {e}")
                
                # 删除可能创建的不完整文件
                if local_zip_path.exists():
                    try:
                        local_zip_path.unlink()
                    except:
                        pass
        
        return result