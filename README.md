# Nikochan Rift (Liga) — Django

## Requisitos
- Python 3.11+ recomendado

## Arranque rápido
```bash
python -m venv .venv
# Windows: .\.venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

pip install -r requirements.txt

# Opcional: variables de entorno
# copia .env.example a .env y exporta/usa un gestor de envs

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Twitch embed
- `TWITCH_CHANNEL` debe ser el **slug** del canal (p.ej. `j4npu`), no la URL.
- `TWITCH_PARENT` debe coincidir con el dominio desde el que se carga el iframe (p.ej. `localhost` en local).

## Checklist beta (mínimo)
- [ ] `DJANGO_SECRET_KEY` en entorno (no hardcode)
- [ ] `DJANGO_DEBUG=0` en producción
- [ ] `DJANGO_ALLOWED_HOSTS` configurado
- [ ] `collectstatic` si despliegas
