# models.py
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch
from django.conf import settings
import os
from functools import lru_cache

class ModelManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.device = self._get_device()
        self._initialize_models()
        self._initialized = True

    def _get_device(self):
        if torch.cuda.is_available():
            return "cuda"
        return "cpu"

    def _initialize_models(self):
        try:
            # Initialize small models first for quick intent/move detection
            self.intent_pipeline = pipeline(
                'zero-shot-classification',
                "facebook/bart-large-mnli",
                device=self.device
            )
            self.roberta_qa = pipeline(
                "question-answering",
                "deepset/roberta-base-squad2",
                device=self.device
            )

            # Initialize LLaMA with proper tokenizer and model handling
            self.tokenizer = AutoTokenizer.from_pretrained(
                "meta-llama/Llama-3.2-1B",
                token=settings.HF_TOKEN
            )

            self.llm_model = AutoModelForCausalLM.from_pretrained(
                "meta-llama/Llama-3.2-1B",
                token=settings.HF_TOKEN,
                torch_dtype=torch.float32
            ).to(self.device)

        except Exception as e:
            print(f"Error initializing models: {e}")
            raise

    def quick_response(self, prompt: str) -> str:
        """Single method for generating responses"""
        try:
            # Generate response using LLaMA
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.llm_model.generate(
                    **inputs,
                    max_length=150,  # Keep responses short
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id
                )

            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = response.replace(prompt, "").strip()

            # Fallback for empty or invalid responses
            if not response or response == prompt:
                return self._get_fallback_response()

            return response

        except Exception as e:
            print(f"Error in quick_response: {str(e)}")
            return self._get_fallback_response()

    def _get_fallback_response(self) -> str:
        """Provide safe fallback responses"""
        return "Let me analyze that move..."

    def get_intent(self, message: str, labels: list) -> dict:
        """Quick intent classification"""
        try:
            return self.intent_pipeline(message, labels)
        except Exception:
            return {"labels": labels, "scores": [0.0] * len(labels)}

    def extract_move(self, message: str, context: str) -> str:
        """Extract chess move from text"""
        try:
            result = self.roberta_qa(
                question="What chess move is mentioned?",
                context=context
            )
            return result['answer'].strip()
        except Exception:
            return None

# Global singleton instance
model_manager = ModelManager()