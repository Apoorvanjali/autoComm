"""
LoRA demo: speech-to-text fine-tuning (isolated from main app).

Dataset: librispeech_asr (clean)
Model: facebook/wav2vec2-base-960h (default)
Metric: WER
"""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from typing import Dict, List, Union

import evaluate
import numpy as np
import torch
from datasets import Audio, load_dataset
from peft import LoraConfig, TaskType, get_peft_model
from transformers import (
    AutoModelForCTC,
    AutoProcessor,
    Trainer,
    TrainingArguments,
)

from common import DemoReport, count_parameters, ensure_dir, set_seed, utc_now_iso, write_report


@dataclass
class DataCollatorCTCWithPadding:
    processor: AutoProcessor
    padding: Union[bool, str] = True

    def __call__(self, features: List[Dict[str, Union[List[int], np.ndarray]]]) -> Dict[str, torch.Tensor]:
        input_features = [{"input_values": feature["input_values"]} for feature in features]
        label_features = [{"input_ids": feature["labels"]} for feature in features]

        batch = self.processor.pad(input_features, padding=self.padding, return_tensors="pt")
        labels_batch = self.processor.tokenizer.pad(label_features, padding=self.padding, return_tensors="pt")

        labels = labels_batch["input_ids"].masked_fill(labels_batch.attention_mask.ne(1), -100)
        batch["labels"] = labels
        return batch


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="LoRA speech-to-text demo")
    parser.add_argument("--model", default="facebook/wav2vec2-base-960h")
    parser.add_argument("--dataset", default="librispeech_asr")
    parser.add_argument("--config", default="clean")
    parser.add_argument("--train-samples", type=int, default=120)
    parser.add_argument("--eval-samples", type=int, default=40)
    parser.add_argument("--epochs", type=float, default=1.0)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", default="examples/outputs/lora_speech")
    return parser.parse_args()


def prepare_sample(batch, processor):
    audio = batch["audio"]
    inputs = processor(audio["array"], sampling_rate=audio["sampling_rate"])
    batch["input_values"] = inputs.input_values[0]

    with processor.as_target_processor():
        batch["labels"] = processor(batch["text"]).input_ids
    return batch


def compute_metrics_builder(processor):
    wer = evaluate.load("wer")

    def compute_metrics(pred):
        pred_ids = np.argmax(pred.predictions, axis=-1)
        pred.label_ids[pred.label_ids == -100] = processor.tokenizer.pad_token_id

        pred_str = processor.batch_decode(pred_ids)
        label_str = processor.batch_decode(pred.label_ids, group_tokens=False)

        error = wer.compute(predictions=pred_str, references=label_str)
        return {"wer": round(float(error), 4)}

    return compute_metrics


def main() -> None:
    args = parse_args()
    set_seed(args.seed)
    ensure_dir(args.output_dir)

    print(f"Loading dataset: {args.dataset} ({args.config})")
    train_ds = load_dataset(args.dataset, args.config, split=f"train.100[:{args.train_samples}]")
    eval_ds = load_dataset(args.dataset, args.config, split=f"validation[:{args.eval_samples}]")

    train_ds = train_ds.cast_column("audio", Audio(sampling_rate=16000))
    eval_ds = eval_ds.cast_column("audio", Audio(sampling_rate=16000))

    print(f"Loading processor/model: {args.model}")
    processor = AutoProcessor.from_pretrained(args.model)
    base_model = AutoModelForCTC.from_pretrained(args.model)

    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.1,
        bias="none",
        task_type=TaskType.FEATURE_EXTRACTION,
    )
    model = get_peft_model(base_model, lora_config)
    param_stats = count_parameters(model)

    train_prepared = train_ds.map(
        lambda x: prepare_sample(x, processor),
        remove_columns=train_ds.column_names,
    )
    eval_prepared = eval_ds.map(
        lambda x: prepare_sample(x, processor),
        remove_columns=eval_ds.column_names,
    )

    data_collator = DataCollatorCTCWithPadding(processor=processor)
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        learning_rate=args.lr,
        num_train_epochs=args.epochs,
        logging_steps=10,
        save_strategy="no",
        eval_strategy="epoch",
        report_to=[],
        fp16=torch.cuda.is_available(),
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_prepared,
        eval_dataset=eval_prepared,
        tokenizer=processor.feature_extractor,
        data_collator=data_collator,
        compute_metrics=compute_metrics_builder(processor),
    )

    print("Training LoRA adapters for speech-to-text...")
    trainer.train()

    metrics = trainer.evaluate()
    adapter_dir = os.path.join(args.output_dir, "adapter")
    model.save_pretrained(adapter_dir)
    processor.save_pretrained(adapter_dir)

    report = DemoReport(
        task="speech_to_text",
        base_model=args.model,
        dataset=f"{args.dataset}:{args.config}",
        train_samples=args.train_samples,
        eval_samples=args.eval_samples,
        metrics={k: float(v) for k, v in metrics.items() if isinstance(v, (int, float))},
        trainable_parameters=param_stats["trainable"],
        total_parameters=param_stats["total"],
        trainable_percent=param_stats["trainable_percent"],
        output_dir=args.output_dir,
        generated_at_utc=utc_now_iso(),
    )
    write_report(os.path.join(args.output_dir, "report.json"), report)
    print(f"Done. Report: {os.path.join(args.output_dir, 'report.json')}")


if __name__ == "__main__":
    main()
