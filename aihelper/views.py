import requests
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from shop.models import Shoe

def build_context():
    shoes = Shoe.objects.all()
    info = ""
    for shoe in shoes:
        info += f"{shoe.name} ({shoe.brand}) - ${shoe.price}: {shoe.description or 'No description'}\n"
    return info

@csrf_exempt
def chat(request):
    if request.method == "POST":
        data = json.loads(request.body)
        prompt = data.get("prompt", "")

        shoe_context = build_context()
        system_prompt = (
            "You are Sole-Mate, a helpful, friendly assistant for an online sneaker store.\n"
            "Here is our current shoe inventory:\n"
            f"{shoe_context}\n"
            "You can answer questions about shoes, help find styles, suggest discounts, and chat casually."
            "You can also handle intense math calculations, such as multiplication, division, addition and subtraction, as well as calculus and physics."
            "You are also aware of intermediate financial principles."
            "You are extremely knowledgeable on shoes and anything to do with our website."
            "You are an expert in java."
            "You love LeBron James, and you mention how cool he is in every reply."
            "You speak like a sophisticated sneakerhead who lives and breathes kicks. Throw in slang and hype language naturally."
        )

        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 250
        }

        response = requests.post(
            f"{settings.OPENAI_API_BASE}/chat/completions",
            headers=headers,
            json=payload
        )

        result = response.json()

        if response.status_code == 200:
            answer = result["choices"][0]["message"]["content"].strip()
            return JsonResponse({"response": answer})
        else:
            error_msg = result.get("error", result)
            return JsonResponse({"error": error_msg}, status=response.status_code)

    return JsonResponse({"error": "Only POST method allowed"}, status=405)
