from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QLocale, QSize, Qt, QThread, QUrl, Signal
from PySide6.QtGui import QAction, QDesktopServices, QDragEnterEvent, QDropEvent, QIcon, QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QScrollArea,
    QSlider,
    QSpinBox,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from rotopixel.palettes import palette_names
from rotopixel.processor import RotoscopeSettings, process_video, sample_frame


APP_ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
ASSET_DIR = APP_ROOT / "assets"
EXPORT_DIR = Path.cwd() / "exports"
EXPORT_DIR.mkdir(exist_ok=True)

TEXT = {
    "en": {
        "app_caption": "Rotoscoped pixel-video studio",
        "menu_file": "File",
        "menu_settings": "Settings",
        "menu_pipeline": "Pipeline",
        "menu_view": "View",
        "menu_help": "Help",
        "action_open": "Open Video",
        "action_preview": "Render Preview",
        "action_export": "Export MP4",
        "action_open_exports": "Open Exports Folder",
        "action_quit": "Quit",
        "action_reset": "Reset Style",
        "action_language_zh": "Chinese UI",
        "action_language_en": "English UI",
        "action_pipeline_overview": "Current Pipeline",
        "action_toggle_frame_limit": "Toggle Test Frame Limit",
        "action_about": "About Cucumber",
        "drop_title": "Drop a video here",
        "drop_subtitle": "MP4, MOV, AVI, MKV, or WEBM",
        "preview_title": "Preview frame",
        "preview_subtitle": "Tune the style, then export.",
        "no_video": "No video selected",
        "choose_video": "Choose video",
        "language": "Language",
        "palette": "Palette",
        "pixel_size": "Pixel size",
        "width": "Width",
        "color_levels": "Color levels",
        "ink_strength": "Ink strength",
        "line_weight": "Line weight",
        "edge_low": "Edge low",
        "edge_high": "Edge high",
        "fps": "FPS",
        "preview_time": "Preview time",
        "limit_export": "Limit export while testing",
        "frame_limit": "Frame limit",
        "render_preview": "Render preview",
        "export_mp4": "Export MP4",
        "ready": "Ready",
        "video_loaded": "Video loaded",
        "rendering_preview": "Rendering preview...",
        "preview_ready": "Preview ready",
        "choose_video_dialog": "Choose a video",
        "video_files": "Video files (*.mp4 *.mov *.avi *.mkv *.webm)",
        "preview_failed": "Preview failed",
        "export_dialog": "Export MP4",
        "mp4_video": "MP4 video (*.mp4)",
        "exporting": "Exporting...",
        "exporting_frames": "Exporting {done}/{total} frames",
        "exporting_frames_unknown": "Exporting {done} frames",
        "exported_status": "Exported {frames} frames to {path}",
        "export_complete": "Export complete",
        "saved_to": "Saved to:\n{path}",
        "export_failed": "Export failed",
        "pipeline_title": "Current Pipeline",
        "pipeline_body": "1. Open or drop source video\n2. Preview a styled frame\n3. Tune palette, pixel size, ink, edge thresholds, and FPS\n4. Export MP4 with stable style settings",
        "about_title": "About Cucumber",
        "about_body": "Cucumber is an open-source desktop studio for turning video into rotoscoped pixel-game footage.",
    },
    "zh": {
        "app_caption": "转描像素视频工作室",
        "menu_file": "文件",
        "menu_settings": "设置",
        "menu_pipeline": "管线",
        "menu_view": "视图",
        "menu_help": "帮助",
        "action_open": "打开视频",
        "action_preview": "生成预览",
        "action_export": "导出 MP4",
        "action_open_exports": "打开导出文件夹",
        "action_quit": "退出",
        "action_reset": "重置风格",
        "action_language_zh": "中文界面",
        "action_language_en": "英文界面",
        "action_pipeline_overview": "当前管线",
        "action_toggle_frame_limit": "切换测试帧数限制",
        "action_about": "关于 Cucumber",
        "drop_title": "把视频拖到这里",
        "drop_subtitle": "支持 MP4、MOV、AVI、MKV、WEBM",
        "preview_title": "预览帧",
        "preview_subtitle": "调好风格后就可以导出。",
        "no_video": "还没有选择视频",
        "choose_video": "选择视频",
        "language": "界面语言",
        "palette": "调色盘",
        "pixel_size": "像素块",
        "width": "导出宽度",
        "color_levels": "色阶",
        "ink_strength": "描线强度",
        "line_weight": "线条粗细",
        "edge_low": "边缘低阈值",
        "edge_high": "边缘高阈值",
        "fps": "导出帧率",
        "preview_time": "预览时间",
        "limit_export": "测试导出时限制帧数",
        "frame_limit": "帧数上限",
        "render_preview": "生成预览",
        "export_mp4": "导出 MP4",
        "ready": "就绪",
        "video_loaded": "视频已载入",
        "rendering_preview": "正在生成预览...",
        "preview_ready": "预览已生成",
        "choose_video_dialog": "选择视频",
        "video_files": "视频文件 (*.mp4 *.mov *.avi *.mkv *.webm)",
        "preview_failed": "预览失败",
        "export_dialog": "导出 MP4",
        "mp4_video": "MP4 视频 (*.mp4)",
        "exporting": "正在导出...",
        "exporting_frames": "正在导出 {done}/{total} 帧",
        "exporting_frames_unknown": "正在导出 {done} 帧",
        "exported_status": "已导出 {frames} 帧到 {path}",
        "export_complete": "导出完成",
        "saved_to": "已保存到：\n{path}",
        "export_failed": "导出失败",
        "pipeline_title": "当前管线",
        "pipeline_body": "1. 打开或拖入源视频\n2. 生成一帧风格预览\n3. 调整调色盘、像素块、描线、边缘阈值和帧率\n4. 用稳定风格设置导出 MP4",
        "about_title": "关于 Cucumber",
        "about_body": "Cucumber 是一个开源桌面软件，用来把视频转成转描像素游戏画面。",
    },
}


