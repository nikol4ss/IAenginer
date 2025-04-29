import os
from openai import OpenAI
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

openai_key = os.getenv('OPENAI_API_KEY')

if not openai_key:
    logger.error("Error: OPENAI_API_KEY is not set.")
    sys.exit(1)

client = OpenAI(api_key=openai_key)
logger.info("[OPENAI] connected")

history = set()

def chatgpt_test():
    prompt = "I want to test if it works, tell me any fruit, without repeating"
    try:
        logger.info("[OPENAI] Sending request for a fruit.")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=1,
            max_tokens=10
        )
        logger.info("[OPENAI] Response received.")
    except Exception as e:
        logger.error(f"[OPENAI] Error: {e}")
        return None

    fruit = response.choices[0].message.content.strip()
    while fruit in history:
        try:
            logger.info("[OPENAI] Fruit already chosen, requesting new one.")
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=1,
                max_tokens=10
            )
            logger.info("[OPENAI] Response received.")
        except Exception as e:
            logger.error(f"[OPENAI] Error: {e}")
            return None

        fruit = response.choices[0].message.content.strip()

    history.add(fruit)
    return fruit

if __name__ == "__main__":
    result = chatgpt_test()
    if result:
        logger.info(f"[OPENAI] Response: {result}")
