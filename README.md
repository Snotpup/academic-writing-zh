<img src="assets/avatar.png" alt="论文纸页与笔尖" width="96" height="96">

# 中文论文写作与润色

一个用于中文论文写作、润色和论证深化的 AI skill，围绕理论运用、作者判断与连贯论证改进文本，保留原意、作者立场和文献边界。

Chinese Academic Writing and Polishing: an AI skill for improving Chinese academic prose and arguments while preserving the author's meaning, stance, and source boundaries.

维护者：[Snotpup](https://github.com/Snotpup)。许可证：[MIT](LICENSE)。

## 能做什么

- 重组段落，补足材料能够支持的推理，深化分析与文献对话。
- 结合章节功能落实九项中文表达要求，减少空话、概念堆叠和模板化过渡。
- 保留四类输入区，接受直接粘贴的内容、文件路径或目录路径；需要相关材料时主动询问，收到路径后实际读取。
- 区分文献结论、本文推论和待补证据，不编造引用，不把相关关系写成因果关系。

## 快速开始

从 [Releases](https://github.com/Snotpup/academic-writing-zh/releases) 下载需要的版本：

- `academic-writing-zh-版本号.zip`：通用 skill 包。
- `academic-writing-zh-upload-版本号.zip`：将中英文展示元数据放在 frontmatter 顶层的上传适配包，仅在上传端要求这些字段时使用。
- `SHA256SUMS`：下载文件的校验值。

把解压后的 `academic-writing-zh` 文件夹交给支持 skill 的工具，按该工具的安装方式使用；也可以在能够读取本地文件的 AI 工具中直接指定 `SKILL.md`。不同工具对安装位置和文件读取的支持不同，本项目不保证所有客户端都能直接安装。

使用时说明当前任务，并提供需要的材料。例如：

```text
请读取 academic-writing-zh/SKILL.md，按此技能润色讨论章节。
允许重组段落、补足推理和深化分析，保留我的原意、立场与文献边界。

参考文献的相关信息：提供登记条目与摘要、摘录、全文的内容或路径。
待优化的论文原文：提供原文或文件路径，并指出当前版本及处理范围。
论文写作结构：提供目录、章节安排或相关上下文的内容或路径。
其它相关信息：提供研究问题、作者立场、背景材料及其他要求。
```

不需要每次把四类材料重新填一遍。已有信息可以沿用，只补充本次任务需要而尚未取得的部分。也可以指定只做诊断、逐段对照或只输出正文。

## 使用边界

技能文件提供写作规则，不会自行运行论文上传程序。材料会经过哪些模型和服务，取决于你实际使用的 AI 工具与配置。

文献的题名、作者和年份不能代替对文献内容的理解。缺少关键证据时，应保留具体缺口或待检验解释，不能先写成已经证实的结论。研究事实、引用准确性与最终采用的判断仍需作者核对。

当前版本完成了格式、打包和部分合成示例自查，尚未形成对真实论文写作效果的系统验证，也不承诺通过任何 AI 检测器。

## 版本与贡献

默认分支 `main` 用于维护当前源码，正式下载以 [Releases](https://github.com/Snotpup/academic-writing-zh/releases) 中的版本为准。变化记录见 [CHANGELOG.md](CHANGELOG.md)，修改与发布方法见 [CONTRIBUTING.md](CONTRIBUTING.md)。

欢迎在 [Issues](https://github.com/Snotpup/academic-writing-zh/issues) 提交问题或建议。请使用脱敏或合成的最小片段，避免上传未公开论文、真实个人信息、研究参与者数据或访问凭据。

MIT 允许复制、修改、分发和商用，要求保留版权与许可证声明，完整条款见 [LICENSE](LICENSE)。
