# Final 作业要求核对

核对日期：2026-11-01。依据用户提供的《2026 SHU 基础实践 Task & Final》中“期末作业 Final”部分。平时作业的 AIGC 调研不属于本次 Final 文件包的必需材料。

## 作品与工程

| 作业要求 | 状态 | 对应内容 |
| --- | --- | --- |
| 确定场景，提供图片及文字说明 | 已完成 | [README](../README.md) 描述地下混凝土通风走廊，附 AI 概念图并注明生成方式 |
| 分析持续基底及间断短声需求 | 已完成 | README 的场景分析、结构及参数说明 |
| 收集声音素材 | 已完成 | 9 份 Freesound 素材，作者、来源、许可和改编用途见 [Sources](Sources.md) |
| 剪辑和导出声音资产 | 已完成 | 使用 Python 音频处理工具剪辑、滤波、淡化及导出；脚本与参数记录已保留 |
| 基底时长大于 30 秒 | 已完成 | 3 条持续层分别为 60、64、54 秒 |
| 间断随机声至少 3 个以上 | 已完成 | 9 条不同短声，时长 1.15–8 秒 |
| 48 kHz／24 bit／stereo WAV | 已完成 | `Audio/Exports/` 的 12 条导出文件与 `Originals/SFX/Corridor/` 的 12 条工程引用副本均符合 |
| Wwise 2025.1.11.9262 | **存在版本差异** | 实际使用 2025.1.12.9287；用户已确认保留当前版本，尚未在指定版本中打开，不代表教师已同意该差异 |
| 创建非中文名称的新工程 | 已完成 | `Final.wproj`，工程名 `Final` |
| 正确配置 .gitignore | 已完成 | 排除缓存、备份、本地工具环境、个人设置、生成的 SoundBank 和录音中间文件 |
| 将声音资产导入 Wwise | 已完成 | 12 个 AudioFile 引用均有对应音频文件 |
| 持续基底循环 | 已完成 | 三个持续层均启用无限循环；实际播放记录跨越各自循环长度 |
| Random Container 随机触发短声 | 已完成 | `RND_Pipe_And_Metal` 与 `RND_Distant_Mechanism`，含随机顺序、间隔、音高和音量变化 |
| Positioning 随距离变化 | 已完成 | 9 条短声具有不同的 Listener with Automation 位置，并应用音量／低通距离衰减；实际播放记录包含衰减结果 |
| 在 Soundcaster Session 预览 | 已完成 | `SC_Corridor_Final` 的 6 个入口；102.4 秒实际整体混音录音及截图已保留 |

剪辑说明见 [AudioEditing](AudioEditing.md) 和 [AudioExpansion](AudioExpansion.md)。作业允许使用数字音频工作站或声音剪辑工具，本作品使用脚本形式的音频处理工具，不包含 REAPER 等 DAW 工程文件。

## 提交及课程准备事项

| 事项 | 当前状态 |
| --- | --- |
| 上传至公开 GitHub 仓库 | 工程与配套材料位于 [ULookup/GameAudio 的 Final 目录](https://github.com/ULookup/GameAudio/tree/main/Final) |
| 将仓库链接发送至 xichen@soundoer.com | 尚未发送；邮件草稿随本地交付材料提供 |
| 邮件标题 | 必须使用 `SHU261基础实践_Final_[学号]_[姓名]`，将方括号内容替换为本人信息 |
| 注册 Audiokinetic、安装 Launcher、学习官方基础教程 | 当前安装的 Wwise 可使用；个人账户注册、Launcher 使用和教程学习情况无法由工程文件确认 |

作业未要求提交游戏可执行文件、生成的 SoundBank、操作视频或 DAW 会话文件，因此未将这些项目列为缺失。

## 实际播放记录

[最终试听](../Preview/Corridor_Expanded_Preview.wav) 为 Soundcaster 实际输出，连续播放观察约 100 秒后淡出停止。三个持续层均持续存在，两个随机组均有触发，包含结构异响和机器工作片段。随机播放并不保证每次包含全部短声。

整理提交材料时发现 `Play_Bed_Only` 少了主基底的 Action，现已补齐为“主基底”和“新增背景层容器”两条播放动作。短暂实际播放确认三个持续层同时存在，随后已停止；完整环境事件与最终混音录音不受此修复影响。

证据：[整体播放记录](SoundcasterPlayback.json)、[三层基底单独播放记录](BedOnlyPlayback.json)、[Soundcaster 截图](Images/Soundcaster_Expanded_Playback.jpg)、[各短声位置](SpatialPositions.json)。

## 提交包内容

- `Final.wproj` 和所有 `.wwu` 工作单元，构成完整可编辑工程。
- `Originals/`：Wwise 引用音频及厂商预设依赖。
- `Audio/Exports/`：12 条符合规定格式的导出资产。
- `Preview/Corridor_Expanded_Preview.wav`：最终混音试听。
- `Docs/`：来源、剪辑参数、场景图、当前播放截图及核对说明。
- `Tools/`：制作脚本，仅供查阅及重复制作；正常试听不需要运行。
- `README.md` 与 `.gitignore`。

提交包已排除缓存、自动生成文件、个人设置、原始录音中间文件、旧版试听及本地备份。原始 Freesound 下载素材保留在本机 Downloads；重新运行音频剪辑脚本需要这些原素材，正常打开工程和播放不需要。
