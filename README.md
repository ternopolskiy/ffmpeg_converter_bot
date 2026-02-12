# 🎵 FLAC to MP3 Converter Bot

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Aiogram](https://img.shields.io/badge/Aiogram-3.15-2AABEE?style=for-the-badge&logo=telegram&logoColor=white)](https://aiogram.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Required-007808?style=for-the-badge&logo=ffmpeg&logoColor=white)](https://ffmpeg.org/)

A powerful Telegram bot that converts FLAC audio files to high-quality MP3 (320 kbps) format. Built with modern async Python stack, featuring database logging, concurrent processing, and Docker support.

---

## ✨ Features

- 🎧 **High-Quality Conversion**: FLAC → MP3 at 320 kbps bitrate
- 📦 **Batch Processing**: Send multiple files at once (up to 3 concurrent conversions)
- 🏷️ **Metadata Preservation**: Keeps artist, title, album tags from original files
- 📊 **Statistics Tracking**: PostgreSQL database logs all conversions
- ⚡ **Async Processing**: Non-blocking FFmpeg execution
- 🐳 **Docker Ready**: Complete docker-compose setup included
- 🔒 **Production Ready**: Proper error handling and resource cleanup

---

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────┐
│  Telegram    │────▶│  Aiogram Bot │────▶│  FFmpeg  │
│  User        │◀────│  (Python)    │◀────│  Worker  │
└─────────────┘     └──────┬───────┘     └─────────┘
                           │
                    ┌──────┴───────┐
                    │              │
               ┌────▼────┐  ┌─────▼────┐
               │PostgreSQL│  │  Redis   │
               │ (history) │  │ (cache)  │
               └──────────┘  └──────────┘
```

---

## ⚠️ Limitations

### Telegram Bot API Restrictions

| Limit Type | Standard API | Custom Bot API Server |
|-----------|--------------|----------------------|
| **Download** | 20 MB | 2000 MB |
| **Upload** | 50 MB | 2000 MB |

**Important**: This bot uses the standard Telegram Bot API, which means:
- ✅ Files up to **20 MB** can be downloaded and converted
- ❌ Files larger than 20 MB will be rejected with an error message

**Solution for larger files**: Deploy your own [Telegram Bot API Server](https://github.com/tdlib/telegram-bot-api) to increase limits to 2000 MB.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 16+
- Redis 7+
- FFmpeg (installed and in PATH)

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd flac2mp3_bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your credentials
```

4. **Setup database**
```bash
# Start PostgreSQL and Redis (or use Docker)
docker compose up -d postgres redis

# Run migrations
alembic upgrade head
```

5. **Install FFmpeg**

**Ubuntu/Debian:**
```bash
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
- Download from [gyan.dev/ffmpeg](https://www.gyan.dev/ffmpeg/builds/)
- Add to PATH or set `FFMPEG_PATH` in `.env`

6. **Run the bot**
```bash
python -m bot
```

---

## 🐳 Docker Deployment

### Full Stack (Recommended)

```bash
# Build and start all services
docker compose up --build -d

# View logs
docker compose logs -f bot

# Stop services
docker compose down
```

### Services Included

- **bot**: Python application with FFmpeg
- **postgres**: PostgreSQL 16 database
- **redis**: Redis 7 cache

---

## 📁 Project Structure

```
flac2mp3_bot/
├── bot/
│   ├── __main__.py          # Application entry point
│   ├── config.py            # Settings management
│   ├── loader.py            # Redis initialization
│   ├── handlers/
│   │   ├── start.py         # /start and /stats commands
│   │   └── converter.py     # File processing logic
│   ├── middlewares/
│   │   ├── db_middleware.py # Database session injection
│   │   └── throttling.py    # Rate limiting (optional)
│   ├── services/
│   │   └── audio_converter.py # FFmpeg wrapper
│   ├── db/
│   │   ├── database.py      # SQLAlchemy setup
│   │   └── models.py        # User & ConversionLog models
│   └── utils/
│       └── temp_file.py     # Temporary file helpers
├── migrations/              # Alembic database migrations
├── docker-compose.yml       # Docker orchestration
├── Dockerfile              # Bot container image
├── requirements.txt        # Python dependencies
├── alembic.ini            # Alembic configuration
├── .env.example           # Environment template
└── README.md              # This file
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BOT_TOKEN` | *required* | Telegram Bot API token from [@BotFather](https://t.me/BotFather) |
| `POSTGRES_HOST` | `localhost` | PostgreSQL server address |
| `POSTGRES_PORT` | `5432` | PostgreSQL port |
| `POSTGRES_USER` | `postgres` | Database username |
| `POSTGRES_PASSWORD` | *required* | Database password |
| `POSTGRES_DB` | `flac2mp3` | Database name |
| `REDIS_HOST` | `localhost` | Redis server address |
| `REDIS_PORT` | `6379` | Redis port |
| `REDIS_DB` | `0` | Redis database number |
| `TEMP_DIR` | `/tmp/flac2mp3` | Temporary files directory |
| `MAX_FILE_SIZE_MB` | `50` | Maximum upload size (Telegram limit) |
| `FFMPEG_PATH` | `ffmpeg` | Path to FFmpeg binary |

---

## 🎯 Usage

### Commands

- `/start` - Welcome message and instructions
- `/stats` - View your conversion statistics

### Converting Files

1. Send one or more `.flac` files to the bot
2. Bot will process them concurrently (max 3 at a time)
3. Receive converted MP3 files with preserved metadata

**Supported formats:**
- ✅ FLAC files (sent as document or audio)
- ❌ Other formats will be rejected

---

## 🔧 Development

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

### Running Tests

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests (if available)
pytest
```

---

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    total_conversions INTEGER DEFAULT 0
);
```

### Conversion Logs Table
```sql
CREATE TABLE conversion_logs (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    original_filename VARCHAR(500) NOT NULL,
    original_size_mb FLOAT NOT NULL,
    converted_size_mb FLOAT NOT NULL,
    duration_seconds FLOAT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 🛠️ Tech Stack

- **Framework**: [Aiogram 3.15](https://aiogram.dev/) - Modern Telegram Bot framework
- **Database**: [PostgreSQL 16](https://www.postgresql.org/) - Reliable relational database
- **Cache**: [Redis 7](https://redis.io/) - In-memory data store
- **ORM**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/) - Async database toolkit
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/) - Database migration tool
- **Audio Processing**: [FFmpeg](https://ffmpeg.org/) - Multimedia framework
- **Containerization**: [Docker](https://www.docker.com/) - Application containers

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🙏 Acknowledgments

- [Aiogram](https://aiogram.dev/) - Excellent Telegram Bot framework
- [FFmpeg](https://ffmpeg.org/) - Powerful multimedia processing
- [Telegram Bot API](https://core.telegram.org/bots/api) - Bot platform

---

## 📧 Support

If you encounter any issues or have questions:
- Open an [Issue](../../issues)
- Check existing [Discussions](../../discussions)

---

**Made with ❤️ and Python**
