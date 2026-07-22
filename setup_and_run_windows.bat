services:
  edgeboard:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - edgeboard_data:/app/data
    restart: unless-stopped

volumes:
  edgeboard_data:
