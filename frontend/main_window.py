"""
主窗口模块
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QListWidget, QLabel, QMessageBox,
    QFileDialog, QListWidgetItem, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt6.QtGui import QIcon, QDragEnterEvent, QDropEvent
from pathlib import Path
import sys

from backend.config_manager import ConfigManager
from backend.file_finder import FileFinder
from backend.mod_manager import ModManager
from .setup_dialog import SetupDialog


class ModRefreshThread(QThread):
    """Mod 列表刷新线程"""
    finished = pyqtSignal(list)
    
    def __init__(self, mod_manager):
        super().__init__()
        self.mod_manager = mod_manager
    
    def run(self):
        mods = self.mod_manager.list_local_mods()
        self.finished.emit(mods)


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.mod_manager = None
        
        # 检查是否首次启动
        if not self.config_manager.is_configured():
            self.show_setup_dialog()
        
        # 初始化 Mod 管理器
        if self.config_manager.is_configured():
            self.init_mod_manager()
            
            # 检查是否需要导入现有 Mod
            if not self.config_manager.has_imported_existing_mods():
                self.import_existing_mods()
        
        self.init_ui()
        self.refresh_mod_list()
    
    def init_mod_manager(self):
        """初始化 Mod 管理器"""
        local_mods_path = self.config_manager.get_local_mods_path()
        game_mods_path = self.config_manager.get_game_mods_path()
        
        if local_mods_path and game_mods_path:
            self.mod_manager = ModManager(local_mods_path, game_mods_path)
    
    def show_setup_dialog(self):
        """显示首次设置对话框"""
        dialog = SetupDialog(self.config_manager)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self.init_mod_manager()
        else:
            # 用户取消设置，退出程序
            QMessageBox.critical(self, "错误", "未完成初始设置，程序将退出")
            sys.exit(1)
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("星露谷 Mod 管理器")
        self.setMinimumSize(800, 600)
        
        # 启用拖放功能
        self.setAcceptDrops(True)
        
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 顶部信息栏
        info_layout = QHBoxLayout()
        self.info_label = QLabel()
        self.update_info_label()
        info_layout.addWidget(self.info_label)
        info_layout.addStretch()
        
        settings_btn = QPushButton("重新配置路径")
        settings_btn.clicked.connect(self.show_setup_dialog)
        info_layout.addWidget(settings_btn)
        
        main_layout.addLayout(info_layout)
        
        # 分隔器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：本地 Mod 列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # 添加提示标签
        hint_label = QLabel("本地 Mod 列表（可拖入 ZIP 文件添加）")
        hint_label.setStyleSheet("color: #666; font-style: italic;")
        left_layout.addWidget(hint_label)
        
        self.local_mods_list = QListWidget()
        self.local_mods_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        left_layout.addWidget(self.local_mods_list)
        
        # 本地 Mod 操作按钮
        local_btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("添加 Mod")
        add_btn.clicked.connect(self.add_mod)
        local_btn_layout.addWidget(add_btn)
        
        enable_btn = QPushButton("启用")
        enable_btn.clicked.connect(self.enable_mod)
        local_btn_layout.addWidget(enable_btn)
        
        delete_btn = QPushButton("删除")
        delete_btn.clicked.connect(self.delete_local_mod)
        local_btn_layout.addWidget(delete_btn)
        
        left_layout.addLayout(local_btn_layout)
        
        # 右侧：已启用 Mod 列表
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        right_layout.addWidget(QLabel("已启用 Mod 列表"))
        
        self.enabled_mods_list = QListWidget()
        self.enabled_mods_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        right_layout.addWidget(self.enabled_mods_list)
        
        # 已启用 Mod 操作按钮
        enabled_btn_layout = QHBoxLayout()
        
        disable_btn = QPushButton("禁用")
        disable_btn.clicked.connect(self.disable_mod)
        enabled_btn_layout.addWidget(disable_btn)
        
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.refresh_mod_list)
        enabled_btn_layout.addWidget(refresh_btn)
        
        right_layout.addLayout(enabled_btn_layout)
        
        # 添加到分隔器
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 400])
        
        main_layout.addWidget(splitter)
        
        # 底部状态栏
        self.status_label = QLabel("就绪")
        main_layout.addWidget(self.status_label)
    
    def update_info_label(self):
        """更新信息标签"""
        smapi_path = self.config_manager.get_smapi_path()
        if smapi_path:
            self.info_label.setText(f"游戏路径: {Path(smapi_path).parent}")
        else:
            self.info_label.setText("未配置游戏路径")
    
    def refresh_mod_list(self):
        """刷新 Mod 列表"""
        if not self.mod_manager:
            return
        
        self.status_label.setText("正在刷新...")
        
        # 刷新本地 Mod 列表
        local_mods = self.mod_manager.list_local_mods()
        self.local_mods_list.clear()
        
        for mod in local_mods:
            # 构建显示文本
            display_name = mod['name']
            
            # 如果包含多个 Mod，显示数量
            if mod.get('mod_count', 1) > 1:
                display_name += f" ({mod['mod_count']} 个Mod)"
            
            # 如果已启用，添加标记
            if mod['enabled']:
                display_name += " [已启用]"
            
            item = QListWidgetItem(display_name)
            item.setData(Qt.ItemDataRole.UserRole, mod)
            
            self.local_mods_list.addItem(item)
        
        # 刷新已启用 Mod 列表
        enabled_mods = self.mod_manager.list_enabled_mods()
        self.enabled_mods_list.clear()
        
        for mod_name in enabled_mods:
            self.enabled_mods_list.addItem(mod_name)
        
        self.status_label.setText(f"就绪 - 本地: {len(local_mods)} 个, 已启用: {len(enabled_mods)} 个")
    
    def add_mod(self):
        """添加 Mod"""
        if not self.mod_manager:
            QMessageBox.warning(self, "警告", "请先配置游戏路径")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择 Mod 文件",
            "",
            "Zip 文件 (*.zip)"
        )
        
        if file_path:
            self.status_label.setText("正在添加 Mod...")
            if self.mod_manager.add_mod(file_path):
                QMessageBox.information(self, "成功", "Mod 已添加到本地库")
                self.refresh_mod_list()
            else:
                QMessageBox.critical(self, "错误", "添加 Mod 失败")
                self.status_label.setText("添加失败")
    
    def enable_mod(self):
        """启用 Mod"""
        if not self.mod_manager:
            QMessageBox.warning(self, "警告", "请先配置游戏路径")
            return
        
        current_item = self.local_mods_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择一个 Mod")
            return
        
        mod_data = current_item.data(Qt.ItemDataRole.UserRole)
        
        if mod_data['enabled']:
            QMessageBox.information(self, "提示", "该 Mod 已启用")
            return
        
        self.status_label.setText("正在启用 Mod...")
        if self.mod_manager.enable_mod(mod_data['filename']):
            mod_count = mod_data.get('mod_count', 1)
            if mod_count > 1:
                QMessageBox.information(
                    self, 
                    "成功", 
                    f"已启用 '{mod_data['name']}' 中的 {mod_count} 个 Mod"
                )
            else:
                QMessageBox.information(self, "成功", f"Mod '{mod_data['name']}' 已启用")
            self.refresh_mod_list()
        else:
            QMessageBox.critical(self, "错误", "启用 Mod 失败")
            self.status_label.setText("启用失败")
    
    def disable_mod(self):
        """禁用 Mod"""
        if not self.mod_manager:
            QMessageBox.warning(self, "警告", "请先配置游戏路径")
            return
        
        current_item = self.enabled_mods_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择一个已启用的 Mod")
            return
        
        mod_name = current_item.text()
        
        reply = QMessageBox.question(
            self,
            "确认",
            f"确定要禁用 Mod '{mod_name}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.status_label.setText("正在禁用 Mod...")
            if self.mod_manager.disable_mod(mod_name):
                QMessageBox.information(self, "成功", f"Mod '{mod_name}' 已禁用")
                self.refresh_mod_list()
            else:
                QMessageBox.critical(self, "错误", "禁用 Mod 失败")
                self.status_label.setText("禁用失败")
    
    def delete_local_mod(self):
        """删除本地 Mod"""
        if not self.mod_manager:
            QMessageBox.warning(self, "警告", "请先配置游戏路径")
            return
        
        current_item = self.local_mods_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择一个 Mod")
            return
        
        mod_data = current_item.data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self,
            "确认",
            f"确定要删除 Mod '{mod_data['name']}' 吗？\n注意：如果该 Mod 已启用，需要先禁用。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 如果已启用，先禁用
            if mod_data['enabled']:
                enabled_mods = self.mod_manager.list_enabled_mods()
                for enabled_mod in enabled_mods:
                    if enabled_mod.lower() == mod_data['name'].lower():
                        self.mod_manager.disable_mod(enabled_mod)
                        break
            
            self.status_label.setText("正在删除 Mod...")
            if self.mod_manager.delete_local_mod(mod_data['filename']):
                QMessageBox.information(self, "成功", f"Mod '{mod_data['name']}' 已删除")
                self.refresh_mod_list()
            else:
                QMessageBox.critical(self, "错误", "删除 Mod 失败")
                self.status_label.setText("删除失败")
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """处理拖入事件"""
        if event.mimeData().hasUrls():
            # 检查是否包含 ZIP 文件
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith('.zip'):
                    event.acceptProposedAction()
                    return
        event.ignore()
    
    def dropEvent(self, event: QDropEvent):
        """处理放下事件"""
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        zip_files = [f for f in files if f.lower().endswith('.zip')]
        
        if zip_files:
            self.handle_dropped_files(zip_files)
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def handle_dropped_files(self, file_paths):
        """处理拖放的文件"""
        if not self.mod_manager:
            QMessageBox.warning(self, "警告", "请先配置游戏路径")
            return
        
        success_count = 0
        fail_count = 0
        
        for file_path in file_paths:
            self.status_label.setText(f"正在添加: {Path(file_path).name}...")
            if self.mod_manager.add_mod(file_path):
                success_count += 1
            else:
                fail_count += 1
        
        # 刷新列表
        self.refresh_mod_list()
        
        # 显示结果
        if success_count > 0 and fail_count == 0:
            QMessageBox.information(
                self, 
                "成功", 
                f"成功添加 {success_count} 个 Mod"
            )
        elif success_count > 0 and fail_count > 0:
            QMessageBox.warning(
                self, 
                "部分成功", 
                f"成功添加 {success_count} 个 Mod，失败 {fail_count} 个"
            )
        else:
            QMessageBox.critical(
                self, 
                "失败", 
                f"添加 Mod 失败，共 {fail_count} 个文件"
            )
    
    def import_existing_mods(self):
        """导入游戏目录中已有的 Mod"""
        if not self.mod_manager:
            return
        
        # 显示确认对话框
        reply = QMessageBox.question(
            self,
            "导入现有 Mod",
            "检测到您的游戏目录中已有 Mod。\n\n"
            "是否将这些 Mod 导入到本地库？\n"
            "这样可以方便您管理和备份这些 Mod。\n\n"
            "注意：导入过程会将 Mod 打包成 ZIP 文件，不会影响游戏中的 Mod。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if reply == QMessageBox.StandardButton.No:
            # 用户选择不导入，标记为已处理
            self.config_manager.set_existing_mods_imported(True)
            return
        
        # 显示进度对话框
        from PyQt6.QtWidgets import QProgressDialog
        progress = QProgressDialog("正在导入现有 Mod...", None, 0, 0, self)
        progress.setWindowTitle("导入 Mod")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.setCancelButton(None)
        progress.show()
        
        # 执行导入
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, lambda: self._do_import_existing_mods(progress))
    
    def _do_import_existing_mods(self, progress_dialog):
        """执行导入现有 Mod 的操作"""
        result = self.mod_manager.import_existing_mods()
        progress_dialog.close()
        
        # 标记为已导入
        self.config_manager.set_existing_mods_imported(True)
        
        # 刷新列表
        self.refresh_mod_list()
        
        # 显示结果
        if result['success'] > 0 or result['failed'] > 0:
            msg = f"导入完成！\n\n"
            msg += f"成功导入: {result['success']} 个 Mod\n"
            
            if result['failed'] > 0:
                msg += f"失败: {result['failed']} 个\n"
            
            if result['mods']:
                msg += f"\n已导入的 Mod：\n"
                msg += "\n".join(f"  • {mod}" for mod in result['mods'][:10])
                if len(result['mods']) > 10:
                    msg += f"\n  ... 还有 {len(result['mods']) - 10} 个"
            
            if result['errors']:
                msg += f"\n\n错误信息：\n"
                msg += "\n".join(f"  • {err}" for err in result['errors'][:5])
                if len(result['errors']) > 5:
                    msg += f"\n  ... 还有 {len(result['errors']) - 5} 个错误"
            
            if result['failed'] > 0:
                QMessageBox.warning(self, "导入完成", msg)
            else:
                QMessageBox.information(self, "导入完成", msg)
        else:
            QMessageBox.information(
                self,
                "导入完成",
                "游戏目录中没有发现可导入的 Mod。"
            )
