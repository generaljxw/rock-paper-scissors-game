# 音频素材评审文档

**项目**: 儿童猜拳小游戏
**版本**: v2.1
**日期**: 2026-06-03
**状态**: 待评审
**编制人**: Coder开发工程师

---

## 1. 素材获取方案

### 1.1 获取途径

| 途径 | 适用范围 | 版权状态 | 说明 |
|------|----------|----------|------|
| Mixkit Free SFX | 6个SFX音效 | Mixkit License | 免费商用，无需署名，专业录制 |
| Python高质量合成（numpy+scipy） | 9首BGM | 无版权限制 | 自主生成，旋律+和弦+贝斯+鼓点 |

### 1.2 版权合规性审查

| 素材来源 | 许可协议 | 商用授权 | 署名要求 | 合规状态 |
|----------|----------|----------|----------|----------|
| Mixkit Free SFX | Mixkit License | 免费商用 | 无需署名 | 合规 |
| Python合成（BGM） | 自主生成 | 完全可用 | 无需署名 | 合规 |

### 1.3 Mixkit License 说明

- 允许在个人和商业项目中免费使用
- 无需署名（attribution not required）
- 不可将音效素材单独重新分发或转售
- 详细许可协议: https://mixkit.co/license/#sfxFree

---

## 2. 最终素材核验结果

### 2.1 音效（SFX）- 来源: Mixkit Free SFX

| 序号 | 文件名 | 场景 | Mixkit素材名 | 时长 | 大小 | 时长要求 | 大小限制 | 核验结果 |
|------|--------|------|-------------|------|------|----------|----------|----------|
| 1 | rock.wav | 石头出拳 | Martial arts fast punch | 1.3s | 220KB | 1-3s | ≤500KB | PASS |
| 2 | scissors.wav | 剪刀出拳 | Sword cutting and killing | 1.2s | 215KB | 1-3s | ≤500KB | PASS |
| 3 | paper.wav | 布出拳 | Quick whoosh | 1.3s | 224KB | 1-3s | ≤500KB | PASS |
| 4 | win.wav | 胜利判定 | Winning a coin video game | 2.0s | 340KB | 1-3s | ≤500KB | PASS |
| 5 | lose.wav | 失败判定 | Player losing or failing | 1.1s | 195KB | 1-3s | ≤500KB | PASS |
| 6 | draw.wav | 平局判定 | Game bonus reached (trimmed) | 2.0s | 345KB | 1-3s | ≤500KB | PASS |

**SFX核验说明:**
- 全部6个SFX时长和大小均符合要求（1-3s, ≤500KB）
- paper.wav: 已替换为Mixkit ID 2430（Quick whoosh），1.3s短促挥动声，更符合"布"的轻柔飘动特性
- draw.wav: 已对原始音效进行剪辑处理，截取前2秒精华段落，保留关键识别元素
- 所有SFX为专业录音棚录制，音质清晰，风格统一

### 2.2 背景音乐（BGM）- 来源: Python高质量合成

| 序号 | 文件名 | 场景 | 风格描述 | 时长 | 大小 | 时长要求 | 核验结果 |
|------|--------|------|----------|------|------|----------|----------|
| 1 | login.wav | 登录界面 | C大调欢快旋律+和弦+贝斯+鼓点 | 35.0s | 5.9MB | ≥30s | PASS |
| 2 | mode_select.wav | 模式选择界面 | G大调轻松旋律+和弦+贝斯+鼓点 | 35.0s | 5.9MB | ≥30s | PASS |
| 3 | battle_mode1.wav | 一局定胜负 | C调紧张旋律+快速鼓点(130BPM) | 35.0s | 5.9MB | ≥30s | PASS |
| 4 | battle_mode2.wav | 三局两胜 | A调竞技旋律+稳定鼓点(120BPM) | 35.0s | 5.9MB | ≥30s | PASS |
| 5 | battle_mode3.wav | 连战模式 | D调持续紧张旋律+快速鼓点(140BPM) | 35.0s | 5.9MB | ≥30s | PASS |
| 6 | settlement_normal_win.wav | 普通胜利结算 | C大调欢快庆祝+鼓点(120BPM) | 20.0s | 3.4MB | ≥15s | PASS |
| 7 | settlement_normal_lose.wav | 普通失败结算 | A小调低沉旋律+贝斯(75BPM) | 18.0s | 3.1MB | ≥15s | PASS |
| 8 | survival_win.wav | 连战胜利结算 | C大调激昂庆祝+鼓点(120BPM) | 20.0s | 3.4MB | ≥15s | PASS |
| 9 | survival_lose.wav | 连战失败结算 | A小调沉重旋律+贝斯(75BPM) | 18.0s | 3.1MB | ≥15s | PASS |

