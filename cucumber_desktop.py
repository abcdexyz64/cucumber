from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QIcon, QImage, QPixmap
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
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from rotopixel.palettes import palette_names
from rotopixel.processor import RotoscopeSettings, process_video, sample_frame


APP_ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
ASSET_DIR = APP_ROOT / "assets"
EXPORT_DIR = Path.cwd() / "exports"
EXPORT_DIR.mkdir(exist_ok=True)


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
        self.setAcceptDrops(True)
        self.setObjectName("dropArea")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(10)

        self.art = QLabel()
        mascot = ASSET_DIR / "cucumber-mascot-360.png"
        if mascot.exists():
            self.art.setPixmap(QPixmap(str(mascot)).scaled(220, 220, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.art.setAlignment(Qt.AlignCenter)

        self.title = QLabel("Drop a video here")
        self.title.setObjectName("dropTitle")
        self.title.setAlignment(Qt.AlignCenter)

        self.subtitle = QLabel("MP4, MOV, AVI, MKV, or WEBM")
        self.subtitle.setObjectName("muted")
        self.subtitle.setAlignment(Qt.AlignCenter)

        layout.addStretch(1)
        layout.addWidget(self.art)
        layout.addWidget(self.title)
        layout.addWidget(self.subtitle)
        layout.addStretch(1)

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

        self.setWindowTitle("Cucumber")
        icon_path = ASSET_DIR / "cucumber.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        self.setMinimumSize(1080, 700)

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
        side_layout = QVBoxLayout(side)
        side_layout.setContentsMargins(20, 20, 20, 20)
        side_layout.setSpacing(14)
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
        caption = QLabel("Rotoscoped pixel-video studio")
        caption.setObjectName("muted")
        brand_text.addWidget(title)
        brand_text.addWidget(caption)
        brand.addWidget(logo)
        brand.addLayout(brand_text, 1)
        side_layout.addLayout(brand)

        self.source_label = QLabel("No video selected")
        self.source_label.setObjectName("sourceLabel")
        self.source_label.setWordWrap(True)
        side_layout.addWidget(self.source_label)

        browse = QPushButton("Choose video")
        browse.clicked.connect(self.choose_video)
        side_layout.addWidget(browse)

        settings_grid = QGridLayout()
        settings_grid.setHorizontalSpacing(14)
        settings_grid.setVerticalSpacing(10)
        side_layout.addLayout(settings_grid)

        self.palette = QComboBox()
        self.palette.addItems(palette_names())
        self.palette.setCurrentText("Arcade Ink")
        self._add_row(settings_grid, 0, "Palette", self.palette)

        self.pixel_size = self._slider(1, 12, 4)
        self._add_row(settings_grid, 1, "Pixel size", self.pixel_size)

        self.max_width = self._slider(240, 1280, 640, 40)
        self._add_row(settings_grid, 2, "Width", self.max_width)

        self.color_levels = self._slider(2, 12, 6)
        self._add_row(settings_grid, 3, "Color levels", self.color_levels)

        self.edge_strength = self._slider(0, 100, 85, 5)
        self._add_row(settings_grid, 4, "Ink strength", self.edge_strength)

        self.line_thickness = self._slider(1, 5, 1)
        self._add_row(settings_grid, 5, "Line weight", self.line_thickness)

        self.edge_low = self._slider(16, 220, 64, 4)
        self._add_row(settings_grid, 6, "Edge low", self.edge_low)

        self.edge_high = self._slider(16, 220, 132, 4)
        self._add_row(settings_grid, 7, "Edge high", self.edge_high)

        self.fps_limit = self._slider(6, 30, 18)
        self._add_row(settings_grid, 8, "FPS", self.fps_limit)

        self.preview_second = QSpinBox()
        self.preview_second.setRange(0, 600)
        self.preview_second.setSuffix(" s")
        self._add_row(settings_grid, 9, "Preview time", self.preview_second)

        self.limit_frames = QCheckBox("Limit export while testing")
        self.limit_frames.setChecked(True)
        side_layout.addWidget(self.limit_frames)

        self.frame_limit = QSpinBox()
        self.frame_limit.setRange(12, 5000)
        self.frame_limit.setSingleStep(12)
        self.frame_limit.setValue(120)
        self._add_row(settings_grid, 10, "Frame limit", self.frame_limit)

        self.preview_button = QPushButton("Render preview")
        self.preview_button.clicked.connect(self.render_preview)
        side_layout.addWidget(self.preview_button)

        self.export_button = QPushButton("Export MP4")
        self.export_button.setObjectName("primaryButton")
        self.export_button.clicked.connect(self.export_video)
        side_layout.addWidget(self.export_button)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        side_layout.addWidget(self.progress)

        self.status = QLabel("Ready")
        self.status.setObjectName("muted")
        side_layout.addWidget(self.status)
        side_layout.addStretch(1)

        self._set_style()
        self._refresh_controls()

    def choose_video(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Choose a video",
            str(Path.home()),
            "Video files (*.mp4 *.mov *.avi *.mkv *.webm)",
        )
        if filename:
            self.set_source(Path(filename))

    def set_source(self, path: Path) -> None:
        self.source_path = path
        self.source_label.setText(str(path))
        self.status.setText("Video loaded")
        self.progress.setValue(0)
        self._refresh_controls()

    def render_preview(self) -> None:
        if not self.source_path:
            return
        self.status.setText("Rendering preview...")
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            frame = sample_frame(self.source_path, float(self.preview_second.value()), self.settings())
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Preview failed", str(exc))
            return
        finally:
            QApplication.restoreOverrideCursor()
        self.drop_area.art.setPixmap(self._array_to_pixmap(frame).scaled(700, 430, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.drop_area.title.setText("Preview frame")
        self.drop_area.subtitle.setText("Tune the style, then export.")
        self.status.setText("Preview ready")

    def export_video(self) -> None:
        if not self.source_path:
            return
        default_name = f"{self.source_path.stem}-cucumber.mp4"
        output, _ = QFileDialog.getSaveFileName(
            self,
            "Export MP4",
            str(EXPORT_DIR / default_name),
            "MP4 video (*.mp4)",
        )
        if not output:
            return

        self.export_button.setEnabled(False)
        self.preview_button.setEnabled(False)
        self.progress.setValue(0)
        self.status.setText("Exporting...")
        self.export_worker = ExportWorker(self.source_path, Path(output), self.settings())
        self.export_worker.progressed.connect(self.on_progress)
        self.export_worker.completed.connect(self.on_completed)
        self.export_worker.failed.connect(self.on_failed)
        self.export_worker.start()

    def on_progress(self, done: int, total: int) -> None:
        if total:
            self.progress.setValue(min(100, round(done / total * 100)))
            self.status.setText(f"Exporting {done}/{total} frames")
        else:
            self.status.setText(f"Exporting {done} frames")

    def on_completed(self, result: dict) -> None:
        self.progress.setValue(100)
        self.status.setText(f"Exported {result['frames']} frames to {result['path']}")
        self._refresh_controls()
        QMessageBox.information(self, "Export complete", f"Saved to:\n{result['path']}")

    def on_failed(self, message: str) -> None:
        self.status.setText("Export failed")
        self._refresh_controls()
        QMessageBox.critical(self, "Export failed", message)

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
    def _add_row(grid: QGridLayout, row: int, label: str, widget: QWidget) -> None:
        text = QLabel(label)
        text.setObjectName("settingLabel")
        grid.addWidget(text, row, 0)
        grid.addWidget(widget, row, 1)

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
            #sidePanel {
                background: #172019;
                border: 1px solid #304036;
                border-radius: 8px;
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
                padding: 7px;
                color: #ecf8df;
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
