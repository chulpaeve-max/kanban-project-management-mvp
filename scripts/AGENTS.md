# Scripts - Start/Stop Scripts

## Overview

Platform-specific scripts to start and stop the Kanban Studio Docker container.

## Scripts

### Windows
- `start-windows.bat` - Checks Docker is running, then runs docker-compose up --build
- `stop-windows.bat` - Runs docker-compose down

### Mac
- `start-mac.sh` - Checks Docker is running, then runs docker-compose up --build
- `stop-mac.sh` - Runs docker-compose down

### Linux
- `start-linux.sh` - Checks Docker is running, then runs docker-compose up --build
- `stop-linux.sh` - Runs docker-compose down

## Usage

Windows:
```
scripts\start-windows.bat
scripts\stop-windows.bat
```

Mac/Linux:
```
./scripts/start-mac.sh
./scripts/stop-mac.sh
```

or

```
./scripts/start-linux.sh
./scripts/stop-linux.sh
```

## Notes

- Shell scripts (.sh) should be executable (chmod +x on Mac/Linux)
- All scripts check if Docker is running before attempting to start
- Uses docker-compose for container orchestration