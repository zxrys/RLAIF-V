# Data Engine

## Overview
此部分代码用于为您构建 DPO 数据集，您可以直接用它来进行训练。  
您只需输入奖励模型（reward model）、指令模型（instruct model）和数据集，我们将为您构建 DPO 数据集。您只需运行 `run_engine.sh` 脚本即可。\
指令模型：我们使用指令模型来生成数据集中给定问题的原始答案。 \
奖励模型：我们用来评估指令模型生成的答案的模型。我们借助奖励模型获得答案的奖励，并使用此奖励对答案进行排名。之后，我们可以构建 DPO 数据集。

## Usage
请查看 `run_engine.sh` 脚本。

您可以指定要用于生成偏好训练数据集的奖励模型和指令模型。当前支持的奖励模型和指令模型列表如下：\
llava-1.5-7b、RLAIF-V-7B、OmniLMM-12B 和 RLAIF-V-12B。我们也在考虑添加更多模型。\
如果您选择的模型不在模型列表中，您可能需要自行实现相关代码：（`RLAIF-V/builder` 用于模型加载；对于初始回答抽样，请参考`RLAIF-V/llava/llava15_sample_data.py`是如何对数据进行格式化的（请不要忘记传递`raw_images`）同时将您的调用代码添加到`RLAIF-V/data_engine/answer_sampler.py`中; 对于logps计算，请更改`RLAIF-V/data_engine/logps_calculator.py`中用于格式化数据的部分，和`RLAIF-V/muffin/eval/muffin_inference_logp.py`的`get_multimodal_sample_logps`函数）。

另外，**请务必确认您提供的模型名称正确，否则我们无法确定该运行哪段代码**。

接下来是您的数据集，它应该包含以下字段：
1. `idx`：每条数据的唯一索引（可以是字符串）。
2. `question`：图像对应的问题。
3. `image`：该列应遵循以下结构：
   - {'bytes': ..., 'path':...}
   - `bytes` 应为二进制格式。
   - `path` 字段不是必须的，但为了避免错误，建议您保留此字段（可以设置为空字符串）。

您可以选择设置 `--work_dir`，我们将在该目录下保存中间文件和最终输出（实际上是该目录下的子目录）。

如果在生成过程中遇到错误，您可以使用 `--continue_from_stage` 参数指定已完成阶段的下一个阶段（0、1、2）。如果值为 0，则从头开始。（例如，您完成了阶段 0 和阶段 1，在阶段 2 遇到错误，修复问题后设置 `--continue_from_stage 2` 以继续执行）。您可以查看文件 `data_engine.py` 了解每个阶段的具体内容。

运行：
```shell
sh data_engine/run_data_engine.sh
```
