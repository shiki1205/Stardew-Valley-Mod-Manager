"""
首次设置对话框
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QFileDialog, QMessageBox,
    QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from pathlib import Path

from backend.file_finder import FileFinder


class FindSmapiThread(QThread):
    """查找 SMAPI 的线程"""
    found = pyqtSignal(str)
    not_found = pyqtSignal()
    
    def run(self):
        smapi_path = FileFinder.find_smapi_exe()
        if smapi_path:
            self.found.emit(smapi_path)
        else:
            self.not_found.emit()


class SetupDialog(QDialog):
    """首次设置对话框"""
    
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.smapi_path = ""
        self.game_mods_path = ""
        self.init_ui()
        
        # 自动查找 SMAPI
        self.auto_find_smapi()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("首次设置 - 星露谷 Mod 管理器")
        self.setMinimumWidth(600)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # 说明文字
        info_label = QLabel(
            "欢迎使用星露谷 Mod 管理器！\n\n"
            "请配置 StardewModdingAPI.exe 的位置。\n"
            "程序将自动查找常见安装路径，您也可以手动选择。"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # 不确定进度
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        # SMAPI 路径
        smapi_layout = QHBoxLayout()
        smapi_layout.addWidget(QLabel("SMAPI 路径:"))
        
        self.smapi_path_edit = QLineEdit()
        self.smapi_path_edit.setReadOnly(True)
        smapi_layout.addWidget(self.smapi_path_edit)
        
        browse_smapi_btn = QPushButton("浏览...")
        browse_smapi_btn.clicked.connect(self.browse_smapi)
        smapi_layout.addWidget(browse_smapi_btn)
        
        layout.addLayout(smapi_layout)
        
        # Mods 路径
        mods_layout = QHBoxLayout()
        mods_layout.addWidget(QLabel("Mods 目录:"))
        
        self.mods_path_edit = QLineEdit()
        self.mods_path_edit.setReadOnly(True)
        mods_layout.addWidget(self.mods_path_edit)
        
        layout.addLayout(mods_layout)
        
        # 状态标签
        self.status_label = QLabel("正在自动查找 StardewModdingAPI.exe...")
        self.status_label.setStyleSheet("color: blue;")
        layout.addWidget(self.status_label)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.ok_btn = QPushButton("确定")
        self.ok_btn.clicked.connect(self.accept_settings)
        self.ok_btn.setEnabled(False)
        button_layout.addWidget(self.ok_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def auto_find_smapi(self):
        """自动查找 SMAPI"""
        self.progress_bar.show()
        self.status_label.setText("正在自动查找 StardewModdingAPI.exe...")
        
        self.find_thread = FindSmapiThread()
        self.find_thread.found.connect(self.on_smapi_found)
        self.find_thread.not_found.connect(self.on_smapi_not_found)
        self.find_thread.start()
    
    def on_smapi_found(self, smapi_path):
        """SMAPI 查找成功"""
        self.progress_bar.hide()
        self.smapi_path = smapi_path
        self.smapi_path_edit.setText(smapi_path)
        
        # 自动设置 Mods 路径
        mods_path = FileFinder.get_mods_path(smapi_path)
        if mods_path:
            self.game_mods_path = mods_path
            self.mods_path_edit.setText(mods_path)
        
        self.status_label.setText("已自动找到 SMAPI 路径")
        self.status_label.setStyleSheet("color: green;")
        self.ok_btn.setEnabled(True)
    
    def on_smapi_not_found(self):
        """SMAPI 查找失败"""
        self.progress_bar.hide()
        self.status_label.setText("未找到 SMAPI，请手动选择 StardewModdingAPI.exe")
        self.status_label.setStyleSheet("color: red;")
    
    def browse_smapi(self):
        """浏览 SMAPI 文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择 StardewModdingAPI.exe",
            "",
            "可执行文件 (*.exe)"
        )
        
        if file_path:
            if Path(file_path).name != "StardewModdingAPI.exe":
                QMessageBox.warning(self, "警告", "请选择 StardewModdingAPI.exe 文件")
                return
            
            self.smapi_path = file_path
            self.smapi_path_edit.setText(file_path)
            
            # 自动设置 Mods 路径
            mods_path = FileFinder.get_mods_path(file_path)
            if mods_path:
                self.game_mods_path = mods_path
                self.mods_path_edit.setText(mods_path)
            
            self.status_label.setText("路径已设置")
            self.status_label.setStyleSheet("color: green;")
            self.ok_btn.setEnabled(True)
    
    def accept_settings(self):
        """接受设置"""
        if not self.smapi_path or not self.game_mods_path:
            QMessageBox.warning(self, "警告", "请先选择 SMAPI 路径")
            return
        
        # 保存配置
        local_mods_path = str(Path("./mods").resolve())
        if self.config_manager.set_paths(
            self.smapi_path,
            self.game_mods_path,
            local_mods_path
        ):
            QMessageBox.information(self, "成功", "配置已保存")
            self.accept()
        else:
            QMessageBox.critical(self, "错误", "保存配置失败")
