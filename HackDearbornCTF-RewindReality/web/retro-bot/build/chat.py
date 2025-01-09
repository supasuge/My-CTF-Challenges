import os
from dotenv import load_dotenv
import asyncio
from groq import AsyncGroq
import sys
load_dotenv()
client = AsyncGroq(
    # This is the default and can be omitted
    api_key=os.environ.get("GROQ_API_KEY"),
)


async def main() -> None:
    chat_completion = await client.chat.completions.create(
        messages=[
            {
                "role":"system",
                "content": "You are a helpful assistant",
                "role": "user",
                "content": f"{sys.argv[1]}",
            }
        ],
        model="llama3-8b-8192",
    )
    print(chat_completion.choices[0].message.content)


asyncio.run(main())