# Use Node.js as the base image
FROM node:18-alpine AS frontend-builder

# Set working directory
WORKDIR /app/frontend

# Copy frontend files
COPY frontend/package*.json ./
RUN npm install

COPY frontend/public ./public

# Use Python for the backend
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy frontend build from the previous stage
COPY --from=frontend-builder /app/frontend ./frontend

# Create directories for logs
RUN mkdir -p logs/parsed_prompts logs/generated_prompts

# Expose ports
EXPOSE 8000 3000

# Start services
CMD ["sh", "-c", "cd frontend && npm start & cd backend && python main.py"]
