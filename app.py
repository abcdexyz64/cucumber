from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile

import imageio.v3 as iio
import streamlit as st

from rotopixel.palettes import palette_names
from rotopixel.processor import RotoscopeSettings, process_video, sample_frame


APP_ROOT = Path(__file__).parent
EXPORT_DIR = APP_ROOT / "exports"
TMP_DIR = APP_ROOT / "tmp"
EXPORT_DIR.mkdir(exist_ok=True)
TMP_DIR.mkdir(exist_ok=True)


st.set_page_config(page_title="RotoPixel Studio", page_icon="RP", layout="wide")

st.markdown(
    """
    <style>
    .block-container { padding-top: 1.5rem; max-width: 1180px; }
    .stSlider [data-baseweb="slider"] { padding-top: 0.25rem; }
    video { border-radius: 6px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("RotoPixel Studio")
st.caption("把视频统一成稳定的转描像素游戏画面。")

uploaded = st.file_uploader("视频", type=["mp4", "mov", "avi", "mkv", "webm"])

left, right = st.columns([0.34, 0.66], gap="large")

with left:
    st.subheader("风格")
    palette = st.selectbox("调色盘", palette_names(), index=1)
    pixel_size = st.slider("像素块", 1, 12, 4)
    max_width = st.slider("导出宽度", 240, 1280, 640, step=40)
    color_levels = st.slider("色阶", 2, 12, 6)
    edge_strength = st.slider("描线强度", 0.0, 1.0, 0.85, step=0.05)
    line_thickness = st.slider("线条粗细", 1, 5, 1)
    edge_low, edge_high = st.slider("边缘阈值", 16, 220, (64, 132), step=4)
    fps_limit = st.slider("导出帧率", 6, 30, 18)
    preview_second = st.slider("预览时间", 0.0, 20.0, 0.0, step=0.25)
    frame_limit_enabled = st.checkbox("测试导出限制帧数", value=True)
    frame_limit = st.number_input("帧数上限", 12, 600, 120, step=12, disabled=not frame_limit_enabled)

settings = RotoscopeSettings(
    palette=palette,
    max_width=max_width,
    pixel_size=pixel_size,
    color_levels=color_levels,
    edge_low=edge_low,
    edge_high=edge_high,
    edge_strength=edge_strength,
    line_thickness=line_thickness,
    fps_limit=fps_limit,
    frame_limit=int(frame_limit) if frame_limit_enabled else None,
)


def save_upload() -> Path | None:
    if uploaded is None:
        return None
    suffix = Path(uploaded.name).suffix or ".mp4"
    target = TMP_DIR / f"source{suffix}"
    target.write_bytes(uploaded.getbuffer())
    return target


input_path = save_upload()

with right:
    if input_path is None:
        st.info("上传视频后可预览单帧并导出成片。")
    else:
        metadata = iio.immeta(input_path)
        duration = metadata.get("duration")
        fps = metadata.get("fps")
        st.video(str(input_path))
        details = []
        if duration:
            details.append(f"{duration:.2f}s")
        if fps:
            details.append(f"{fps:.2f} fps")
        if details:
            st.caption("源视频：" + " / ".join(details))

        preview_col, export_col = st.columns(2, gap="large")
        with preview_col:
            if st.button("生成预览帧", use_container_width=True):
                with st.spinner("正在转描"):
                    frame = sample_frame(input_path, preview_second, settings)
                st.image(frame, caption="预览", use_container_width=True)

        with export_col:
            if st.button("导出视频", type="primary", use_container_width=True):
                output_path = EXPORT_DIR / f"{Path(uploaded.name).stem}-rotopixel.mp4"
                bar = st.progress(0)
                status = st.empty()

                def on_progress(done: int, total: int) -> None:
                    if total:
                        bar.progress(min(1.0, done / total))
                        status.text(f"已处理 {done}/{total} 帧")
                    else:
                        status.text(f"已处理 {done} 帧")

                with st.spinner("正在导出"):
                    result = process_video(input_path, output_path, settings, progress=on_progress)

                bar.progress(1.0)
                st.success(f"已导出 {result['frames']} 帧，{result['output_fps']:.2f} fps")
                st.video(str(output_path))
                st.download_button(
                    "下载 MP4",
                    data=output_path.read_bytes(),
                    file_name=output_path.name,
                    mime="video/mp4",
                    use_container_width=True,
                )
