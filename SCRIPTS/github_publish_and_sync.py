import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path


def run(cmd: list[str], cwd: Path, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    kwargs = {
        "cwd": str(cwd),
        "text": True,
    }
    if capture:
        kwargs["stdout"] = subprocess.PIPE
        kwargs["stderr"] = subprocess.PIPE
    p = subprocess.run(cmd, **kwargs)
    if check and p.returncode != 0:
        stdout = (p.stdout or "").strip() if capture else ""
        stderr = (p.stderr or "").strip() if capture else ""
        msg = f"Fallo comando: {' '.join(cmd)} (code={p.returncode})"
        if stdout:
            msg += f"\nSTDOUT:\n{stdout}"
        if stderr:
            msg += f"\nSTDERR:\n{stderr}"
        raise RuntimeError(msg)
    return p


def prompt(text: str, default: str | None = None) -> str:
    if not sys.stdin.isatty():
        return default or ""
    suffix = f" [{default}]" if default else ""
    value = input(f"{text}{suffix}: ").strip()
    return value or (default or "")


def slugify_repo_name(name: str) -> str:
    name = name.strip().lower()
    out: list[str] = []
    last_dash = False
    for ch in name:
        ok = ("a" <= ch <= "z") or ("0" <= ch <= "9")
        if ok:
            out.append(ch)
            last_dash = False
        else:
            if not last_dash:
                out.append("-")
                last_dash = True
    slug = "".join(out).strip("-")
    return slug or "repo"


def find_gh_executable() -> str | None:
    gh = shutil.which("gh")
    if gh:
        return gh

    candidates = [
        r"C:\\Program Files\\GitHub CLI\\gh.exe",
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "GitHub CLI", "gh.exe"),
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None


def github_api_request(url: str, token: str, method: str = "GET", data: dict | None = None) -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "github-publish-and-sync",
    }
    payload = None
    if data is not None:
        payload = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=payload, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode("utf-8")
            if not body:
                return {}
            return json.loads(body)
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API error {e.code} en {url}: {raw}") from e


def ensure_git_repo(project_root: Path) -> None:
    if not (project_root / ".git").exists():
        print("[INFO] Inicializando repositorio Git...")
        run(["git", "init"], cwd=project_root)

    # Asegurar rama main
    subprocess.run(
        ["git", "checkout", "-B", "main"],
        cwd=str(project_root),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )


def ensure_commit(project_root: Path, message: str | None) -> None:
    print("[INFO] Agregando cambios...")
    run(["git", "add", "-A"], cwd=project_root)

    diff = run(["git", "diff", "--cached", "--quiet"], cwd=project_root, check=False)
    if diff.returncode == 0:
        print("[INFO] No hay cambios para commitear.")
        return

    if not message:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"chore: sync {ts}"

    print(f"[INFO] Commit: {message}")
    run(["git", "commit", "-m", message], cwd=project_root)


def get_origin_url(project_root: Path) -> str | None:
    p = run(["git", "remote", "get-url", "origin"], cwd=project_root, check=False, capture=True)
    if p.returncode != 0:
        return None
    return (p.stdout or "").strip() or None


def set_origin(project_root: Path, url: str) -> None:
    existing = get_origin_url(project_root)
    if existing:
        run(["git", "remote", "set-url", "origin", url], cwd=project_root)
    else:
        run(["git", "remote", "add", "origin", url], cwd=project_root)


def remote_has_main(project_root: Path) -> bool:
    p = run(["git", "ls-remote", "--heads", "origin", "main"], cwd=project_root, check=False, capture=True)
    return p.returncode == 0 and bool((p.stdout or "").strip())


def sync_with_remote(project_root: Path) -> None:
    print("[INFO] Sincronizando con remoto...")
    if remote_has_main(project_root):
        run(["git", "pull", "origin", "main", "--rebase"], cwd=project_root)
    run(["git", "push", "-u", "origin", "main"], cwd=project_root)


