# Stage 1: Build Tailwind CSS
FROM node:22-alpine AS tailwind_builder

# Forcing a rebuild to ensure all latest code changes are included.
WORKDIR /app

# First, copy only the files needed for npm install to leverage Docker cache
COPY package.json package-lock.json* ./
RUN npm install

# Copy the rest of your front-end source files
COPY tailwind.config.js ./
COPY edcat_root/static/css/input.css ./edcat_root/static/css/input.css
COPY edcat_root/pages/templates/ ./edcat_root/pages/templates/

# Build Tailwind CSS
RUN npx tailwindcss \
  -i ./edcat_root/static/css/input.css \
  -o ./edcat_root/static/css/style.css \
  --minify

# Stage 2: Build the final Python application
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install uv, a fast Python package installer
RUN pip install uv

# Copy only the requirements file to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN uv pip install --no-cache-dir -r requirements.txt --system

# Copy the application code
COPY edcat_root/ ./edcat_root/

# Copy the compiled CSS from the builder stage
COPY --from=tailwind_builder /app/edcat_root/static/css/style.css ./edcat_root/static/css/style.css

EXPOSE 8080

# Run the app using gunicorn - CORRECTED COMMAND
CMD ["gunicorn", "--bind", ":8080", "--workers", "1", "--threads", "8", "edcat_root.main:app"]
