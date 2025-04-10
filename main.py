from settings import settings
from src.interface import demo 

def main():
    demo.launch(share=settings.ENVIRONMENT == "prod")


if __name__ == "__main__":
    main()















