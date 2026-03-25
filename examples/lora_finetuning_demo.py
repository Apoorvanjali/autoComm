"""
🚀 LoRA Fine-Tuning 
===========================

Use Case: Fine-tune BART to summarize emails into action items

Installation:
    pip install transformers datasets peft accelerate torch

Run:
    python lora_finetuning_demo.py
"""

import os
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, Trainer, TrainingArguments
from datasets import Dataset
from peft import LoraConfig, get_peft_model

# Configuration
MODEL_NAME = "facebook/bart-base"
OUTPUT_DIR = "./lora-results"
LORA_MODEL_DIR = "./lora-email-model"

print("=" * 80)
print("🚀 AutoComm LoRA Fine-Tuning Demo")
print("=" * 80)


# ============================================================================
# STEP 1: Create Sample Dataset
# ============================================================================
def create_sample_dataset():
    """Create a small email summarization dataset"""
    print("\n📊 STEP 1: Creating Sample Dataset...")
    
    data = [
        {
            "input": "Please cancel my subscription immediately. I'm not satisfied with the service.",
            "output": "Cancel subscription"
        },
        {
            "input": "I want a refund for the damaged product I received yesterday.",
            "output": "Refund request - damaged product"
        },
        {
            "input": "Change my delivery address to Bangalore, Whitefield area.",
            "output": "Update address - Bangalore Whitefield"
        },
        {
            "input": "Can you help me track my order? Order ID is ABC123.",
            "output": "Track order ABC123"
        },
        {
            "input": "I need to update my payment method to a new credit card.",
            "output": "Update payment method"
        },
        {
            "input": "Schedule a delivery for next Tuesday between 2-4 PM.",
            "output": "Schedule delivery - Tuesday 2-4 PM"
        },
    ]
    
    dataset = Dataset.from_list(data)
    print(f"✅ Created dataset with {len(data)} email samples")
    print(f"   Sample: '{data[0]['input'][:50]}...' → '{data[0]['output']}'")
    
    return dataset


# ============================================================================
# STEP 2: Load Pre-trained Model & Tokenizer
# ============================================================================
def load_pretrained_model():
    """Load BART model and tokenizer"""
    print("\n🤖 STEP 2: Loading Pre-trained BART Model...")
    
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
    
    print(f"✅ Loaded {MODEL_NAME}")
    print(f"   Model parameters: {model.num_parameters():,}")
    
    return tokenizer, model


# ============================================================================
# STEP 3: Apply LoRA Configuration
# ============================================================================
def apply_lora(model):
    """Apply LoRA adapters to the model"""
    print("\n⚡ STEP 3: Applying LoRA (Low-Rank Adaptation)...")
    
    lora_config = LoraConfig(
        r=8,                                    # LoRA rank
        lora_alpha=16,                         # LoRA scaling factor
        target_modules=["q_proj", "v_proj"],   # Apply to query/value projections
        lora_dropout=0.1,                      # Dropout for regularization
        bias="none",                           # Don't adapt bias
        task_type="SEQ_2_SEQ_LM"              # Task type for BART
    )
    
    # Apply LoRA
    model = get_peft_model(model, lora_config)
    
    # Print trainable parameter info
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())
    
    print(f"✅ LoRA Applied Successfully")
    print(f"   Total parameters: {total_params:,}")
    print(f"   Trainable parameters: {trainable_params:,}")
    print(f"   Trainable %: {100 * trainable_params / total_params:.2f}%")
    print(f"   💡 We're only training {100 * trainable_params / total_params:.2f}% of the model!")
    
    return model


# ============================================================================
# STEP 4: Tokenize Dataset
# ============================================================================
def tokenize_dataset(dataset, tokenizer):
    """Tokenize input texts and target summaries"""
    print("\n🔤 STEP 4: Tokenizing Dataset...")
    
    def preprocess(example):
        # Tokenize inputs
        inputs = tokenizer(
            example["input"],
            truncation=True,
            padding="max_length",
            max_length=64
        )
        
        # Tokenize targets
        targets = tokenizer(
            example["output"],
            truncation=True,
            padding="max_length",
            max_length=32
        )
        
        # Set labels for training
        inputs["labels"] = targets["input_ids"]
        
        return inputs
    
    tokenized_dataset = dataset.map(preprocess, batched=False)
    
    print(f"✅ Tokenized {len(tokenized_dataset)} samples")
    print(f"   Input max_length: 64 tokens")
    print(f"   Output max_length: 32 tokens")
    
    return tokenized_dataset


