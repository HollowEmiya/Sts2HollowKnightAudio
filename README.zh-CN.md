# Hollow Knight 音频工程

FMOD Studio 2.03.06；基于教程指定的 STS2 最简工程制作。

## 打开和构建

打开 `HollowKnightAudio.fspro`。事件在 Events 的 `sfx/hollow_knight` 和 `music/hollow_knight` 下。
执行 `./Build.ps1` 重建、导出 GUID、检查 71 个事件，并更新 `Package/`。
也可以在 FMOD 里 File → Build、File → Export GUIDs，再运行脚本整理打包文件。
`Assets/` 是原始 OGG，未裁剪、变调或混入 vibration 素材；音频文件可直接试听。

## 内容

54 个音效：法术 12 个、剑技 6 个、聚集/梦之钉/水晶冲刺 12 个、角色动作 10 个、梦境音效 6 个。
包含白波、下砸准备/下冲/落地、黑砸落地、白吼/黑吼、吸虫施法和弹跳、暗影触须、剑技蓄力开始/完成/循环、强力劈砍、长短旋风斩等。
骨钉蓄力循环、聚集蓄力、水晶冲刺循环是持续事件；需持有播放实例并在释放、取消或战斗结束时停止，不能用一次性 Play 后放任播放。
旋风斩长/短素材是完整的一次性片段，没有强制循环。

17 个音乐：标题、德特茅斯、苍绿之径、十字路、真菌荒地、白宫、大黄蜂、螳螂领主、战斗姐妹、格林、梦魇之王格林、空洞骑士、辐光、纯粹容器、梦境战斗、暗影音乐。
音乐使用流式读取和全片循环。它们保留原版导出的单独音轨，没有复刻 HK 的场景分层混音；循环接缝、切歌淡化和游戏内响度仍需按实际场景试听调整。

`AudioManifest.csv/json` 记录事件路径、源文件、bank 和循环状态。事件名保留源文件名便于核对。
没有找到单独命名的冲刺劈砍或暗影之魂素材，因此没有把其他角色的声音冒充它们；冲刺劈砍能否复用强力劈砍、黑波能否复用白波，需要结合 HK 原版状态机再确认。

## 接入尖塔 2 / RitsuLib

把 `Package/` 内两个 bank 和 GUIDs.txt 放到模组的 `Resources/Audio/`。
只加载这两个自定义 bank。不要复制或加载本工程构建产生的 Master.bank 或 Master.strings.bank。
原版 mixer/bank GUID 保留自 STS2 模板；音效路由到 `bus:/master/sfx`，音乐到 `bus:/master/music`。
`Package/GUIDs.txt` 只包含本工程 71 个事件与 2 个 bank，避免注册模板无关映射。

在 Entry.Init() 注册（参考 `Integration/HollowKnightAudio.cs.example`）：

```csharp
FmodStudioDeferredBankRegistration.RegisterBank("res://Resources/Audio/HK_Emiya_SFX.bank");
FmodStudioDeferredBankRegistration.RegisterBank("res://Resources/Audio/HK_Emiya_Music.bank");
FmodStudioDeferredBankRegistration.RegisterStudioGuidMappings("res://Resources/Audio/GUIDs.txt");
```

命名空间 `STS2RitsuLib.Audio`。Godot 导出设置需包含 `*.bank,GUIDs.txt` 非资源文件。
一次性事件示例：

```csharp
SfxCmd.Play("event:/sfx/hollow_knight/spells/hero_void_scream_spell");
```

音乐事件和循环音效应由已有的音乐/音频实例管理代码播放、停止、释放，并在场景结束清理。
本次交付独立音频工程和接入示例，没有修改模组的卡牌触发代码或替换游戏音乐。

## 验证范围和来源

已使用 FMOD 2.03.06 从落盘工程重新加载、构建，并检查事件素材、轨道、bank、总线路由、流式音乐和循环区域。
尚未进行游戏内试听、卡牌时序、取消蓄力或切歌测试。

素材来自本机 `E:/EProjects/FullHollowKnightResources/FullHollowKnightResources/Assets/AudioClip`。
这些音频为 Team Cherry / 原音乐作者的原版资源，本工程不代表取得其再分发授权。
教程：https://tutorials.sts2modding.com/docs/04-ritsulib/04-10-add-audio/
基础工程：https://github.com/BAKAOLC/STS2_FModProject_Minimal

## 梦境音效扩展
新增 dream_enter、dream_enter_pt_2、dream_orb_pickup、dream_ghost_appear、dream_damage、dreamshield_attack 六个一次性事件，位于 event:/sfx/hollow_knight/dream/。梦之钉蓄力和挥击仍使用原有 charge 分类下的原版素材。梦之门的建立与召回复用梦境进入音效，不使用 dream_gate_fail 失败提示。


## 虚空之心 / 联合虚空音乐（完整双声部编排）

事件：`event:/music/hollow_knight/music/void_heart_birthplace`；bank：`HK_Emiya_VoidHeart.bank`。事件 GUID、出牌触发与音乐路由不变。

原场景 Dream_Abyss 并非固定长度的单曲：先使用 HKDecline 的 Sub Area，再由后续 Music Region 切换到 Action and Sub，后者的过渡时间为 10 秒。Sub=channelInfos[3]=S59-55 Final Stage 3；Action=channelInfos[2]=S59-55 Final Stage 2。旧版本只包含 Sub，漏掉了后续弦乐。

当前制作是自动展开的 108 秒编排，保留两条原版 36 秒声部的全部内容。0–36 秒为底层声部（开头 15 秒淡入）；36 秒开始用 10 秒引入完整弦乐声部；72–108 秒是完整双声部，游戏从这里循环，避免每次回到开场。切换时刻是为卡牌战斗制作的固定编排，不冒充原版唯一固定时长或官方 OST 完整录音。

混音采用原 Action and Sub snapshot 的相对增益：Action +3.704152 dB，Sub -0.025776729 dB。对解码声部的循环边界各做 5ms 平滑，消除端点跳变；原始 OGG 文件保持不变。没有加入其他战斗声部或压缩动态。

可直接试听 `Assets/music/music/VoidHeart_Birthplace_Full.wav`。制作参数、SHA256、峰值及循环边界检测见 `VoidHeartArrangement.json`。解码与渲染脚本为 DecodeVoidHeartStems.gd、RenderFullVoidHeart.py；Godot 脚本通过 `-- <音频工程目录>` 接受工程路径，Python 需 numpy。普通修改后的 bank 构建仍使用 Build.ps1。

虚空之心成功打出后替换本场音乐，同场重复出牌不叠播；战斗结束或场景退出时恢复正常音乐。

## 召唤物攻击音效
新增 companions 分类下 8 个原版一次性事件：hatchling_charge、hatchling_explode、dung_hatchling_explode、grimmchild_fireball_shoot、spider_buddy_sword_1–4。幼崽在冲刺和命中时播放，护符臭屁版使用独立爆裂音；格林之子在发射帧播放；编织者在近身攻击动作开始时播放，按单位索引轮换4个音色。全部路由 SFX；不启动飞行或待机循环。

