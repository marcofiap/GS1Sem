import subprocess


def run_tests():
    print("Executando testes com pytest...")
    try:
        subprocess.run(["pytest", "tests/"], check=True)
    except subprocess.CalledProcessError:
        print("Testes falharam.")


if __name__ == "__main__":
    run_tests()