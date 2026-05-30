"""
Llama 3 8B QLoRA Fine-tuning on Modal A100
-------------------------------------------
This script runs on IBM-equivalent GPU infrastructure.
Trains Llama 3 on our 500 RAFT IBM migration examples.
"""

import modal
import os
from pathlib import Path

# --- Define the cloud environment ---
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install([
        "torch==2.4.1",
        "transformers==4.45.2",
        "peft==0.13.2",
        "trl==0.11.4",
        "bitsandbytes==0.44.1",
        "accelerate==1.0.1",
        "datasets==3.0.1",
        "huggingface_hub==0.25.2",
        "scipy==1.14.1",
        "rich",          # added — required by trl
    ])
)

app = modal.App("llama3-ibm-migration-finetuning", image=image)

volume = modal.Volume.from_name(
    "llama3-ibm-weights",
    create_if_missing=True
)

@app.function(
    gpu="A100",
    timeout=60 * 60 * 4,
    volumes={"/weights": volume},
    secrets=[modal.Secret.from_name("huggingface-secret")],
    memory=65536,
)
def train():
    import torch
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        BitsAndBytesConfig,
        TrainingArguments,
    )
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from trl import SFTTrainer
    from datasets import Dataset
    import json
    import os

    print("=" * 50)
    print("IBM Migration Advisor — Llama 3 Fine-tuning")
    print("=" * 50)
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    print()

    # --- Step 1: Load RAFT dataset ---
    print("Loading RAFT dataset...")
    examples = []
    with open("/weights/raft_dataset.jsonl") as f:
        for line in f:
            examples.append(json.loads(line))
    print(f"  ✓ Loaded {len(examples)} training examples")

    # --- Step 2: Format for SFTTrainer ---
    def format_prompt(example):
        messages = example["messages"]
        return {
            "text": f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
{messages[0]['content']}<|eot_id|><|start_header_id|>user<|end_header_id|>
{messages[1]['content']}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
{messages[2]['content']}<|eot_id|>"""
        }

    formatted = [format_prompt(ex) for ex in examples]
    dataset = Dataset.from_list(formatted)
    print(f"  ✓ Dataset formatted for Llama 3 chat template")

    # --- Step 3: Load Llama 3 with 4-bit quantization ---
    print("\nLoading Llama 3 8B with QLoRA config...")
    model_id = "meta-llama/Meta-Llama-3-8B-Instruct"
    hf_token = os.environ["HF_TOKEN"]

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16
    )

    tokenizer = AutoTokenizer.from_pretrained(model_id, token=hf_token)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        quantization_config=bnb_config,
        device_map="auto",
        token=hf_token
    )
    print(f"  ✓ Llama 3 8B loaded")

    # --- Step 4: Apply LoRA adapters ---
    model = prepare_model_for_kbit_training(model)

    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )

    model = get_peft_model(model, lora_config)
    trainable, total = model.get_nb_trainable_parameters()
    print(f"  ✓ LoRA applied: {trainable:,} trainable params")
    print(f"  ✓ {100 * trainable / total:.3f}% of weights being trained")

    # --- Step 5: Training configuration ---
    training_args = TrainingArguments(
        output_dir="/weights/checkpoints",
        num_train_epochs=3,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        bf16=True,
        logging_steps=10,
        save_strategy="epoch",
        warmup_ratio=0.03,
        lr_scheduler_type="cosine",
        report_to="none",
    )

    # --- Step 6: Run training ---
    print("\nStarting fine-tuning...")
    print(f"  Epochs: {training_args.num_train_epochs}")
    print(f"  Batch size: {training_args.per_device_train_batch_size}")
    print(f"  Learning rate: {training_args.learning_rate}")
    print()

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        dataset_text_field="text",
        max_seq_length=2048,
        packing=False,
    )

    trainer.train()
    print("\n✓ Training complete")

    # --- Step 7: Save and push to HuggingFace Hub ---
    print("\nSaving model...")
    model.save_pretrained("/weights/llama3-ibm-migration-final")
    tokenizer.save_pretrained("/weights/llama3-ibm-migration-final")

    hf_username = os.environ.get("HF_USERNAME", "kjoshi08")
    repo_id = f"{hf_username}/llama3-ibm-migration-raft"

    print(f"Pushing to HuggingFace Hub: {repo_id}")
    model.push_to_hub(repo_id, token=hf_token)
    tokenizer.push_to_hub(repo_id, token=hf_token)

    print(f"\n{'=' * 50}")
    print(f"Fine-tuning complete!")
    print(f"Model published: huggingface.co/{repo_id}")
    print(f"{'=' * 50}")

    return {
        "status": "complete",
        "model": repo_id,
        "examples_trained": len(examples)
    }


@app.local_entrypoint()
def main():
    print("Submitting fine-tuning job to Modal A100...")
    print("This will take 2-3 hours on an A100 GPU")
    print()
    result = train.remote()
    print(f"\nResult: {result}")
