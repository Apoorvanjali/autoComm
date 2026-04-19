"""
LoRA demo: translation fine-tuning (isolated from main app).

Dataset: opus_books (en-fr)
Model: Helsinki-NLP/opus-mt-en-fr (default)
Metric: SacreBLEU
"""

from __future__ import annotations

import argparse
import os
from typing import Dict

import evaluate
from datasets import load_dataset
from peft import LoraConfig, TaskType, get_peft_model
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
)

from common import DemoReport, count_parameters, ensure_dir, set_seed, utc_now_iso, write_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="LoRA translation demo")
    parser.add_argument("--model", default="Helsinki-NLP/opus-mt-en-fr")
    parser.add_argument("--dataset", default="opus_books")
    parser.add_argument("--config", default="en-fr")
    parser.add_argument("--train-samples", type=int, default=500)
    parser.add_argument("--eval-samples", type=int, default=120)
    parser.add_argument("--epochs", type=float, default=1.0)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--max-input", type=int, default=128)
    parser.add_argument("--max-target", type=int, default=128)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", default="examples/outputs/lora_translation")
    return parser.parse_args()


def preprocess_batch(batch, tokenizer, max_input: int, max_target: int):
    pairs = batch["translation"]
    source_texts = [p["en"] for p in pairs]
    target_texts = [p["fr"] for p in pairs]
    model_inputs = tokenizer(source_texts, max_length=max_input, truncation=True)
    labels = tokenizer(text_target=target_texts, max_length=max_target, truncation=True)
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs


def compute_metrics_builder(tokenizer):
    sacrebleu = evaluate.load("sacrebleu")

    def compute_metrics(eval_pred) -> Dict[str, float]:
        predictions, labels = eval_pred
        decoded_preds = tokenizer.batch_decode(predictions, skip_special_tokens=True)
        labels = [[(token if token != -100 else tokenizer.pad_token_id) for token in row] for row in labels]
        decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)

        refs = [[label] for label in decoded_labels]
        score = sacrebleu.compute(predictions=decoded_preds, references=refs)
        return {"bleu": round(float(score.get("score", 0.0)), 4)}

    return compute_metrics


def main() -> None:
    args = parse_args()
    set_seed(args.seed)
    ensure_dir(args.output_dir)

    print(f"Loading dataset: {args.dataset} ({args.config})")
    train_ds = load_dataset(args.dataset, args.config, split=f"train[:{args.train_samples}]")
    eval_ds = load_dataset(args.dataset, args.config, split=f"train[{args.train_samples}:{args.train_samples + args.eval_samples}]")

    print(f"Loading model/tokenizer: {args.model}")
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    base_model = AutoModelForSeq2SeqLM.from_pretrained(args.model)

    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.1,
        bias="none",
        task_type=TaskType.SEQ_2_SEQ_LM,
    )
    model = get_peft_model(base_model, lora_config)
    param_stats = count_parameters(model)

    train_tokenized = train_ds.map(
        lambda x: preprocess_batch(x, tokenizer, args.max_input, args.max_target),
        batched=True,
        remove_columns=train_ds.column_names,
    )
    eval_tokenized = eval_ds.map(
        lambda x: preprocess_batch(x, tokenizer, args.max_input, args.max_target),
        batched=True,
        remove_columns=eval_ds.column_names,
    )

    data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model)
    training_args = Seq2SeqTrainingArguments(
        output_dir=args.output_dir,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        learning_rate=args.lr,
        num_train_epochs=args.epochs,
        logging_steps=10,
        save_strategy="no",
        eval_strategy="epoch",
        predict_with_generate=True,
        report_to=[],
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_tokenized,
        eval_dataset=eval_tokenized,
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics_builder(tokenizer),
    )

    print("Training LoRA adapters for translation...")
    trainer.train()

    metrics = trainer.evaluate()
    adapter_dir = os.path.join(args.output_dir, "adapter")
    model.save_pretrained(adapter_dir)
    tokenizer.save_pretrained(adapter_dir)

    report = DemoReport(
        task="translation",
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