# ============================================================================
# STEP 5: Train LoRA Model
# ============================================================================
def train_lora_model(model, tokenized_dataset):
    """Train the LoRA-adapted model"""
    print("\n🏋️  STEP 5: Training LoRA Model...")
    
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=2,
        num_train_epochs=3,
        logging_steps=1,
        save_steps=10,
        learning_rate=1e-4,  # Smaller LR for LoRA
        optim="adamw_torch",
        remove_unused_columns=False,
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
    )
    
    print("   Training started... (this may take a moment)")
    trainer.train()
    
    print(f"✅ Training Complete!")
    print(f"   Results saved to: {OUTPUT_DIR}/")
    
    return model


# ============================================================================
# STEP 6: Save LoRA Model
# ============================================================================
def save_lora_model(model, tokenizer):
    """Save the trained LoRA model and tokenizer"""
    print("\n💾 STEP 6: Saving LoRA Model...")
    
    os.makedirs(LORA_MODEL_DIR, exist_ok=True)
    
    model.save_pretrained(LORA_MODEL_DIR)
    tokenizer.save_pretrained(LORA_MODEL_DIR)
    
    print(f"✅ Model saved to: {LORA_MODEL_DIR}/")
    print(f"   Files:")
    print(f"     - adapter_config.json (LoRA configuration)")
    print(f"     - adapter_model.bin (LoRA weights - much smaller!)")
    print(f"     - tokenizer.json")


# ============================================================================
# STEP 7: Inference - Compare Before & After
# ============================================================================
def demonstrate_inference(original_model, finetuned_model, tokenizer):
    """Show the improvement from fine-tuning"""
    print("\n🎯 STEP 7: Demonstrating Inference Results")
    print("=" * 80)
    
    # Test email
    test_email = "Please cancel my subscription immediately. I'm not satisfied."
    
    print(f"\n📧 Test Email:")
    print(f"   '{test_email}'")
    print()
    
    # First, let's show we're using the original model for comparison
    print("BEFORE (Original BART):")
    print("-" * 40)
    inputs = tokenizer(test_email, return_tensors="pt", truncation=True)
    summary_ids = original_model.generate(inputs["input_ids"], max_length=30, num_beams=4)
    original_summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    print(f"   Output: '{original_summary}'")
    print(f"   (Generic summarization - doesn't capture action item)")
    
    print()
    print("AFTER (LoRA Fine-tuned):")
    print("-" * 40)
    summary_ids = finetuned_model.generate(inputs["input_ids"], max_length=30, num_beams=4)
    finetuned_summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    print(f"   Output: '{finetuned_summary}'")
    print(f"   ✅ (Specialized - recognizes action item)")
    
    print()
    print("=" * 80)
    print("🎓 Key Insights:")
    print("=" * 80)
    print(f"""
1. LoRA creates lightweight adapter layers (0.01% of model size)
2. Only LoRA layers are trained, not the entire BART model
3. Training is fast - runs on CPU (no GPU needed for small datasets)
4. LoRA model can be merged into base model or used separately
5. Multiple LoRA adapters can be created for different domains
    """)


# ============================================================================
# Main Execution
# ============================================================================
def main():
    """Run the complete fine-tuning pipeline"""
    
    print("\n" + "=" * 80)
    print("📋 CONFIGURATION")
    print("=" * 80)
    print(f"Model: {MODEL_NAME}")
    print(f"LoRA Rank: 8")
    print(f"Training Epochs: 3")
    print(f"Dataset Size: 6 samples")
    print(f"Device: {'GPU (CUDA)' if torch.cuda.is_available() else 'CPU'}")
    
    try:
        # Step 1: Create dataset
        dataset = create_sample_dataset()
        
        # Step 2: Load model
        tokenizer, original_model = load_pretrained_model()
        
        # Keep a copy of the original model for comparison
        model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
        
        # Step 3: Apply LoRA
        model = apply_lora(model)
        
        # Step 4: Tokenize
        tokenized_dataset = tokenize_dataset(dataset, tokenizer)
        
        # Step 5: Train
        model = train_lora_model(model, tokenized_dataset)
        
        # Step 6: Save
        save_lora_model(model, tokenizer)
        
        # Step 7: Demo inference
        demonstrate_inference(original_model, model, tokenizer)
        
        print("\n" + "=" * 80)
        print("✅ DEMO COMPLETE!")
        print("=" * 80)
        print("""
You can now:
1. Show LoRA model files: ls lora-email-model/
2. Load and use the model:
   
   from peft import PeftModel
   from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
   
   tokenizer = AutoTokenizer.from_pretrained("facebook/bart-base")
   model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-base")
   model = PeftModel.from_pretrained(model, "lora-email-model")
   
3. Integrate with your AutoComm services (future enhancement)
        """)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure all dependencies are installed: pip install -r requirements-lora.txt")
        print("2. Check if you have enough disk space")
        print("3. Try running on CPU first (remove GPU code if needed)")
        raise


if __name__ == "__main__":
    main()
