import os

try:
    # Para streamlit >= 1.12
    from streamlit.web import bootstrap
except ImportError:
    # Para versões mais antigas
    from streamlit import bootstrap


def main():
    # diretório atual
    this_dir = os.path.dirname(os.path.abspath(__file__))
    # seu arquivo principal do streamlit
    target_script = os.path.join(this_dir, "mainAPP.py")

    # opções equivalentes a: --server.port=8501 --server.address=0.0.0.0
    flag_options = {
        "server.port": "8501",
     #   "server.address": "0.0.0.0",
    }

    # carrega as configs
    bootstrap.load_config_options(flag_options=flag_options)

    # executa o app
    # Parâmetros: (caminho_script, is_hello, args, flag_options)
    bootstrap.run(target_script, False, [], flag_options)


if __name__ == "__main__":
    main()
