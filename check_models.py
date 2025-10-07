#!/usr/bin/env python3
"""
Script to check available OpenAI models in your account
"""
import openai
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        return
    
    try:
        client = openai.OpenAI(api_key=api_key)
        models = client.models.list()
        
        # Filtrar modelos relevantes
        relevant_models = []
        computer_use_models = []
        
        for model in models.data:
            model_id = model.id
            if any(x in model_id.lower() for x in ['gpt-4', 'gpt-3.5']):
                relevant_models.append(model_id)
                
                # Modelos que soportan computer use
                if model_id in ['gpt-4o', 'gpt-4o-2024-08-06', 'gpt-4o-2024-11-20']:
                    computer_use_models.append(model_id)
        
        print(f"📋 Modelos disponibles ({len(relevant_models)} encontrados):")
        for model in sorted(relevant_models):
            if model in computer_use_models:
                print(f"  ✅ {model} (Soporta computer_use_preview)")
            else:
                print(f"  ❌ {model} (NO soporta computer_use_preview)")
        
        print(f"\n🖥️  Modelos compatibles con computer_use_preview:")
        if computer_use_models:
            for model in sorted(computer_use_models):
                print(f"  ✅ {model}")
            print(f"\n💡 Recomendación: Usa '{computer_use_models[0]}' en tu workflow")
        else:
            print("  ❌ Ningún modelo compatible encontrado")
            print("  💳 Necesitas una cuenta de pago de OpenAI para acceso a gpt-4o")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if "authentication" in str(e).lower():
            print("🔑 Verifica tu API key de OpenAI")

if __name__ == "__main__":
    main()