**BGM核验说明:**
- 全部9首BGM时长均满足需求要求
- 所有BGM包含旋律+和弦+贝斯+鼓点（失败结算无鼓点），音乐层次丰富
- 对战模式BGM节奏区分明确: mode1=130BPM, mode2=120BPM, mode3=140BPM
- 当前为WAV格式（无损），转MP3后大小将降至约300-500KB/首
- 所有BGM支持循环播放（loop），首尾有淡入淡出处理

### 2.3 核验总结

| 类别 | 总数 | 通过 | 警告 | 不通过 | 说明 |
|------|------|------|------|--------|------|
| SFX | 6 | 6 | 0 | 0 | 全部时长和大小符合要求 |
| BGM | 9 | 9 | 0 | 0 | 全部时长和风格符合要求 |

---

## 3. 素材技术规格

### 3.1 SFX素材详情（Mixkit专业录制）

| 文件名 | Mixkit ID | 描述 | 原始格式 |
|--------|-----------|------|----------|
| rock.wav | 2161 | Martial arts fast punch - 武术快速出拳，低沉有力 | WAV 44100Hz 16bit |
| scissors.wav | 2166 | Sword cutting and killing - 剑刃剪切，锐利快速 | WAV 44100Hz 16bit |
| paper.wav | 2430 | Quick whoosh - 短促挥动声，轻柔飘动感 | WAV 44100Hz 16bit |
| win.wav | 2000 | Winning a coin video game - 游戏获胜金币声 | WAV 44100Hz 16bit |
| lose.wav | 2001 | Player losing or failing - 玩家失败音效 | WAV 44100Hz 16bit |
| draw.wav | 2064 | Game bonus reached (trimmed 2s) - 游戏奖励达成，截取精华段落 | WAV 44100Hz 16bit |

### 3.2 BGM合成参数

| 参数 | 值 | 说明 |
|------|-----|------|
| 采样率 | 44100 Hz | CD音质标准 |
| 位深度 | 32 bit float | 高精度合成 |
| 声道 | 单声道 | 游戏音效标准 |
| 旋律合成 | 正弦波+泛音(1-4次) | 丰富音色 |
| 贝斯合成 | 正弦波+三角波混合 | 温暖低音 |
| 鼓点合成 | 底鼓+军鼓+踩镲 | 标准节奏组 |
| 和弦 | 三和弦(根音+三度+五度) | 丰富和声 |
| 包络 | ADSR(Attack/Decay/Sustain/Release) | 自然音色 |
| 循环 | 交叉淡入淡出(0.5s) | 无缝循环 |
| 首尾 | 淡入0.3-0.5s/淡出0.8-1.0s | 平滑过渡 |

---

## 4. 评审记录

### 4.1 占位素材评审结果（已归档）

**评审日期**: 2026-06-03
**评审结论**: 三种对战模式BGM节奏符合预期，其余占位素材质量未达标准，全部占位素材不纳入最终素材库。

### 4.2 当前素材评审

| 角色 | 姓名 | 日期 | 评审结果 |
|------|------|------|----------|
| Planner架构师 | Planner | | |
| 项目负责人 | 用户 | | |

### 4.3 评审意见

| 序号 | 素材文件 | 评审意见 | 处理结果 |
|------|----------|----------|----------|
| 1 | | | |
| 2 | | | |
| 3 | | | |

### 4.4 评审结论

- [ ] 全部通过，可进入开发集成
- [ ] 部分需修改，修改后重新评审
- [ ] 需全面重新制作

---

## 5. 格式转换说明

当前素材为WAV格式（无损），最终交付需转为MP3格式：

| 格式 | 用途 | 比特率 | 说明 |
|------|------|--------|------|
| WAV | 开发调试 | 1411kbps | 当前素材格式 |
| MP3 | 最终交付 | 128kbps | BGM和SFX统一使用MP3 |
| OGG | 备选 | 128kbps | QMediaPlayer兼容格式 |

转换命令示例：
```bash
# 使用ffmpeg批量转换WAV到MP3
ffmpeg -i input.wav -b:a 128k output.mp3
```

预估MP3格式大小：
- BGM: 约300KB-500KB/首（远小于3MB限制）
- SFX: 约20KB-50KB/个（远小于500KB限制）
