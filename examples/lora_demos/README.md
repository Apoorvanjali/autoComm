# LoRA Demo Suite (Isolated)

This folder contains isolated LoRA fine-tuning demos for multiple AutoComm-relevant tasks.

Important: This suite is intentionally separated from the production app flow. It does not modify routes, services, or UI in the main AutoComm runtime.

## Included Demos

1. Summarization

- Script: `examples/lora_demos/run_summarization_lora.py`
- Base model: `google/flan-t5-small`
- Dataset: `xsum`
- Metric: ROUGE

2. Translation

- Script: `examples/lora_demos/run_translation_lora.py`
- Base model: `Helsinki-NLP/opus-mt-en-fr`
- Dataset: `opus_books` (`en-fr`)
- Metric: SacreBLEU

3. Speech-to-Text

- Script: `examples/lora_demos/run_speech_lora.py`
- Base model: `facebook/wav2vec2-base-960h`
- Dataset: `librispeech_asr` (`clean`)
- Metric: WER

## Install Side-Demo Dependencies

```bash
pip install -r requirements-lora.txt
```

## Run Commands

From repository root:

```bash
python examples/lora_demos/run_summarization_lora.py
python examples/lora_demos/run_translation_lora.py
python examples/lora_demos/run_speech_lora.py
```

Optional quick run (smaller subsets):

```bash
python examples/lora_demos/run_summarization_lora.py --train-samples 100 --eval-samples 30 --epochs 1
python examples/lora_demos/run_translation_lora.py --train-samples 150 --eval-samples 40 --epochs 1
python examples/lora_demos/run_speech_lora.py --train-samples 50 --eval-samples 20 --epochs 1
```

## Outputs

Each task writes to `examples/outputs/<task>/`:

- `adapter/` - saved LoRA adapter weights and tokenizer/processor
- `report.json` - reviewer-friendly summary with:
  - task
  - base model
  - dataset
  - sample counts
  - metric values
  - trainable parameter counts and percentage

## Reviewer Narrative (Accurate)

Use this framing in interviews/reviews:

1. Production system uses stable pretrained inference/services.
2. This suite demonstrates isolated LoRA fine-tuning capability.
3. Public benchmark datasets are used for reproducible side experiments.
