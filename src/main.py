from interface import demo
from settings import settings 

def main():
    demo.launch(share = settings.ENVIRONMENT=="prod")


if __name__ == "__main__":
    main()