def ensure_github_repo_via_gh(project_root: Path, owner: str, repo: str, visibility: str) -> str:
    gh = find_gh_executable()
    if not gh:
        raise RuntimeError("No se encontro GitHub CLI (gh).")

    # auth status
    auth = subprocess.run([gh, "auth", "status"], cwd=str(project_root))
    if auth.returncode != 0:
        raise RuntimeError(
            "gh no esta autenticado. Ejecuta en una terminal: gh auth login\n"
            "Luego reintenta este script."
        )

    full = f"{owner}/{repo}"
    view = subprocess.run([gh, "repo", "view", full], cwd=str(project_root), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if view.returncode != 0:
        print("[INFO] Repo no existe en GitHub. Creando via gh...")
        # Nota: --source . y --remote origin enlazan y crean el remoto
        create = subprocess.run(
            [gh, "repo", "create", full, f"--{visibility}", "--source", ".", "--remote", "origin"],
            cwd=str(project_root),
        )
        if create.returncode != 0:
            raise RuntimeError("Fallo al crear el repositorio con gh.")
    else:
        print("[INFO] Repo ya existe en GitHub. Configurando remote origin...")
        set_origin(project_root, f"https://github.com/{owner}/{repo}.git")

    return f"https://github.com/{owner}/{repo}"


def ensure_github_repo_via_token(project_root: Path, owner: str, repo: str, private: bool, token: str) -> str:
    # determinar login del token
    me = github_api_request("https://api.github.com/user", token)
    login = me.get("login")
    if not login:
        raise RuntimeError("No se pudo determinar el usuario del token (respuesta inesperada de /user).")

    # ¿Existe repo?
    repo_url = f"https://api.github.com/repos/{owner}/{repo}"
    exists = True
    try:
        github_api_request(repo_url, token)
    except RuntimeError as e:
        if "error 404" in str(e).lower():
            exists = False
        else:
            raise

    if not exists:
        print("[INFO] Repo no existe en GitHub. Creando via API...")
        payload = {"name": repo, "private": private}
        if owner.lower() == str(login).lower():
            github_api_request("https://api.github.com/user/repos", token, method="POST", data=payload)
        else:
            github_api_request(f"https://api.github.com/orgs/{owner}/repos", token, method="POST", data=payload)

    set_origin(project_root, f"https://github.com/{owner}/{repo}.git")
    return f"https://github.com/{owner}/{repo}"


def project_root_from_script() -> Path:
    here = Path(__file__).resolve().parent
    if here.name.lower() == "scripts":
        return here.parent
    return here


def main() -> int:
    parser = argparse.ArgumentParser(description="Publicar/sincronizar un proyecto en GitHub (crear repo + push)")
    parser.add_argument("message", nargs="?", default=None, help="Mensaje de commit")
    parser.add_argument("remote_url", nargs="?", default=None, help="URL HTTPS del repo (opcional)")
    parser.add_argument("--owner", default=os.environ.get("GITHUB_OWNER") or os.environ.get("OWNER"), help="Owner (usuario u org)")
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPO") or os.environ.get("REPO_NAME"), help="Nombre del repo")
    parser.add_argument("--visibility", default=os.environ.get("GITHUB_VISIBILITY") or "private", choices=["private", "public"], help="Visibilidad")
    parser.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"), help="Token de GitHub (alternativa a gh)")

    args = parser.parse_args()

    project_root = project_root_from_script()

    if not shutil.which("git"):
        print("[ERROR] Git no esta instalado o no esta en PATH.")
        return 1

    ensure_git_repo(project_root)

    # Si el usuario pasó una URL como primer argumento (sin mensaje), interpretarlo como remote
    if args.message and args.message.lower().startswith("http") and not args.remote_url:
        args.remote_url = args.message
        args.message = None

    if args.remote_url:
        print("[INFO] Configurando remote origin (URL provista)...")
        set_origin(project_root, args.remote_url)
    else:
        # Si no hay origin, intentamos crearlo
        if not get_origin_url(project_root):
            default_owner = args.owner or "cetrusa"
            default_repo = args.repo or slugify_repo_name(project_root.name)
            owner = args.owner or prompt("Owner (usuario u org)", default_owner)
            repo = args.repo or prompt("Nombre del repo", default_repo)
            visibility = args.visibility or prompt("Visibilidad (private/public)", "private")
            if visibility not in ("private", "public"):
                visibility = "private"
            args.visibility = visibility
            if not owner or not repo:
                print("[ERROR] Falta owner/repo. Pasa URL o define GITHUB_OWNER/GITHUB_REPO.")
                return 1

            if args.token:
                url = ensure_github_repo_via_token(
                    project_root,
                    owner,
                    repo,
                    private=(args.visibility == "private"),
                    token=args.token,
                )
            else:
                url = ensure_github_repo_via_gh(project_root, owner, repo, visibility=args.visibility)

            print(f"[EXITO] Repo listo: {url}")

    ensure_commit(project_root, args.message)

    origin = get_origin_url(project_root)
    if not origin:
        print("[ERROR] No hay remote origin configurado. No se puede hacer push.")
        return 1

    sync_with_remote(project_root)
    print("[EXITO] Proyecto sincronizado.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"[ERROR] {e}")
        raise SystemExit(1)
