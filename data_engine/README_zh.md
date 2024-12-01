# Data Engine

## Welcome
感谢您使用 Data Engine。  
此部分代码用于为您构建 DPO 数据集，您可以直接用它来进行训练。  
您只需输入奖励模型（reward model，也即一个经过DPO训练的模型，用来为您要训练的模型做指导）、指令模型（instruct model，您要训练的模型）和数据集，我们将为您构建 DPO 数据集。您只需运行 `run_engine.sh` 脚本即可。

## Usage
请查看 `run_engine.sh` 脚本。

您需要输入奖励模型和指令模型的路径及名称。目前我们支持以下模型：llava-1.5-7b、RLAIF-V-7B、OmniLMM-12B 和 RLAIF-V-12B。我们也在考虑添加更多模型。\
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

## Conclusion
如果您遇到任何问题，请随时通过提交 Issues 联系我们。

感谢您选择 RLAIF-V，祝您使用愉快！