class ExportWorker(QThread):
    progressed = Signal(int, int)
    completed = Signal(dict)
    failed = Signal(str)

    def __init__(self, source: Path, output: Path, settings: RotoscopeSettings) -> None:
        super().__init__()
        self.source = source
        self.output = output
        self.settings = settings

    def run(self) -> None:
        try:
            result = process_video(self.source, self.output, self.settings, self.progressed.emit)
        except Exception as exc:  # noqa: BLE001
            self.failed.emit(str(exc))
            return
        self.completed.emit(result)


class DropArea(QFrame):
    file_dropped = Signal(Path)

    def __init__(self) -> None:
        super().__init__()
        self.preview_mode = False
        self.setAcceptDrops(True)
        self.setObjectName("dropArea")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(10)

        self.art = QLabel()
        mascot = ASSET_DIR / "cucumber-mascot-cutout.png"
        if mascot.exists():
            self.art.setPixmap(QPixmap(str(mascot)).scaled(340, 340, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.art.setAlignment(Qt.AlignCenter)

        self.title = QLabel()
        self.title.setObjectName("dropTitle")
        self.title.setAlignment(Qt.AlignCenter)

        self.subtitle = QLabel()
        self.subtitle.setObjectName("muted")
        self.subtitle.setAlignment(Qt.AlignCenter)

        layout.addStretch(1)
        layout.addWidget(self.art)
        layout.addWidget(self.title)
        layout.addWidget(self.subtitle)
        layout.addStretch(1)
        self.set_language("en")

    def set_language(self, language: str) -> None:
        text = TEXT[language]
        if self.preview_mode:
            self.title.setText(text["preview_title"])
            self.subtitle.setText(text["preview_subtitle"])
        else:
            self.title.setText(text["drop_title"])
            self.subtitle.setText(text["drop_subtitle"])

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if self._first_video_path(event):
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        path = self._first_video_path(event)
        if path:
            self.file_dropped.emit(path)

    @staticmethod
    def _first_video_path(event: QDragEnterEvent | QDropEvent) -> Path | None:
        urls = event.mimeData().urls()
        for url in urls:
            if not url.isLocalFile():
                continue
            path = Path(url.toLocalFile())
            if path.suffix.lower() in {".mp4", ".mov", ".avi", ".mkv", ".webm"}:
                return path
        return None


class CucumberWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.source_path: Path | None = None
        self.export_worker: ExportWorker | None = None
        self.language = "zh" if QLocale.system().name().startswith("zh") else "en"
        self.setting_labels: dict[str, QLabel] = {}

        self.setWindowTitle("Cucumber")
        icon_path = ASSET_DIR / "cucumber.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        self.setMinimumSize(1080, 700)
        self.menus: dict[str, object] = {}
        self.actions: dict[str, QAction] = {}
        self._create_menus_and_toolbar()

        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(22, 22, 22, 22)
        root_layout.setSpacing(18)

        self.drop_area = DropArea()
        self.drop_area.file_dropped.connect(self.set_source)
        root_layout.addWidget(self.drop_area, 3)

        side = QFrame()
        side.setObjectName("sidePanel")
        side.setMinimumWidth(470)
        side_layout = QVBoxLayout(side)
        side_layout.setContentsMargins(20, 20, 20, 20)
        side_layout.setSpacing(12)
        root_layout.addWidget(side, 2)

        brand = QHBoxLayout()
        brand.setSpacing(12)
        logo = QLabel()
        logo_path = ASSET_DIR / "cucumber-icon-256.png"
        if logo_path.exists():
            logo.setPixmap(QPixmap(str(logo_path)).scaled(54, 54, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        brand_text = QVBoxLayout()
        title = QLabel("Cucumber")
        title.setObjectName("appTitle")
        self.caption = QLabel()
        self.caption.setObjectName("muted")
        brand_text.addWidget(title)
        brand_text.addWidget(self.caption)
        brand.addWidget(logo)
        brand.addLayout(brand_text, 1)
        side_layout.addLayout(brand)

        self.source_label = QLabel()
        self.source_label.setObjectName("sourceLabel")
        self.source_label.setWordWrap(True)
        side_layout.addWidget(self.source_label)

        self.browse_button = QPushButton()
        self.browse_button.clicked.connect(self.choose_video)
        side_layout.addWidget(self.browse_button)

        settings_scroll = QScrollArea()
        settings_scroll.setObjectName("settingsScroll")
        settings_scroll.setWidgetResizable(True)
        settings_scroll.setFrameShape(QFrame.NoFrame)
        settings_host = QWidget()
        settings_host.setObjectName("settingsHost")
        settings_layout = QVBoxLayout(settings_host)
        settings_layout.setContentsMargins(0, 0, 8, 0)
        settings_layout.setSpacing(12)
        settings_grid = QGridLayout()
        settings_grid.setColumnMinimumWidth(0, 136)
        settings_grid.setColumnStretch(0, 0)
        settings_grid.setColumnStretch(1, 1)
        settings_grid.setHorizontalSpacing(18)
        settings_grid.setVerticalSpacing(13)
        settings_layout.addLayout(settings_grid)

        self.language_select = QComboBox()
        self.language_select.addItem("中文", "zh")
        self.language_select.addItem("English", "en")
        self.language_select.setCurrentIndex(0 if self.language == "zh" else 1)
        self.language_select.currentIndexChanged.connect(self.change_language)
        self.setting_labels["language"] = self._add_row(settings_grid, 0, "", self.language_select)

        self.palette = QComboBox()
        self.palette.addItems(palette_names())
        self.palette.setCurrentText("Arcade Ink")
        self.setting_labels["palette"] = self._add_row(settings_grid, 1, "", self.palette)

        self.pixel_size = self._slider(1, 12, 4)
        self.setting_labels["pixel_size"] = self._add_row(settings_grid, 2, "", self.pixel_size)

        self.max_width = self._slider(240, 1280, 640, 40)
        self.setting_labels["width"] = self._add_row(settings_grid, 3, "", self.max_width)

        self.color_levels = self._slider(2, 12, 6)
        self.setting_labels["color_levels"] = self._add_row(settings_grid, 4, "", self.color_levels)

        self.edge_strength = self._slider(0, 100, 85, 5)
        self.setting_labels["ink_strength"] = self._add_row(settings_grid, 5, "", self.edge_strength)

        self.line_thickness = self._slider(1, 5, 1)
        self.setting_labels["line_weight"] = self._add_row(settings_grid, 6, "", self.line_thickness)

        self.edge_low = self._slider(16, 220, 64, 4)
        self.setting_labels["edge_low"] = self._add_row(settings_grid, 7, "", self.edge_low)

        self.edge_high = self._slider(16, 220, 132, 4)
        self.setting_labels["edge_high"] = self._add_row(settings_grid, 8, "", self.edge_high)

        self.fps_limit = self._slider(6, 30, 18)
        self.setting_labels["fps"] = self._add_row(settings_grid, 9, "", self.fps_limit)

        self.preview_second = QSpinBox()
        self.preview_second.setRange(0, 600)
        self.preview_second.setSuffix(" s")
        self.setting_labels["preview_time"] = self._add_row(settings_grid, 10, "", self.preview_second)

        self.limit_frames = QCheckBox()
        self.limit_frames.setChecked(True)
        settings_layout.addWidget(self.limit_frames)

        self.frame_limit = QSpinBox()
        self.frame_limit.setRange(12, 5000)
        self.frame_limit.setSingleStep(12)
        self.frame_limit.setValue(120)
        self.setting_labels["frame_limit"] = self._add_row(settings_grid, 11, "", self.frame_limit)
        settings_layout.addStretch(1)
        settings_scroll.setWidget(settings_host)
        side_layout.addWidget(settings_scroll, 1)

        self.preview_button = QPushButton()
        self.preview_button.clicked.connect(self.render_preview)
        side_layout.addWidget(self.preview_button)

        self.export_button = QPushButton()
        self.export_button.setObjectName("primaryButton")
        self.export_button.clicked.connect(self.export_video)
        side_layout.addWidget(self.export_button)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        side_layout.addWidget(self.progress)

        self.status = QLabel()
        self.status.setObjectName("muted")
        side_layout.addWidget(self.status)
        side_layout.addStretch(1)

        self._set_style()
        self.apply_language()
        self._refresh_controls()

    def _create_menus_and_toolbar(self) -> None:
        menu_bar = self.menuBar()
        self.menus["file"] = menu_bar.addMenu("")
        self.menus["settings"] = menu_bar.addMenu("")
        self.menus["pipeline"] = menu_bar.addMenu("")
        self.menus["view"] = menu_bar.addMenu("")
        self.menus["help"] = menu_bar.addMenu("")

        self.actions["open"] = self._action("Ctrl+O", self.choose_video)
        self.actions["preview"] = self._action("Ctrl+R", self.render_preview)
        self.actions["export"] = self._action("Ctrl+E", self.export_video)
        self.actions["open_exports"] = self._action("", self.open_exports_folder)
        self.actions["quit"] = self._action("Ctrl+Q", self.close)
        self.actions["reset"] = self._action("", self.reset_style)
        self.actions["language_zh"] = self._action("", lambda: self.set_language("zh"))
        self.actions["language_en"] = self._action("", lambda: self.set_language("en"))
        self.actions["pipeline_overview"] = self._action("", self.show_pipeline_overview)
        self.actions["toggle_frame_limit"] = self._action("", self.toggle_frame_limit)
        self.actions["about"] = self._action("", self.show_about)

        self.menus["file"].addAction(self.actions["open"])
        self.menus["file"].addSeparator()
        self.menus["file"].addAction(self.actions["preview"])
        self.menus["file"].addAction(self.actions["export"])
        self.menus["file"].addSeparator()
        self.menus["file"].addAction(self.actions["open_exports"])
        self.menus["file"].addSeparator()
        self.menus["file"].addAction(self.actions["quit"])

        self.menus["settings"].addAction(self.actions["reset"])
        self.menus["settings"].addSeparator()
        self.menus["settings"].addAction(self.actions["language_zh"])
        self.menus["settings"].addAction(self.actions["language_en"])

        self.menus["pipeline"].addAction(self.actions["pipeline_overview"])
        self.menus["pipeline"].addAction(self.actions["toggle_frame_limit"])
        self.menus["view"].addAction(self.actions["open_exports"])
        self.menus["help"].addAction(self.actions["about"])

        toolbar = QToolBar("Main")
        toolbar.setObjectName("mainToolbar")
        toolbar.setIconSize(QSize(18, 18))
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextOnly)
        toolbar.addAction(self.actions["open"])
        toolbar.addAction(self.actions["preview"])
        toolbar.addAction(self.actions["export"])
        toolbar.addSeparator()
        toolbar.addAction(self.actions["pipeline_overview"])
        toolbar.addAction(self.actions["reset"])
        self.addToolBar(Qt.TopToolBarArea, toolbar)

    def _action(self, shortcut: str, handler) -> QAction:
        action = QAction(self)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(handler)
        return action

    def change_language(self, _index: int | None = None) -> None:
        language = self.language_select.currentData()
        if language in TEXT:
            self.language = language
            self.apply_language()

    def set_language(self, language: str) -> None:
        if language not in TEXT:
            return
        self.language = language
        index = self.language_select.findData(language)
        if index >= 0 and self.language_select.currentIndex() != index:
            self.language_select.blockSignals(True)
            self.language_select.setCurrentIndex(index)
            self.language_select.blockSignals(False)
        self.apply_language()

    def open_exports_folder(self) -> None:
        EXPORT_DIR.mkdir(exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(EXPORT_DIR)))

    def reset_style(self) -> None:
        self.palette.setCurrentText("Arcade Ink")
        self.pixel_size.setValue(4)
        self.max_width.setValue(640)
        self.color_levels.setValue(6)
        self.edge_strength.setValue(85)
        self.line_thickness.setValue(1)
        self.edge_low.setValue(64)
        self.edge_high.setValue(132)
        self.fps_limit.setValue(18)
        self.preview_second.setValue(0)
        self.limit_frames.setChecked(True)
        self.frame_limit.setValue(120)
        self.status.setText(self.tr("ready") if self.source_path is None else self.tr("video_loaded"))

    def show_pipeline_overview(self) -> None:
        QMessageBox.information(self, self.tr("pipeline_title"), self.tr("pipeline_body"))

    def toggle_frame_limit(self) -> None:
        self.limit_frames.setChecked(not self.limit_frames.isChecked())

    def show_about(self) -> None:
        QMessageBox.information(self, self.tr("about_title"), self.tr("about_body"))

    def tr(self, key: str) -> str:
        return TEXT[self.language][key]

    def apply_language(self) -> None:
        for key, menu in self.menus.items():
            menu.setTitle(self.tr(f"menu_{key}"))
        for key, action in self.actions.items():
            action_key = f"action_{key}"
            if action_key in TEXT[self.language]:
                action.setText(self.tr(action_key))
        self.caption.setText(self.tr("app_caption"))
        self.drop_area.set_language(self.language)
        if self.source_path is None:
            self.source_label.setText(self.tr("no_video"))
            self.status.setText(self.tr("ready"))
        elif self.status.text() in {TEXT["en"]["ready"], TEXT["zh"]["ready"], TEXT["en"]["video_loaded"], TEXT["zh"]["video_loaded"]}:
            self.status.setText(self.tr("video_loaded"))
        self.browse_button.setText(self.tr("choose_video"))
        self.limit_frames.setText(self.tr("limit_export"))
        self.preview_button.setText(self.tr("render_preview"))
        self.export_button.setText(self.tr("export_mp4"))
        for key, label in self.setting_labels.items():
            label.setText(self.tr(key))

    def choose_video(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("choose_video_dialog"),
            str(Path.home()),
            self.tr("video_files"),
        )
        if filename:
            self.set_source(Path(filename))

    def set_source(self, path: Path) -> None:
        self.source_path = path
        self.source_label.setText(str(path))
        self.drop_area.preview_mode = False
        self.drop_area.set_language(self.language)
        self.status.setText(self.tr("video_loaded"))
        self.progress.setValue(0)
        self._refresh_controls()

    def render_preview(self) -> None:
        if not self.source_path:
            return
        self.status.setText(self.tr("rendering_preview"))
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            frame = sample_frame(self.source_path, float(self.preview_second.value()), self.settings())
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, self.tr("preview_failed"), str(exc))
            return
        finally:
            QApplication.restoreOverrideCursor()
        self.drop_area.art.setPixmap(self._array_to_pixmap(frame).scaled(700, 430, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.drop_area.preview_mode = True
        self.drop_area.set_language(self.language)
        self.status.setText(self.tr("preview_ready"))

    def export_video(self) -> None:
        if not self.source_path:
            return
        default_name = f"{self.source_path.stem}-cucumber.mp4"
        output, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("export_dialog"),
            str(EXPORT_DIR / default_name),
            self.tr("mp4_video"),
        )
        if not output:
            return

        self.export_button.setEnabled(False)
        self.preview_button.setEnabled(False)
        self.progress.setValue(0)
        self.status.setText(self.tr("exporting"))
        self.export_worker = ExportWorker(self.source_path, Path(output), self.settings())
        self.export_worker.progressed.connect(self.on_progress)
        self.export_worker.completed.connect(self.on_completed)
        self.export_worker.failed.connect(self.on_failed)
        self.export_worker.start()

    def on_progress(self, done: int, total: int) -> None:
        if total:
            self.progress.setValue(min(100, round(done / total * 100)))
            self.status.setText(self.tr("exporting_frames").format(done=done, total=total))
        else:
            self.status.setText(self.tr("exporting_frames_unknown").format(done=done))

    def on_completed(self, result: dict) -> None:
        self.progress.setValue(100)
        self.status.setText(self.tr("exported_status").format(frames=result["frames"], path=result["path"]))
        self._refresh_controls()
        QMessageBox.information(
            self,
            self.tr("export_complete"),
            self.tr("saved_to").format(path=result["path"]),
        )

    def on_failed(self, message: str) -> None:
        self.status.setText(self.tr("export_failed"))
        self._refresh_controls()
        QMessageBox.critical(self, self.tr("export_failed"), message)

    def settings(self) -> RotoscopeSettings:
        low = min(self.edge_low.value(), self.edge_high.value() - 1)
        high = max(self.edge_high.value(), low + 1)
        return RotoscopeSettings(
            palette=self.palette.currentText(),
            max_width=self.max_width.value(),
            pixel_size=self.pixel_size.value(),
            color_levels=self.color_levels.value(),
            edge_low=low,
            edge_high=high,
            edge_strength=self.edge_strength.value() / 100,
            line_thickness=self.line_thickness.value(),
            fps_limit=self.fps_limit.value(),
            frame_limit=self.frame_limit.value() if self.limit_frames.isChecked() else None,
        )

    def _refresh_controls(self) -> None:
        enabled = self.source_path is not None and not (self.export_worker and self.export_worker.isRunning())
        self.preview_button.setEnabled(enabled)
        self.export_button.setEnabled(enabled)
        if self.actions:
            self.actions["preview"].setEnabled(enabled)
            self.actions["export"].setEnabled(enabled)

    @staticmethod
    def _array_to_pixmap(frame) -> QPixmap:
        height, width, channels = frame.shape
        image = QImage(frame.data, width, height, channels * width, QImage.Format_RGB888)
        return QPixmap.fromImage(image.copy())

    @staticmethod
    def _slider(minimum: int, maximum: int, value: int, step: int = 1) -> QSlider:
        slider = QSlider(Qt.Horizontal)
        slider.setRange(minimum, maximum)
        slider.setValue(value)
        slider.setSingleStep(step)
        slider.setPageStep(step)
        return slider

    @staticmethod
    def _add_row(grid: QGridLayout, row: int, label: str, widget: QWidget) -> QLabel:
        text = QLabel(label)
        text.setObjectName("settingLabel")
        text.setMinimumWidth(132)
        text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        widget.setMinimumHeight(32)
        if isinstance(widget, QComboBox):
            widget.setMinimumWidth(260)
        grid.addWidget(text, row, 0)
        grid.addWidget(widget, row, 1)
        return text

    def _set_style(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow, QWidget {
                background: #101411;
                color: #edf7df;
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: 14px;
            }
            #dropArea {
                background: #151c17;
                border: 1px solid #2e3c32;
                border-radius: 8px;
            }
            QMenuBar {
                background: #111811;
                color: #e7f7d8;
                border-bottom: 1px solid #29382f;
                padding: 3px 8px;
            }
            QMenuBar::item {
                background: transparent;
                padding: 7px 12px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background: #263627;
                color: #d7ff72;
            }
            QMenu {
                background: #151f17;
                color: #eef8e4;
                border: 1px solid #344539;
                padding: 6px;
            }
            QMenu::item {
                padding: 8px 28px 8px 16px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background: #2f432f;
                color: #d7ff72;
            }
            #mainToolbar {
                background: #111811;
                border-bottom: 1px solid #26362d;
                spacing: 8px;
                padding: 6px 10px;
            }
            #mainToolbar QToolButton {
                background: #1c281e;
                border: 1px solid #344739;
                border-radius: 5px;
                color: #eff9e7;
                padding: 7px 10px;
                font-weight: 600;
            }
            #mainToolbar QToolButton:hover {
                background: #2d3f2f;
                border-color: #79a847;
            }
            #sidePanel {
                background: #172019;
                border: 1px solid #304036;
                border-radius: 8px;
            }
            #settingsScroll, #settingsHost {
                background: transparent;
                border: none;
            }
            #appTitle {
                font-size: 28px;
                font-weight: 700;
                color: #d7ff72;
            }
            #dropTitle {
                font-size: 24px;
                font-weight: 650;
                color: #f0ffcf;
            }
            #muted {
                color: #a9b8a1;
            }
            #sourceLabel {
                background: #101611;
                border: 1px solid #2b382f;
                border-radius: 6px;
                padding: 10px;
                color: #d8e8d0;
            }
            #settingLabel {
                color: #b6c9ae;
                background: transparent;
                font-size: 14px;
            }
            QPushButton {
                background: #243226;
                border: 1px solid #405541;
                border-radius: 6px;
                padding: 10px 12px;
                color: #f4ffe7;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #2d3f2f;
                border-color: #79a847;
            }
            QPushButton:disabled {
                color: #6f7b6d;
                border-color: #263128;
                background: #182019;
            }
            #primaryButton {
                background: #97d63d;
                border-color: #baf064;
                color: #10210c;
            }
            #primaryButton:hover {
                background: #afe94f;
            }
            QComboBox, QSpinBox {
                background: #101611;
                border: 1px solid #344539;
                border-radius: 5px;
                padding: 6px 10px;
                color: #ecf8df;
                min-height: 30px;
            }
            QComboBox QAbstractItemView {
                background: #101611;
                border: 1px solid #344539;
                color: #ecf8df;
                selection-background-color: #2d3f2f;
            }
            QProgressBar {
                background: #101611;
                border: 1px solid #344539;
                border-radius: 5px;
                height: 12px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: #9de047;
                border-radius: 4px;
            }
            QSlider::groove:horizontal {
                background: #2b382f;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #d7ff72;
                border: 1px solid #efffc1;
                width: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            """
        )


def main() -> int:
    app = QApplication(sys.argv)
    window = CucumberWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
