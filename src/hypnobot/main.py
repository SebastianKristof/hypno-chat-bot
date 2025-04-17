from src.hypnobot.hypnobot import HypnoBot

if __name__ == "__main__":
    bot = HypnoBot()
    while True:
        query = input("Ask HypnoBot something: ")
        response = bot.process(query)
        print("\n=== HypnoBot Response ===")
        print(response)
