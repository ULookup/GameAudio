# 环境声扩充资产

本次扩充保持“地下设施混凝土通风走廊”的声音方向：原 60 秒空气基底继续作为主体，新增较弱的真实深通风层与空间共鸣层，并以低频率加入结构异响和机器工作片段。

原六个导出资产、原剪辑脚本及 `AudioAssets.json` 均保留。本文件说明新增的六个资产；精确参数另存于 `AudioExpansion.json`。

## 导出结果

新增资产均位于 `Audio/Exports/`，格式统一为 **48 kHz／24 bit PCM／双声道 WAV**。

| 资产 | 时长 | 峰值 dBFS | RMS dBFS | 作用 |
| --- | ---: | ---: | ---: | --- |
| `AMB_Deep_Ventilation_Loop_64s.wav` | 64.00 s | -18.84 | -34.00 | 真实深沉通风底层 |
| `AMB_Subtle_Space_Resonance_Loop_54s.wav` | 54.00 s | -23.78 | -37.00 | 微弱空间低鸣与共鸣 |
| `SFX_Structure_Groan_01.wav` | 1.15 s | -14.00 | -29.40 | 短促结构共鸣 |
| `SFX_Structure_Groan_02.wav` | 7.00 s | -15.00 | -27.65 | 较长金属结构呻吟 |
| `SFX_Machine_Cycle_01.wav` | 8.00 s | -14.00 | -28.29 | 一段远处机器工作过程 |
| `SFX_Machine_Cycle_02.wav` | 8.00 s | -14.00 | -27.84 | 另一段机器工作过程 |

这里的 RMS 是整条音频的均方根电平，不是 LUFS。短声的实际听感还取决于 Wwise 中的声部音量、距离衰减与触发间隔。

## 持续层

**深通风层**使用 kyles 的地下室通风原录音，选取 1.00–68.00 秒。经 40 Hz 高通、1.4 kHz 低通处理，尾首做 3 秒等功率交叉淡化，得到 64 秒循环。最终为 -34 dBFS RMS，比原空气主基底低 8 dB。

**空间共鸣层**以 Nox 的 bunker 素材为主，选取 0.50–57.50 秒，使用 80 Hz 高通及 600 Hz 低通，减轻极低频堆积。Vospi 的 spacecraft 素材选取 1.00–20.50 秒，使用 40 Hz 高通及 250 Hz 低通，3 秒尾首交叉淡化后形成 16.5 秒内部循环。

Vospi 原素材是带音调性的合成 Drone，因此只作为极弱的附加共鸣。最终混合前，Nox 层为 -37 dBFS RMS，Vospi 层为 -47 dBFS RMS，相差 10 dB。两者混合后再次进行 3 秒尾首交叉淡化，得到 54 秒循环，最终整体为 -37 dBFS RMS。

新增循环的 64 秒与 54 秒长度不同于主基底的 60 秒，减少各层同时重复同一变化的情况。两个新增层都保留完整接缝，未以静音淡出代替循环衔接。

## 结构异响与机器片段

结构异响来自同一份原录音中的两个不重叠片段：

- `Groan_01`：0.30–1.45 秒，保留真实短声，不人为拉长；100 Hz 高通、2.5 kHz 低通，柔化高瞬态，120 ms 淡入、350 ms 淡出。
- `Groan_02`：1.65–8.65 秒，保留中段共鸣及自然衰减；100 Hz 高通、2.2 kHz 低通，450 ms 淡入、800 ms 淡出。

机器素材本身含周期性排风机声音，选取 5.00–13.00 秒和 30.00–38.00 秒两个不同片段。分别使用 100 Hz 高通、1.4／1.2 kHz 低通，头尾各约 1.1–1.2 秒淡化。两条都作为有起落的单次事件，供 Wwise 稀疏触发，不加入永久循环的主空气层。

## 原素材与选段

| 原始文件 | 选段（秒） | 导出用途 |
| --- | --- | --- |
| `451924__kyles__room-tone-large-room-church-basement-heavy-deep-ventilation-or-furnace-hum.flac` | 1.00–68.00 | 深通风循环 |
| `817225__nox_sound__atmosphere_scifi_bunker_loop_stereo.wav` | 0.50–57.50 | 空间共鸣主体 |
| `343738__vospi__empty-corridor-of-a-spacecraft.wav` | 1.00–20.50 | 极弱音调层 |
| `496836__hinchinbrook__metallic-groan.wav` | 0.30–1.45；1.65–8.65 | 两条结构异响 |
| `260815__iccleste__industrial-machine-cycle.wav` | 5.00–13.00；30.00–38.00 | 两条机器片段 |

## 重复导出

`Tools/enrich_audio.py` 使用 NumPy、SciPy、SoundFile，并复用 `Tools/process_audio.py` 的音频处理函数。原始素材不会被改写。

```powershell
python Tools/enrich_audio.py --sources "D:\FreesoundSources"
```

该命令只更新以上六个新增 WAV 和 `Docs/AudioExpansion.json`。44.1 kHz 原素材使用多相重采样转换至 48 kHz，全部文件在导出时执行 24 bit TPDF 抖动。导出规格、时长和电平已读取确认；本轮实际 Wwise 混音录音见 [Corridor_Expanded_Preview.wav](../Preview/Corridor_Expanded_Preview.wav)。
