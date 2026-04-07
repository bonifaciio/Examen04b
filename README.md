# Descargador de Instagram 📹

Aplicación web dockerizada para descargar videos y reels de Instagram. Interfaz web intuitiva con historial de descargas y soporte para contenido privado mediante cookies.

## Características

✅ Descarga reels y videos públicos de Instagram  
✅ Interfaz web en `localhost:5002`  
✅ Soporte opcional para contenido privado (con cookies)  
✅ Historial de descargas  
✅ Tres variantes de Dockerfile (standard, optimizado, multistage)  
✅ Gunicorn como servidor WSGI  
✅ Diseño responsive y moderno  

## Requisitos

- Docker >= 20.10
- Docker Compose (opcional)
- Navegador web

## Instalación y Uso

### 1. Construir imagen Docker

```bash
cd /home/boni/Examen04b
sudo docker build -t instagram-web .
```

### 2. Ejecutar contenedor (sin cookies - contenido público)

```bash
sudo docker run -d --rm \
  -p 5002:5002 \
  --name instagram-web \
  -v "$(pwd)/downloads:/app/downloads" \
  instagram-web
```

### 3. Ejecutar contenedor (con cookies - contenido privado)

```bash
sudo docker run -d --rm \
  -p 5002:5002 \
  --name instagram-web \
  -e COOKIES_FILE=/app/cookies.txt \
  -v "$(pwd)/downloads:/app/downloads" \
  -v "$(pwd)/cookies.txt:/app/cookies.txt:ro" \
  instagram-web
```

### 4. Abrir en navegador

```
http://localhost:5002
```

### 5. Detener contenedor

```bash
sudo docker stop instagram-web
```

## Estructura del Proyecto

```
Examen04b/
├── app/
│   ├── app.py                    # Aplicación Flask principal
│   ├── requirements.txt          # Dependencias Python
│   ├── templates/
│   │   └── index.html           # Template principal
│   └── static/
│       └── styles.css           # Estilos CSS
├── downloads/                   # Carpeta de descargas
├── Dockerfile                   # Imagen estándar (Python 3.10-slim + ffmpeg)
├── Dockerfile.optimizado        # Imagen optimizada (más pequeña, caché mejorado)
├── Dockerfile.multistage        # Build multistage (builder + runtime) - Recomendado
├── .gitignore                   # Ignorar archivos grandes y generados
└── README.md                    # Este archivo
```

## Variantes de Dockerfile

### `Dockerfile`
**Uso**: Producción general  
**Tamaño**: ~800MB  
**Ventajas**: Simple, flexible

```bash
sudo docker build -t instagram-web -f Dockerfile .
```

### `Dockerfile.optimizado`
**Uso**: Cuando tamaño es crítico  
**Tamaño**: ~750MB (base slim)  
**Ventajas**: Imagen base más pequeña

```bash
sudo docker build -t instagram-web -f Dockerfile.optimizado .
```

### `Dockerfile.multistage` (Recomendado)
**Uso**: Producción optimizada  
**Tamaño**: ~750MB  
**Ventajas**: Solo dependencias necesarias en imagen final

```bash
sudo docker build -t instagram-web -f Dockerfile.multistage .
```

## Dependencias Python

```
yt-dlp          # Descargador universal de videos
Flask           # Framework web
gunicorn        # Servidor WSGI
```

## Usar Cookies para Contenido Privado

### Generar cookies en formato Netscape

1. Instala extensión de navegador: **Get cookies.txt** (Chrome/Firefox)
2. Ve a `instagram.com`
3. Inicia sesión
4. Haz clic en extensión → exporta cookies
5. Guarda como `cookies.txt` en `/home/boni/Examen04b/cookies.txt`
6. Ejecuta contenedor con flag `-v`

**Formato esperado (Netscape)**:
```
# Netscape HTTP Cookie File
.instagram.com	TRUE	/	TRUE	1704067200	sessionid	abc123...
.instagram.com	TRUE	/	TRUE	1704067200	ds_user_id	12345...
```

## Variables de Entorno

| Variable | Default | Descripción |
|----------|---------|-------------|
| `COOKIES_FILE` | `/app/cookies.txt` | Ruta a archivo cookies Netscape |
| `DOWNLOADS_DIR` | `downloads` | Directorio de descarga |
| `HISTORIAL_FILE` | `historial.txt` | Archivo de historial |
| `PORT` | `5002` | Puerto HTTP |

## Ver Logs

```bash
sudo docker logs -f instagram-web
```

## Limpiar Contenedor y Imagen

```bash
# Detener
sudo docker stop instagram-web

# Eliminar imagen (si no la necesitas más)
sudo docker rmi instagram-web
```

## Solución de Problemas

### Error: "URL no reconocida. Usa un enlace de Instagram."
- Verifica que el link sea válido
- Formato: `https://www.instagram.com/reel/...`

### Error: "does not look like a Netscape format cookies file"
- El archivo `cookies.txt` tiene formato incorrecto
- Regenera con la extensión "Get cookies.txt"
- O simplemente no montes cookies y descarga contenido público

### Error: "Container name already in use"
- Detén el contenedor anterior: `sudo docker stop instagram-web`

### Descarga lenta
- Puede ser un problema de conexión o restricciones de Instagram
- Espera unos minutos e intenta de nuevo

## API Rutas

### `GET /`
Pagina de inicio con formulario y historial

### `POST /`
Descarga video. Body: `url=<instagram_url>`

### `GET /downloads/<filename>`
Descarga archivo completado

## Ejemplo de uso vía curl

```bash
curl -X POST http://localhost:5002 \
  -d "url=https://www.instagram.com/reel/DVgMkGyDTfF/"
```

## Notas Legales

- Respeta los términos de servicio de Instagram
- Solo descarga contenido para el cual tengas permiso
- No reventes contenido descargado

## Licencia

MIT

## Autor

Bonifacio Zevillano  
[GitHub: bonifaciio](https://github.com/bonifaciio)

---

¿Preguntas o problemas? Revisa los logs del contenedor o abre un issue en GitHub.
