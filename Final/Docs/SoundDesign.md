# 声音设计与参数

持续空气声构成走廊主体，深层通风与微弱共鸣补充低频和空间感；管道、构件及机械声音以较疏的间隔出现。所有导出资产均为 **48 kHz／24 bit PCM／双声道 WAV**。

## 音频资产

资产位于 `Audio/Exports/`，下表选段时间均以原素材起点为零、单位为秒。作者与下载链接见 [素材来源](Sources.md)。

| 文件名（省略 .wav） | 时长 | 原素材选段 |
| --- | ---: | --- |
| `AMB_Underground_Corridor_Loop_60s` | 60.00 s | ecfike 16.00–80.00；Sheyvan 1.00–24.00 |
| `AMB_Deep_Ventilation_Loop_64s` | 64.00 s | kyles 1.00–68.00 |
| `AMB_Subtle_Space_Resonance_Loop_54s` | 54.00 s | Nox_Sound 0.50–57.50；Vospi 1.00–20.50 |
| `SFX_Pipe_Resonance_01` | 2.95 s | derjuli 3.55–6.50 |
| `SFX_Pipe_Resonance_02` | 2.87 s | derjuli 15.78–18.65 |
| `SFX_Pipe_Resonance_03` | 3.54 s | derjuli 26.36–29.90 |
| `SFX_Metal_Creak_01` | 1.90 s | EagleStealthTeam 5.35–7.25 |
| `SFX_Metal_Creak_02` | 3.55 s | EagleStealthTeam 46.80–50.35 |
| `SFX_Structure_Groan_01` | 1.15 s | hinchinbrook 0.30–1.45 |
| `SFX_Structure_Groan_02` | 7.00 s | hinchinbrook 1.65–8.65 |
| `SFX_Machine_Cycle_01` | 8.00 s | iccleste 5.00–13.00 |
| `SFX_Machine_Cycle_02` | 8.00 s | iccleste 30.00–38.00 |

## 剪辑与混合

**主基底**保留走廊录音的双声道，使用 35 Hz 高通和 6.5 kHz 低通。通风机层使用 70 Hz 高通及 1.7 kHz 低通，以较低电平混合；其单声道素材复制至左右声道。混合素材使用 4 秒尾首交叉淡化，形成 60 秒循环，整体电平为 −26 dBFS RMS。

**深层通风**使用 40 Hz 高通和 1.4 kHz 低通，做 3 秒尾首交叉淡化，形成 64 秒循环，电平为 −34 dBFS RMS。

**空间共鸣**以 Nox_Sound 的地堡氛围为主体，使用 80 Hz 高通及 600 Hz 低通；Vospi 的持续音使用 40 Hz 高通及 250 Hz 低通，以低于主体 10 dB 的电平混入。混合后做 3 秒尾首交叉淡化，形成 54 秒循环，整体为 −37 dBFS RMS。RMS 为均方根电平，不是 LUFS。

三条循环均保持接缝连续，不以静音淡出代替循环衔接。

**管道共鸣**使用 100 Hz 高通及 3.8–4.2 kHz 低通，柔化瞬态并保留共鸣尾部；起音淡入 50–70 ms，尾音淡出 450–650 ms。**金属吱声**使用 160 Hz 高通及 4.0–4.2 kHz 低通，起音淡入 120–150 ms，尾音淡出 220–350 ms。

**结构异响**使用 100 Hz 高通及 2.2–2.5 kHz 低通：短片段淡入 120 ms、淡出 350 ms，长片段淡入 450 ms、淡出 800 ms。**机器片段**使用 100 Hz 高通及 1.2–1.4 kHz 低通，头尾各约 1.1–1.2 秒淡化，作为有起落的单次声音使用。

44.1 kHz 素材重采样到 48 kHz，导出时统一采用 24 bit TPDF 抖动。

## Wwise 播放结构

`AMB_Underground_Corridor` 同时播放三个无限循环的持续层，以及两个独立的 Random Container。主基底单独位于根容器下，另两个持续层位于 `AMB_Atmosphere_Layers`。

| 参数 | `RND_Pipe_And_Metal` | `RND_Distant_Mechanism` |
| --- | --- | --- |
| 内容 | 3 条管道共鸣、2 条金属吱声 | 2 条结构异响、2 条机器片段 |
| 模式 | Shuffle、Continuous、Infinite | Shuffle、Continuous、Infinite |
| 避免重复 | 最近 2 条 | 最近 1 条 |
| 首次播放等待 | 3–7 秒 | 8–14 秒 |
| 每条结束后等待 | 7–17 秒 | 18–34 秒 |
| 子声音高变化 | ±70 cents | ±35 cents |
| 子声音量变化 | ±2 dB | ±1.5 dB |

机械随机组的容器音量为 +4 dB，用于补偿距离衰减后的电平。两组独立运行，可能偶尔叠加。

## 距离与方位

九条短声使用 Listener with Automation，相对听者保持固定位置，并应用 `ATT_Corridor_Metal_40m` 衰减。

| 距离 | 音量衰减 | 低通参数 |
| ---: | ---: | ---: |
| 0 m | 0 dB | 0 |
| 5 m | −3 dB | 5 |
| 10 m | −8 dB | 15 |
| 20 m | −18 dB | 35 |
| 40 m | −48 dB | 65 |

低通参数采用 Wwise 的 LPF 数值，不是截止频率 Hz。下表坐标单位为米，分别表示右、前、上三个方向；负的右向坐标表示位于左侧。

| 短声 | 右 | 前 | 上 |
| --- | ---: | ---: | ---: |
| `SFX_Pipe_Resonance_01` | −2 | 7 | 2 |
| `SFX_Pipe_Resonance_02` | 3 | 11 | 2.5 |
| `SFX_Pipe_Resonance_03` | −1.5 | 17 | 3 |
| `SFX_Metal_Creak_01` | 2 | 5 | 2 |
| `SFX_Metal_Creak_02` | −2 | 12 | 1 |
| `SFX_Structure_Groan_01` | −2 | 8 | 2 |
| `SFX_Structure_Groan_02` | 2 | 13 | 2.5 |
| `SFX_Machine_Cycle_01` | −3 | 10 | 0.5 |
| `SFX_Machine_Cycle_02` | 3 | 14 | 0.8 |
