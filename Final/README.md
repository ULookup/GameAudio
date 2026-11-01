# Underground Ventilation Corridor

SHU261 基础实践 Final：地下避难所环境声设计。

![地下避难所通风走廊概念图](Docs/Images/Underground_Ventilation_Corridor.png)

## 场景与声音设计

设计对象是地下避难所内的混凝土通风走廊。听者停留在走廊内，空气持续流动，远处通风设备保持运转，管道与金属支架偶尔发出共鸣和摩擦声，间歇出现较低沉的结构异响和机器工作声。

持续环境由三层组成：60 秒的走廊空气主基底、64 秒的深层通风声、54 秒的微弱空间共鸣。各层使用不同循环长度，减轻同时重复的感觉。9 条短声分为两个随机组，以不同的方位、距离和播放间隔构成细节。

## 内容与规格

| 内容 | 数量与规格 |
| --- | --- |
| 持续循环 | 3 条，分别为 60、64、54 秒 |
| 间断短声 | 9 条，包含管道共鸣、金属吱声、结构异响和机器工作片段 |
| 导出音频 | 48 kHz／24 bit PCM／双声道 WAV |
| 最终试听 | [完整环境混音](Preview/Corridor_Expanded_Preview.wav)，102.4 秒实际 Soundcaster 输出 |
| 工程 | [Final.wproj](Final.wproj)，完整可编辑 Wwise 工程 |

工程使用 **Wwise 2025.1.12.9287** 制作；课程指定版本为 **2025.1.11.9262**。两者存在版本差异，工程未在指定版本中打开。

## 打开与试听

1. 下载完整工程目录，保留 `Final.wproj`、各工作单元目录和 `Originals/`。
2. 使用 Wwise 2025.1.12.9287 打开 `Final.wproj`。
3. 在 Project Explorer 的 **Sessions → Default Work Unit** 中双击 `SC_Corridor_Final`。
4. 点击 `Play_Corridor_Ambience` 模块的播放按钮，试听完整环境。
5. 切换分层试听前，先点击 Soundcaster 总停止按钮，避免重复叠加。

| Soundcaster 入口 | 播放内容 |
| --- | --- |
| `Play_Corridor_Ambience` | 完整环境：3 个持续层与 2 个随机组 |
| `Play_Bed_Only` | 3 个持续层 |
| `Play_Random_Only` | 管道共鸣与金属吱声 |
| `Play_Distant_Mechanism_Only` | 结构异响与机器工作片段 |
| `Play_Deep_Ventilation_Only` | 深层通风 |
| `Play_Space_Resonance_Only` | 空间共鸣 |

随机组设有初始等待及播放间隔，点击播放后不一定立即出现。每次播放的顺序和间隔会变化。`Stop_Corridor_Ambience` 事件以 2 秒淡出停止完整环境。

## 文件说明

- `Audio/Exports/`：12 条导出资产。
- `Originals/`：工程引用的音频及厂商预设依赖。
- `Preview/`：最终混音试听。
- [声音设计与参数](Docs/SoundDesign.md)：选段、处理、随机播放和距离设置。
- [素材来源](Docs/Sources.md)：音效作者、来源链接及许可。

`Originals/Plugins/` 内的混响 IR 随厂商预设保留，不计入本作品的 12 条音频资产。
