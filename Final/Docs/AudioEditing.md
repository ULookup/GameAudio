# 音频剪辑与导出

设计对象为地下设施的混凝土通风走廊。持续空气声构成主体，低电平通风机提供远处设备的运转感，短促管道共鸣与金属吱声作为间断细节。距离衰减和随机播放由 Wwise 配置。

所有交付资产均导出为 **48 kHz、24 bit PCM、双声道 WAV**，位于 `Audio/Exports/`。原始下载素材未改写。

## 资产与选段

时间均为原始素材中的秒数，起点包含、终点不包含。

| 导出资产 | 原素材与选段 | 时长 | 峰值 dBFS | RMS dBFS |
| --- | --- | ---: | ---: | ---: |
| `AMB_Underground_Corridor_Loop_60s.wav` | hallway 16.00–80.00；machinery 1.00–24.00 | 60.00 s | -13.47 | -26.00 |
| `SFX_Pipe_Resonance_01.wav` | metalpipe 3.55–6.50 | 2.95 s | -16.00 | -32.31 |
| `SFX_Pipe_Resonance_02.wav` | metalpipe 15.78–18.65 | 2.87 s | -17.00 | -31.85 |
| `SFX_Pipe_Resonance_03.wav` | metalpipe 26.36–29.90 | 3.54 s | -15.00 | -32.68 |
| `SFX_Metal_Creak_01.wav` | creaking-metal-desk 5.35–7.25 | 1.90 s | -18.00 | -32.57 |
| `SFX_Metal_Creak_02.wav` | creaking-metal-desk 46.80–50.35 | 3.55 s | -18.00 | -31.55 |

RMS 为整条文件的数字均方根电平，不是 LUFS。五条随机声使用五个不同选段。

## 基底处理

- 走廊原录音保留双声道，重采样到 48 kHz，使用 35 Hz 高通和 6.5 kHz 低通；混合前调整为 -26 dBFS RMS。
- 通风机原录音为单声道，复制到左右声道，使用 70 Hz 高通和 1.7 kHz 低通，调整为 -39 dBFS RMS，作为较弱的机械层。
- 通风机 23 秒选段使用 2 秒等功率交叉淡化，形成 21 秒内部循环，再重复铺满主基底。
- 合成的 64 秒素材使用 4 秒尾首交叉淡化，导出 60 秒可循环基底。接缝不使用淡出到静音的方式。
- 最终基底调整为 -26 dBFS RMS，为叠加随机声保留电平余量。

## 随机声处理

三条管道素材使用 100 Hz 高通及 3.8–4.2 kHz 低通，压柔过高的瞬态峰值，保留共鸣尾部。起音淡入 50–70 ms，尾音淡出 450–650 ms。

两条金属吱声使用 160 Hz 高通及 4.0–4.2 kHz 低通，起音淡入 120–150 ms，尾音淡出 220–350 ms。较短的一条用于轻微构件异响，较长的一条提供持续的金属摩擦细节。

导出前统一完成 24 bit TPDF 抖动。滤波、淡化和电平处理参数及精确选段记录于 `AudioAssets.json`。

## 原始素材对应

| 简称 | 原始文件 |
| --- | --- |
| hallway | `474458__ecfike__concrete-hallway-with-air-conditioner.wav` |
| machinery | `569432__sheyvan__machinery-ventilation-running-1-1.wav` |
| metalpipe | `824117__derjuli__metalpipe.wav` |
| creaking-metal-desk | `172158__eaglestealthteam__creaking-metal-desk.wav` |

## 重复导出

剪辑使用 Python 音频处理工具完成，脚本为 `Tools/process_audio.py`，依赖 NumPy、SciPy、SoundFile。默认从用户的 Downloads 目录读取四份原始素材；可用 `--sources` 指定其他目录。

```powershell
python Tools/process_audio.py --sources "D:\FreesoundSources"
```

执行会重新导出上述六个 WAV，并更新 `Docs/AudioAssets.json`。导出信息已确认采样率、位深、声道和时长；选段依据波形能量与衰减包络。包含这些资产的完整环境已在 Wwise Soundcaster 中播放并录音，可通过 [最终试听](../Preview/Corridor_Expanded_Preview.wav) 收听。其余六条资产的处理说明见 [AudioExpansion.md](AudioExpansion.md)。
