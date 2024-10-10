# tutor/llm_integration.py

from transformers import AutoTokenizer, AutoModelForCausalLM

class ChessLLM:
    def __init__(self, model_name="gpt2"):  # You might want to use a more suitable model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)

    def generate_response(self, prompt, max_length=1024):
        inputs = self.tokenizer.encode(prompt, return_tensors="pt")
        outputs = self.model.generate(inputs, max_length=max_length, num_return_sequences=1)
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response

chess_llm = ChessLLM()  # Initialize once and reuse

def get_llm_response(prompt):
    return chess_llm.generate_response(prompt)