import subprocess
import sys
import os
import time
import shutil

def get_venv_paths(backend_dir):
    """Retorna os caminhos para o executável do python e do pip dentro do venv"""
    venv_dir = os.path.join(backend_dir, "venv")
    if os.name == "nt": # Windows
        python_exe = os.path.join(venv_dir, "Scripts", "python.exe")
        pip_exe = os.path.join(venv_dir, "Scripts", "pip.exe")
    else: # Linux/Mac
        python_exe = os.path.join(venv_dir, "bin", "python")
        pip_exe = os.path.join(venv_dir, "bin", "pip")
    return venv_dir, python_exe, pip_exe

def install_backend_deps(backend_dir):
    print("[SISTEMA] Verificando dependencias do Back-end...", flush=True)
    venv_dir, python_exe, pip_exe = get_venv_paths(backend_dir)
    
    # 1. Cria o ambiente virtual se não existir (Evita o erro PEP-668 / externally-managed)
    if not os.path.exists(venv_dir) or not os.path.exists(pip_exe):
        print("          Criando ambiente virtual (venv)...", flush=True)
        try:
            subprocess.run([sys.executable, "-m", "venv", "venv"], cwd=backend_dir, check=True)
        except subprocess.CalledProcessError:
            print("          [ERRO] Falha ao criar o ambiente virtual.", flush=True)
            print("          No Linux/Ubuntu, você geralmente precisa instalar o pacote venv.", flush=True)
            print("          Tente rodar: sudo apt install python3-venv", flush=True)
            sys.exit(1)
    
    # 2. Instala as dependências dentro do venv
    requirements_path = os.path.join(backend_dir, "requirements.txt")
    installed_marker = os.path.join(venv_dir, ".installed_deps")
    
    if os.path.exists(requirements_path):
        if not os.path.exists(installed_marker) or os.path.getmtime(requirements_path) > os.path.getmtime(installed_marker):
            print("          Instalando pacotes Python no venv...", flush=True)
            try:
                subprocess.run([python_exe, "-m", "pip", "install", "-r", "requirements.txt"], cwd=backend_dir, check=True)
                # Cria a marcação de que já foi instalado para pular na próxima vez
                with open(installed_marker, "w") as f:
                    f.write("Instalado")
            except subprocess.CalledProcessError:
                print("          [ERRO] Ocorreu um erro ao instalar as dependências do Python.", flush=True)
                print("          Isso normalmente acontece em Linux/Raspberry Pi quando faltam bibliotecas C ou venv está corrompido.", flush=True)
                print("          Tente rodar: sudo apt install python3-venv python3-dev build-essential", flush=True)
                print("          E apague a pasta 'backend/venv' para tentar de novo.", flush=True)
                sys.exit(1)
        else:
            print("          Pacotes do Python ja estao instalados (venv pronto).", flush=True)
    else:
        print("          Nenhum arquivo requirements.txt encontrado.", flush=True)

def check_npm_installed():
    """Verifica se o npm está instalado no sistema"""
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
    return shutil.which(npm_cmd) is not None or shutil.which("npm") is not None

def install_frontend_deps(frontend_dir):
    print("[SISTEMA] Verificando dependencias do Front-end...", flush=True)
    
    if not check_npm_installed():
        print("          [AVISO] O comando 'npm' não foi encontrado no seu sistema.", flush=True)
        print("          Tentando instalar o Node.js e npm via apt (requer senha de sudo se solicitado)...", flush=True)
        try:
            subprocess.run(["sudo", "apt", "update"], check=True)
            subprocess.run(["sudo", "apt", "install", "-y", "nodejs", "npm"], check=True)
            print("          [SUCESSO] Node.js e npm instalados!", flush=True)
        except subprocess.CalledProcessError:
            print("          [ERRO] Falha ao tentar instalar o Node.js automaticamente.", flush=True)
            print("          Por favor, instale manualmente rodando: sudo apt install nodejs npm", flush=True)
            sys.exit(1)
        

    node_modules_path = os.path.join(frontend_dir, "node_modules")
    if not os.path.exists(node_modules_path):
        print("          Pasta node_modules nao encontrada. Instalando pacotes npm...", flush=True)
        # shell=True é recomendado no Windows para comandos npm
        subprocess.run(["npm", "install"], cwd=frontend_dir, shell=True)
    else:
        print("          Pasta node_modules ja existe.", flush=True)
        
def build_frontend(frontend_dir):
    print("[SISTEMA] Construindo Front-end (React/Vite) para produção...", flush=True)
    dist_path = os.path.join(frontend_dir, "dist")
    if not os.path.exists(dist_path):
        print("          Pasta dist não encontrada. Rodando 'npm run build'...", flush=True)
        try:
            subprocess.run(["npm", "run", "build"], cwd=frontend_dir, shell=True, check=True)
            print("          [SUCESSO] Build finalizado!", flush=True)
        except subprocess.CalledProcessError:
            print("          [ERRO] A compilação (build) do front-end falhou.", flush=True)
            sys.exit(1)
    else:
        print("          Build ja existe. Ignorando 'npm run build' (apague a pasta dist se quiser forçar novo build).", flush=True)

def run_backend(backend_dir, root_dir):
    print("[SISTEMA] Iniciando Servidor Back-end (Python)...", flush=True)
    _, python_exe, _ = get_venv_paths(backend_dir)
    
    # Adicionamos a raiz ao PYTHONPATH para caso o código do backend faça 'import backend.algo'
    env = os.environ.copy()
    env["PYTHONPATH"] = root_dir + os.pathsep + env.get("PYTHONPATH", "")
    
    return subprocess.Popen(
        [python_exe, "app.py"],
        cwd=backend_dir,
        env=env
    )

if __name__ == "__main__":
    print("="*60)
    print("Iniciador Automático HydraSensor (Front e Back)")
    print("="*60)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(base_dir, "backend")
    frontend_dir = os.path.join(base_dir, "frontend")
    
    # Etapa 1: Instalação de dependências
    print("\n--- ETAPA 1: Configuração ---")
    install_backend_deps(backend_dir)
    install_frontend_deps(frontend_dir)
    build_frontend(frontend_dir)
    
    # Etapa 2: Inicialização dos serviços
    print("\n--- ETAPA 2: Inicialização ---")
    backend_proc = None
    
    try:
        backend_proc = run_backend(backend_dir, base_dir)
        
        print(f"\n[SISTEMA] Tudo pronto! Acesse a aplicação na porta 5000: http://localhost:5000", flush=True)
        print("[SISTEMA] O Servidor Python agora hospeda o React automaticamente. Pressione Ctrl+C para encerrar.", flush=True)
        
        backend_proc.wait()
        
    except KeyboardInterrupt:
        print("\n[SISTEMA] Encerrando servidor...", flush=True)
        if backend_proc:
            backend_proc.terminate()
            
        print("[SISTEMA] Encerrado com sucesso.")
        sys.exit(0)
