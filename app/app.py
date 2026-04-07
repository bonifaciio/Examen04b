import datetime
import os
from pathlib import Path

import yt_dlp
from flask import Flask, render_template, request, send_from_directory


app = Flask(__name__)

PLATAFORMA = "Instagram"

COOKIES_FILE = Path(os.getenv("COOKIES_FILE", "/app/cookies.txt")).expanduser()
DOWNLOADS_DIR = Path(os.getenv("DOWNLOADS_DIR", "downloads"))
HISTORIAL_FILE = Path(os.getenv("HISTORIAL_FILE", "historial.txt"))

DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)


def es_url_instagram(url: str) -> bool:
    url = url.lower()
    return "instagram.com" in url


def guardar_historial(url: str, archivo: str) -> dict:
    registro = {
        "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "plataforma": PLATAFORMA,
        "url": url,
        "archivo": archivo,
    }
    with open(HISTORIAL_FILE, "a", encoding="utf-8") as f:
        f.write(
            f"{registro['fecha']}|{registro['plataforma']}|{registro['url']}|{registro['archivo']}\n"
        )
    return registro


def cargar_historial() -> list[dict]:
    if not HISTORIAL_FILE.exists():
        return []

    items: list[dict] = []
    with open(HISTORIAL_FILE, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("|", 3)
            if len(parts) == 4:
                items.append(
                    {
                        "fecha": parts[0],
                        "plataforma": parts[1],
                        "url": parts[2],
                        "archivo": parts[3],
                    }
                )
    return list(reversed(items))


def descargar_video(url: str) -> dict:
    if not es_url_instagram(url):
        raise ValueError("URL no reconocida. Usa un enlace de Instagram.")

    opciones = {
        "outtmpl": str(DOWNLOADS_DIR / "%(title).150s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
    }

    aviso_cookies = None
    if COOKIES_FILE.is_file():
        opciones["cookiefile"] = str(COOKIES_FILE)
    elif COOKIES_FILE.exists():
        aviso_cookies = (
            f"{COOKIES_FILE} existe pero es directorio. Debe ser un archivo cookies.txt valido."
        )
    else:
        aviso_cookies = (
            "No se encontro cookies.txt. Para contenido privado, monta /app/cookies.txt."
        )

    try:
        with yt_dlp.YoutubeDL(opciones) as ydl:
            info = ydl.extract_info(url, download=True)
            final_path = ydl.prepare_filename(info)

            req = info.get("requested_downloads") or []
            if req and req[0].get("filepath"):
                final_path = req[0]["filepath"]
    except Exception as exc:
        # Si cookies.txt existe pero no está en formato Netscape, reintenta sin cookies.
        if "Netscape format cookies file" in str(exc) and "cookiefile" in opciones:
            aviso_cookies = (
                "cookies.txt no tiene formato Netscape; se intento descargar sin cookies."
            )
            opciones.pop("cookiefile", None)

            with yt_dlp.YoutubeDL(opciones) as ydl:
                info = ydl.extract_info(url, download=True)
                final_path = ydl.prepare_filename(info)

                req = info.get("requested_downloads") or []
                if req and req[0].get("filepath"):
                    final_path = req[0]["filepath"]
        else:
            raise

    archivo = Path(final_path).name
    registro = guardar_historial(url, archivo)
    if aviso_cookies:
        registro["aviso"] = aviso_cookies
    return registro


@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None
    error = None

    if request.method == "POST":
        url = (request.form.get("url") or "").strip()
        if not url:
            error = "Ingresa una URL para descargar."
        else:
            try:
                resultado = descargar_video(url)
            except Exception as exc:
                error = f"No se pudo descargar el video: {exc}"

    return render_template(
        "index.html",
        resultado=resultado,
        error=error,
        historial=cargar_historial(),
    )


@app.route("/downloads/<path:filename>")
def download_file(filename: str):
    return send_from_directory(DOWNLOADS_DIR, filename, as_attachment=True)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5002"))
    app.run(host="0.0.0.0", port=port, debug=False)